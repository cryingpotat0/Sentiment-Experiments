from flask import Flask, redirect, redirect, g, render_template

from flask import jsonify
app = Flask(__name__)
from google.cloud import language
from PyLyrics import *
from flask import request
import requests
import json
import csv
import base64
import urllib.parse

app.debug = True

song_scores = dict()

def top_200_songs_reader():
    with open("regional-global-daily-latest.csv", "rt", encoding = "ISO-8859-1") as read_file:
        with open('top200.csv', 'wt') as write_file:
            reader = csv.reader(read_file)
            writer = csv.writer(write_file)
            for row in reader:
                rank = int(row[0])
                song_scores[rank] = dict()
                song_scores[rank]['track'] = row[1]
                song_scores[rank]['artist'] = row[2]
                print("Working on track number {rank}, {track} by {artist}".format(
                            rank=rank, track=row[1], artist=row[2]))
                song_scores[rank]['google_score'] = float(google_song_sentiment(song_scores[rank]['artist'], song_scores[rank]['track']))
                song_scores[rank]['microsoft_score'] = float(microsoft_song_sentiment(song_scores[rank]['artist'], song_scores[rank]['track']))
                print("Google score is {}".format(song_scores[rank]['google_score']))
                print("Microsoft score is {}".format(song_scores[rank]['microsoft_score']))
                writer.writerow([rank, row[1], row[2], song_scores[rank]['google_score'], song_scores[rank]['microsoft_score']])


def top_200_songs_writer():
    with open('top200.csv', 'wb') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in song_scores.items():
            writer.writerow([key, value])

app.debug = True

######## SPOTIFY START ############
CLIENT_ID = "9fff3ec0f724450d9c8ef35594ac4729"
CLIENT_SECRET = "4eb6f9b4d06f4ae1bdfd1cdb9ae5a7de"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)


# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5000
REDIRECT_URI = "{}:{}/index".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": "http://localhost:5000/index/",
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

@app.route("/login/")
def index():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key,urllib.parse.quote(val)) for key,val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


@app.route("/index")
def redirected_page():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET))
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]
    
    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}
    
    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)
    
    # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    playlist_data = json.loads(playlists_response.text)
    
    # Combine profile and playlist data to display
    display_arr = [profile_data] + playlist_data["items"]
    return str(display_arr)

######## SPOTIFY END ########

def google_sentiment_text(text):
    """Detects sentiment in the text."""
    language_client = language.Client()

    # Instantiates a plain text document.
    document = language_client.document_from_text(text)

    # Detects sentiment in the document. You can also analyze HTML with:
    #   document.doc_type == language.Document.HTML
    sentiment = document.analyze_sentiment()

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
    return str(google_song_sentiment(artist, song)) + " HELLO " + str(microsoft_song_sentiment(artist, song))
    # return str(google_song_sentiment(artist, song)) + "HELLO" + str(microsoft_song_sentiment(artist, song))
    # return jsonify(score=google_song_sentiment(artist, song))



@app.route("/microsoft")
def microsoft():
    return "Microsoft"

if __name__ == "__main__":
    app.run()
