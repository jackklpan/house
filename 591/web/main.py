from typing import List, Optional
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pymongo import MongoClient

client = MongoClient()
db = client['rentdb']
house_col = db['houses']

app = FastAPI()


@app.get('/')
def read_root(page_size:int,
            page_num:int,
            sex:Optional[List[str]]=Query(['1', '2', '3']),
            regionname:Optional[List[str]]=Query(['新北市', '台北市']),
            phone_number:Optional[str]=None,
            post_by_house_owner:Optional[bool]=None,
            last_name:Optional[str]=None,
            poster_sex:Optional[str]=None,
            ):
    try:
        skips = page_size * (page_num - 1)
        query_dict = {
            'sex': {'$in': sex},
            'regionname': {'$in': regionname},
        }
        if last_name != None:
            query_dict['linkman'] = {'$regex': '^{}'.format(last_name)}
        if phone_number != None:
            query_dict['phone_number'] = {'$eq': phone_number}
        if post_by_house_owner != None:
            if post_by_house_owner == False:
                query_dict['post_owner'] = {'$ne': '屋主'}
            else:
                query_dict['post_owner'] = {'$eq': '屋主'}
        if poster_sex != None:
            if poster_sex == '男':
                query_dict['nick_name'] = {'$regex': '.*先生$'}
            elif poster_sex == '女':
                query_dict['nick_name'] = {'$regex': '.*(小姐|太太)$'}
        result = list(house_col.find(query_dict).skip(skips).limit(page_size))
        return JSONResponse({
                'status': 'success',
                'data': result})
    except Exception as e:
        return JSONResponse({
                'status': 'failed',
                'error': str(e)})
