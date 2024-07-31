from elasticsearch import Elasticsearch, helpers
import json
es = Elasticsearch("https://localhost:9200", verify_certs=False,
                   api_key="eXJUempKQUJPSG9HaHYtd0Y1RnA6MEtibVhrVFZULUM2TFVYMnJLZWpsQQ==")

def save_json(data,filename="output/output.json"):
    with open(filename, "w") as outfile: 
        json.dump(data, outfile,indent = 4)

def search(queries):
    json_result={}
    for i,query in enumerate(queries):
        res = es.search(index='papers_relevance,papers_newest', body=query)
        json_result[f'query{i}']= [hit["_source"] for hit in res['hits']['hits']]
    return json_result
    # for hit in res['hits']['hits']:
    #     print(hit["_source"])

def main():
    # ساخت پرس و جو
    queries = [
        {
        "query": {
            "bool": {
                "must": [],
                "filter": [
                {
                    "match_phrase": {
                    "title": "cloud"
                    }
                },
                {
                    "match_phrase": {
                    "title": "security"
                    }
                }
                ],
                "should": [],
                "must_not": []
            }
        }
    },

    {
        "query": {
        "range": {
            "Date of Publication": {
            "gte": "2000-01-01T00:00:00.000+03:30",
            "lt": "2010-01-01T00:00:00.000+03:30"
            }
        }
    }
    },
    {
        "query": {
            "range": {
                "Cites in Papers": {
                "gte": "10"
                }
            }
        }
    },

    {
        "query": {
            "match_phrase": {
                "Authors.from": " USA"
            }
        }
    }
    ]
    result=search(queries)
    save_json(result)
if __name__ == '__main__':
    main()