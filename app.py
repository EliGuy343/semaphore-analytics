from flask import Flask
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
import json
import nltk
import string
from collections import Counter
from flask import request
from flask_cors import CORS

from nltk.sentiment import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()


app = Flask(__name__)
CORS(app)

stop_words = ["a", "an","I","i", "the", "this", "that", "it", "is", "really", "to", "and", "for", "these", "those"] + list(string.punctuation)


cred = credentials.Certificate("semaphore-a7fd1-firebase-adminsdk-dyeb3-e430d9430a.json")
fb_admin = firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/total')
def max_posts_users():
    posts_ref = db.collection(u'posts')
    user_ref = db.collection(u'users')

    posts = []
    users = []

    for doc in posts_ref.stream():
        posts.append(doc.to_dict())
        
    for doc in user_ref.stream():
        users.append(doc.to_dict())

    result = {
        "totalPosts": int(len(posts)),
        "TotalUsers": int(len(users))
    }
    result_json = json.dumps(result)
    return result_json

@app.route('/active')
def most_active():
    posts_ref = db.collection(u'posts')
    posts = []

    for doc in posts_ref.stream():
        posts.append(doc.to_dict())

    posts_df = pd.DataFrame(posts)
    posts_df_grouped = posts_df.groupby("username")["text"].count()
    max_posts = posts_df_grouped.nlargest(3).to_dict()
    result = {
        "mostActivePosters": max_posts
    }
    result_json = json.dumps(result)
    return result_json
    

@app.route('/trending/top5')
def trending_words():
    doc_ref = db.collection(u'posts')
    docs = doc_ref.stream()
    posts = []
    for doc in docs:
        posts.append(doc.to_dict())

    posts_df = pd.DataFrame(posts)
    posts = posts_df['text']
    filtered_wordlists = []

    for post in posts:
        wordlist = [word for word in nltk.word_tokenize(post) if word not in stop_words]
        filtered_wordlists.append(wordlist)

    all_words = [item for sublist in filtered_wordlists for item in sublist]
    word_counter = Counter(all_words)
    most_common_words = word_counter.most_common(5)
    result_json = json.dumps(most_common_words)

    return result_json
    
@app.route('/sentiment')
def sentiment_analysis():
    search_word = ""
    if(request.args.get("search")):
        search_word = request.args.get("search")
    
    doc_ref = db.collection(u'posts')
    docs = doc_ref.stream()
    posts = []
    for doc in docs:
        posts.append(doc.to_dict())

    posts_df = pd.DataFrame(posts)
    posts_search = posts_df[posts_df.text.str.contains(search_word)]
    posts_list = posts_search['text'].values.tolist()
    result = map(lambda x: sia.polarity_scores(x), posts_list)
    result_list = list(result)
    result_json = json.dumps(result_list)

    return result_json

if __name__ == "__main__":
    app.run(debug=True)
