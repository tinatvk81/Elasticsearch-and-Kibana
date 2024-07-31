from elasticsearch import Elasticsearch, helpers
import json
from datetime import datetime
from dateutil.parser import parse

# اتصال به Elasticsearch
es = Elasticsearch("https://localhost:9200", verify_certs=False,
                   api_key="eXJUempKQUJPSG9HaHYtd0Y1RnA6MEtibVhrVFZULUM2TFVYMnJLZWpsQQ==")

# تابع برای خواندن داده‌های JSON
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def convert_to_date(paper):
    date_str = paper.get("Date of Publication")
    if date_str:
        try:
            # تبدیل رشته به datetime با استفاده از dateutil.parser
            date_obj = parse(date_str)
            paper["Date of Publication"] = date_obj
            print(date_obj)
        except ValueError:
            pass
    return paper

# بارگذاری داده‌ها از فایل‌ها
data1 = load_json('data/newest.json')['papers']
data2 = load_json('data/relevance.json')['papers']


def insert(data,index):
# ادغام داده‌ها

    # تبدیل رشته‌های تاریخ به datetime قبل از ایندکس کردن
    converted_data = [convert_to_date(paper) for paper in data]


    # Index کردن داده‌ها
    actions = [
        {
            "_index": index,
            "_source": paper
        }
        for paper in converted_data
    ]

    helpers.bulk(es, actions)
    print(f"Data {index} indexed successfully!")

insert(data1,"papers_newest")
insert(data2,"papers_relevance")