from flask import Flask
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
import json

flask_app = Flask(__name__)

cred = credentials.Certificate("semaphore-a7fd1-firebase-adminsdk-dyeb3-e430d9430a.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

@flask_app.route('/max/user')
def max_posts_user():
    doc_ref = db.collection(u'posts')
    docs = doc_ref.stream()
    posts = []
    comments = []
    for doc in docs:
        comments_ref = db.collection(u'posts').document(doc.id).collection('comments')

        for comment in comments_ref.stream():
            comments.append(comment.to_dict())

        posts.append(doc.to_dict())

    posts_df = pd.DataFrame(posts)
    posts_df_grouped = posts_df.groupby("username")["text"].count()
    max_user = posts_df_grouped.idxmax()
    max_amount = posts_df_grouped.max()
    
    comments_df = pd.DataFrame(comments)
    comments_df_grouped = comments_df.groupby("username")["comment"].count()
    max_user_comments = comments_df_grouped.idxmax()
    max_amount_comments = comments_df_grouped.max()

    result ={
        "max_posts":{
            "user": max_user,
            "max_posts": max_amount
        },
        "max_comments":{
            "user": max_user_comments,
            "max_comments": max_amount_comments
        }
    }
    result_json = json.dumps(result)
    return result_json

if __name__ == "__main__":
    flask_app.run(debug=True)
