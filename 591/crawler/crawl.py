import requests
import json
from bs4 import BeautifulSoup
from loguru import logger
from pymongo import MongoClient
import argparse

parser = argparse.ArgumentParser(description='Prepare screw train/val data.')
parser.add_argument('--region', type=str, help='1: 台北市, 3:新北市', required=True)
args = parser.parse_args()

def get_csrf_and_cookies(region):
    main_response = requests.get('https://rent.591.com.tw/')
    soup = BeautifulSoup(main_response.text, 'html.parser')
    csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']
    main_response.cookies.set('urlJumpIp', str(region))
    cookies = main_response.cookies
    return csrf_token, cookies

def get_data(first_row, sex, csrf_token, cookies):
    headers = {'X-CSRF-TOKEN': csrf_token}
    list_response = requests.get('https://rent.591.com.tw/home/search/rsList?kind=0&order=posttime&orderType=asc&firstRow={}&sex={}'.format(first_row, sex), cookies=cookies, headers=headers)
    if list_response.status_code != 200:
        return None
    data = json.loads(list_response.text)
    return data['data']['data']

client = MongoClient()
db = client['rentdb']
house_col = db['houses']
csrf_token, cookies = get_csrf_and_cookies(region=args.region)
try_count = 0
first_row = 0
for sex in ['1', '2', '3']: # boy, girl, both
    while True:
        try:
            data = get_data(first_row, sex, csrf_token, cookies)
            if data == None:
                csrf_token, cookies = get_csrf_and_cookies(region='3')
            elif len(data) <= 0:
                break
            else:
                for row in data:
                    row['_id'] = row['id']
                    row['sex'] = sex
                    row['post_owner'] = row['nick_name'].split(' ')[0]
                    existed = house_col.count({'_id': row['_id']})
                    if existed >= 1:
                        house_col.replace_one({'_id': row['_id']}, row)
                    else:
                        house_col.insert_one(row)
                first_row = first_row + 30
                logger.info('page:' + str(int(first_row/30)))
        except Exception as e:
            logger.error('get data failed: ' + str(e))
            if try_count > 3:
                break
            try_count = try_count + 1
