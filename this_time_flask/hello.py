from flask import Flask
app = Flask(__name__)
from google.cloud import language
from PyLyrics import *
from flask import request

app.debug = True





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

@app.route("/hello")
def hello():
    artist = request.args.get('artist')

    song = request.args.get('song')
    #return artist

    # print(google_song_sentiment(artist, song))
    # lyrics = getLyrics("Taylor Swift", "Blank Space")
    # print(lyrics)
    # split_lyrics = splitLyrics(lyrics)
    # print(split_lyrics)
    # sentiment_scores = [google_sentiment_text(x) for x in split_lyrics]
    # print(sentiment_scores)

    # return "HELLO!!!!"
    # return "Hello World!"
    return str(google_song_sentiment(artist, song))


if __name__ == "__main__":
    app.run()