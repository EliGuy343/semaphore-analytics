FROM python:3.8
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN python -m nltk.downloader punkt
RUN python -m nltk.downloader vader_lexicon
ENV PORT=80