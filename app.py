from flask import Flask
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
import json
import nltk
import string
from collections import Counter
from transformers import pipeline
from flask import request
sentiment_pipeline = pipeline("sentiment-analysis")

flask_app = Flask(__name__)
stop_words = ["a", "an","I","i", "the", "this", "that", "it", "is", "really", "to", "and", "for", "these", "those"] + list(string.punctuation)


cred = credentials.Certificate("semaphore-a7fd1-firebase-adminsdk-dyeb3-e430d9430a.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

@flask_app.route('/total')
def max_posts_user():
    posts_ref = db.collection(u'posts')
    user_ref = db.collection(u'users')

    posts = []
    users = []
    for doc in posts_ref.stream():
        posts.append(doc.to_dict())
        
    for doc in user_ref.stream():
        users.append(doc.to_dict())
    

    posts_df = pd.DataFrame(posts)
    posts_df_grouped = posts_df.groupby("username")["text"].count()
    max_user = posts_df_grouped.idxmax()
    max_amount = posts_df_grouped.max()
    

    result = {
        "max_posts":
        {
            "user": max_user,
            "max_posts": max_amount
        },
        "Total_posts": len(posts),
        "total_users": len(users)
    }
    result_json = json.dumps(result)
    return result_json


@flask_app.route('/trending/top5')
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
    
@flask_app.route('/sentiment')
def sentiment_analysis():
    search_word = request.args.get("search")
    
    doc_ref = db.collection(u'posts')
    docs = doc_ref.stream()
    posts = []
    for doc in docs:
        posts.append(doc.to_dict())

    posts_df = pd.DataFrame(posts)
    posts_search = posts_df[posts_df.text.str.contains(search_word)]
    posts_list = posts_search['text'].values.tolist()
    result = sentiment_pipeline(posts_list)
    result_json = json.dumps(result)
    return result_json

if __name__ == "__main__":
    flask_app.run(debug=True)
