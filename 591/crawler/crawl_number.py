import requests
from bs4 import BeautifulSoup
from loguru import logger
from pymongo import MongoClient
from PIL import Image
import pytesseract
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import cv2
import re

detailed_url = 'https://rent.591.com.tw/rent-detail-{}.html'

client = MongoClient()
db = client['rentdb']
house_col = db['houses']

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-notifications')
chrome = webdriver.Chrome('./chromedriver', chrome_options=options)

try_count = 0
all_houses = house_col.find()
for house in all_houses:
    try:
        logger.info(detailed_url.format(house['_id']))
        response = requests.get(detailed_url.format(house['_id']))
        soup = BeautifulSoup(response.text, 'html.parser')
        img_span = soup.find('span', {'class': 'num'})
        if img_span == None:
            logger.warning('The id is not existed now.')
            continue
        phone_img = img_span.find('img', src=True)
        if phone_img == None:
            phone_number = img_span.get_text().strip()
        else:
            phone_img = phone_img['src']
            logger.info('https:' + phone_img)
            chrome.get('https:' + phone_img)
            chrome.save_screenshot('screenshot.png')
            img = cv2.imread('screenshot.png')
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnt = contours[0]
            x, y, w, h = cv2.boundingRect(cnt)
            crop = img[y:y+h, x:x+w]
            cv2.imwrite('screenshot.png', crop)

            img = Image.open('screenshot.png')
            text = pytesseract.image_to_string(img, lang='eng', config='--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789')
            if text != None:
                phone_number = re.findall('\d+', text)
                if len(phone_number) > 0:
                    phone_number = phone_number[0]
                else:
                    phone_number = None
        
        if phone_number and len(phone_number) <= 6:
            phone_number = None
        logger.info(phone_number)
        house_col.update_one({'_id': house['id']}, {'$set': {'phone_number': phone_number}})
    except Exception as e:
        logger.error('get phone number failed: ' + str(e))
        if try_count > 3:
            break
        try_count = try_count + 1

chrome.close()