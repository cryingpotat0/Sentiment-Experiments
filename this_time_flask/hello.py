from flask import Flask
app = Flask(__name__)
from google.cloud import language
from PyLyrics import *
from flask import request
import requests
import json
import csv

app.debug = True

song_scores = dict()

def top_200_songs_reader():
    with open("regional-global-daily-latest.csv", "rt", encoding = "ISO-8859-1") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rank = int(row[0])
            song_scores[rank] = dict()
            song_scores[rank]['track'] = row[1]
            song_scores[rank]['artist'] = row[2]
            print("Working on track number {rank}, {track} by {artist}".format(
                        rank=rank, track=row[1], artist=row[2]))
            song_scores[rank]['google_score'] = float(google_song_sentiment(song_scores[rank]['artist'], song_scores[rank]['track']))
            song_scores[rank]['microsoft_score'] = float(microsoft_song_sentiment(song_scores[rank]['artist'], song_scores[rank]['track']))

def top_200_songs_writer():
    with open('top200.csv', 'wb') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in mydict.items():
            writer.writerow([key, value])

def google_sentiment_text(text):
    """Detects sentiment in the text."""
    language_client = language.Client()

    # Instantiates a plain text document.
    document = language_client.document_from_text(text)

    # Detects sentiment in the document. You can also analyze HTML with:
    #   document.doc_type == language.Document.HTML
    sentiment = document.analyze_sentiment()

    # print('Score: {}'.format(sentiment.score))
    # print('Magnitude: {}'.format(sentiment.magnitude))

    return sentiment.score

def getLyrics(artist, song):
    try:
        print(artist)
        print(song)
        return PyLyrics.getLyrics(str(artist), str(song))
    except ValueError:
        return "SORRY"

def splitLyrics(lyrics, BREAK_LIMIT = 300):
    return [lyrics[i : i + BREAK_LIMIT] for i in range(0, len(lyrics), BREAK_LIMIT)]

def google_song_sentiment(artist, song):
    lyrics = getLyrics(artist, song)

    split_lyrics = splitLyrics(lyrics)
    sentiment_scores = [google_sentiment_text(x) for x in split_lyrics]
    return str(sum(sentiment_scores)/len(sentiment_scores))

def microsoft_song_sentiment(artist, song):
    lyrics = getLyrics(artist, song)
    lyrics = lyrics.replace("\n\n", ". ")
    split_lyrics = splitLyrics(lyrics)

    d = [{"id": x+1, "text": split_lyrics[x]} for x in range(len(split_lyrics))]
    data = {"documents" : d}
    headers = {'Ocp-Apim-Subscription-Key': 'ab4d68e54a814f768d0402035c5645a5',
            'Content-Type': 'application/json',
            'Accept': 'application/json'}

    r = requests.post('https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment', data = json.dumps(data), headers=headers)

    list_of_scoredicts = json.loads(r.text)['documents']
    scores = [x['score'] for x in list_of_scoredicts]
    return str(sum(scores)/len(scores))


@app.route("/hello")
def hello():
    top_200_songs_reader()

    artist = request.args.get('artist')
    song = request.args.get('song')

    return str(google_song_sentiment(artist, song) * 50) + " HELLO " + str((microsoft_song_sentiment(artist, song) - 0.5) * 100)





if __name__ == "__main__":
    app.run()