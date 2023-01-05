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
    for doc in docs:
        posts.append(doc.to_dict())
    posts_df = pd.DataFrame(posts)
    posts_df_grouped = posts_df.groupby("username")["text"].count()
    max_user = posts_df_grouped.idxmax()
    max_amount = posts_df_grouped.max()
    result = {"user": max_user, "max_posts": max_amount }
    result_json = json.dumps(result)
    return result_json

if __name__ == "__main__":
    flask_app.run(debug=True)
