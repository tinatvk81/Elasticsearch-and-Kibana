from flask import Flask, request, render_template
from elasticsearch import Elasticsearch
import json
import rs

app = Flask(__name__)

# Elasticsearch client
es = Elasticsearch("https://localhost:9200", verify_certs=False, 
                   api_key="NkZ0aGs1QUJteUNhT3RGMzZaZFM6RmJlZkxBcGFTeS1NYmxneUdfNGFSQQ==")

# Kibana settings
KIBANA_URL = 'http://localhost:5601'
DASHBOARD_ID = 'be62c0e8-5553-4be3-9878-730ff92a1155'

def create_kibana_query(results):
    if results:
        should_queries = []
        for hit in results:
            should_queries.append({
                "match": {
                    "title": hit['_source']['title']  # Assuming title field from Elasticsearch
                }
            })

        kibana_query = {
            "query": {
                "bool": {
                    "should": should_queries
                }
            }
        }
        return kibana_query
    else:
        return None

def get_dashboard_url(query):
    return f"http://localhost:5601/app/kibana#/dashboard/{DASHBOARD_ID}?_a=(query:(query_string:(query:'{query}')))"

@app.route('/')
def home():
    return render_template('search.html')

@app.route('/search', methods=['POST'])
def search():
    conditions = []
    queries = []

    fields = request.form.getlist('field')
    queries = request.form.getlist('query')
    operators = request.form.getlist('operator')
    
    for i in range(len(queries)):
        match_query = {
            "match": {
                fields[i]: queries[i]
            }
        }
        conditions.append(match_query)

    if conditions:
        bool_query = {"must": [conditions[0]]}
        for i in range(1, len(conditions)):
            operator = operators[i - 1]
            if operator == "AND":
                if "must" not in bool_query:
                    bool_query["must"] = []
                bool_query["must"].append(conditions[i])
            else:  # operator is "OR"
                if "should" not in bool_query:
                    bool_query = {"should": bool_query.get("must", [])}
                bool_query["should"].append(conditions[i])

        es_query = {
            "query": {
                "bool": bool_query
            }
        }
    else:
        es_query = {"query": {"match_all": {}}}

    results = es.search(index="papers_relevance,papers_newest", body=es_query)['hits']['hits']
    kibana_query = create_kibana_query(results)
    search_query = json.dumps(es_query['query'])
    embed_url = get_dashboard_url(search_query)
    print(embed_url)

    return render_template('dashboard.html', kibana_embed_url=embed_url)

@app.route('/rs_search', methods=['POST'])
def rs_search():
    rs_field = request.form['rs_field']
    title_doi = request.form['title_doi']
    num_results = int(request.form['num_results'])
    
    similar_papers = rs.get_similar_papers(es, rs_field, title_doi, num_results)
    return render_template('rs.html', list=similar_papers, enumerate=enumerate)

    # return f"Field: {rs_field}, Title or DOI: {title_doi}, Number of similar articles: {num_results}"

if __name__ == '__main__':
    app.run(debug=True)
