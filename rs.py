
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_similar_papers(es,target_field,target_value,count):
    query=create_query(target_field,target_value)
    res = es.search(index='papers_relevance,papers_newest', body=query)
    target_paper=res['hits']['hits'][0]["_source"]
    return calculate_similarity(data,target_paper,count)
        

# def calculate_similarity(papers):
#     # paper['title']
#     ...
      
def calculate_similarity(papers,target_paper,count):
    similarities={}
    target_paper['IEEE Keywords']=' '.join(target_paper['IEEE Keywords'])
    target_paper['Author Keywords']=' '.join(target_paper['Author Keywords'])
    for key in ['title','IEEE Keywords','Author Keywords','Abstract']:
        docs=[paper[key] for paper in papers]
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(docs)
        query_vector = vectorizer.transform([target_paper[key]])

        # Compute cosine similarity between the query and all documents
        similarities[key] = cosine_similarity(query_vector, tfidf_matrix).flatten()
    score_list= 0.5* similarities['title'] +similarities['IEEE Keywords'] +similarities['Author Keywords'] + similarities['Abstract']
        
    top_indices = score_list.argsort()[-1*(count+1):][::-1][1:]
    # top_indices = score_list.argsort()[-count:][::-1] + 1
    top_docs = [(papers[idx]['title'],papers[idx]['DOI']) for idx in top_indices]
    
    return top_docs



def create_query(target_field,target_value):
    query = {
        "query": {
            "bool":{"must":[{"match":{target_field:target_value}}]}
        }
    }
    return query

data_newest = load_json('data/newest.json')['papers']
data_relevance = load_json('data/relevance.json')['papers']
data = data_newest +data_relevance
for paper in data:
    paper['IEEE Keywords']=' '.join(paper['IEEE Keywords'])
    paper['Author Keywords']=' '.join(paper['Author Keywords'])

 



    
    