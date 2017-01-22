from flask import Flask, redirect, redirect, g, render_template

from flask import jsonify
app = Flask(__name__, static_url_path='/static')
from google.cloud import language
from PyLyrics import *
from flask import request
import requests
import json
import csv
import base64
import urllib.parse

app.debug = True

song_sentiment_scores = dict()
all_song_data = dict()

def read_song_sentiment_scores_from_file():
    with open('top100-gm.csv') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            song_sentiment_scores[int(row[0])] = {
                        "track": row[1],
                        "artist": row[2],
                        "google_score": int((float(row[3]) + 1)*50),
                        "microsoft_score": int(float(row[4]) * 100)
                }

## DO NOT RUN THIS METHOD AGAIN ! ! ! ! 
def write_song_sentiment_scores():
    with open("regional-global-daily-latest.csv", "rt", encoding = "ISO-8859-1") as read_file:
        with open('top200.csv', 'wt') as write_file:
            reader = csv.reader(read_file)
            writer = csv.writer(write_file)
            for row in reader:
                rank = int(row[0])
                song_sentiment_scores[rank] = dict()
                song_sentiment_scores[rank]['track'] = row[1]
                song_sentiment_scores[rank]['artist'] = row[2]
                print("Working on track number {rank}, {track} by {artist}".format(
                            rank=rank, track=row[1], artist=row[2]))
                song_sentiment_scores[rank]['google_score'] = float(google_song_sentiment(song_sentiment_scores[rank]['artist'], song_sentiment_scores[rank]['track']))
                song_sentiment_scores[rank]['microsoft_score'] = float(microsoft_song_sentiment(song_sentiment_scores[rank]['artist'], song_sentiment_scores[rank]['track']))
                print("Google score is {}".format(song_sentiment_scores[rank]['google_score']))
                print("Microsoft score is {}".format(song_sentiment_scores[rank]['microsoft_score']))
                writer.writerow([rank, row[1], row[2], song_sentiment_scores[rank]['google_score'], song_sentiment_scores[rank]['microsoft_score']])

def parse_spotify_data():
    f = open('spotify_data')
    json_string = f.read()

    spotify_data_dict = json.loads(json_string)
    spotify_data_list = spotify_data_dict["audio_features"]
    # all_song_data = dict()

    for i in range(100):
        all_song_data[i + 1] = spotify_data_list[i]
        all_song_data[i + 1] = dict(list(all_song_data[i + 1].items()) + list(song_sentiment_scores[i + 1].items()))

    # print(all_song_data[0])

def all_song_data_to_file():
    json.dump(all_song_data, open("all_song_data", "w"))

def get_all_song_data():
    global all_song_data
    f = open('all_song_data')
    json_string = f.read()
    # print(json.loads(json_string))
    all_song_data = json.loads(json_string)
    all_song_data = {int(k): v for k,v in all_song_data.items()}

@app.route("/songSearch")
def single_song_dict_creator():
    artist = request.args.get('artist')
    song = request.args.get('song')
    access_token = request.args.get('access_token')
    microsoft_score = int(float(microsoft_song_sentiment(artist=artist, song=song))*100)
    google_score = int((float(google_song_sentiment(artist=artist, song=song))+1)*50)
    header = {'Authorization': 'Bearer ' + access_token} # TO DO ! ! ! ! ! !!  ! ! ! ! ! ! ! ! ! ! ! !
    response = requests.get('https://api.spotify.com/v1/search?q=artist:{artist} track:{song}&type=track&limit=1'.format(artist = artist, song = song), headers=header)
    dictionary_to_use = json.loads(response.text)
    song_id = None
    for x in dictionary_to_use['tracks']['items']:
        if x['type'] == 'track':
            song_id = x['id']
            break


    header = {'Authorization': 'Bearer ' + access_token} # TO DO ! ! ! ! ! !!  ! ! ! ! ! ! ! ! ! ! ! !
    response = requests.get('https://api.spotify.com/v1/audio-features/' + song_id, headers = header)
    song_dict = json.loads(response.text)
    song_dict["google_score"] = google_score
    song_dict["microsoft_score"] = microsoft_score
    song_dict['energy'] *= 100;
    song_dict['danceability'] *= 100;
    song_dict['acousticness'] *= 100;
    return json.dumps(song_dict)


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
REDIRECT_URI = "{}:{}/index/".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": "https://triple-s-156413.appspot-preview.com/index/",
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

@app.route("/login/")
def index():
    # Auth Step 1: Authorization
    #### WILL HAVE THE TWO ? THINGIES. 

    url_args = "&".join(["{}={}".format(key,urllib.parse.quote(val)) for key,val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)




@app.route("/index/")
def redirected_page():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    #print(auth_token)
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": "https://triple-s-156413.appspot-preview.com/index/",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    #base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET))
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    #print("response")
    #print(response_data)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]
    
    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}
    redirect_url = "http://localhost:5000/song?access_token="+access_token
    return redirect(redirect_url)
    # Get profile data
    #print("start")

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


def json_creator(string):
    #to be called after get_all_song_data() has been called and the dictionary has been populated.
    custom_dict = dict()
    for i in range(1, 101):
        track = all_song_data[i]['track']
        artist = all_song_data[i]['artist']
        dict_key = track + ", by " + artist

        custom_dict[dict_key] = all_song_data[i][string]
    return json.dumps(custom_dict)



@app.route("/hello")
def hello():
    # top_200_songs_reader()
    artist = request.args.get('artist')
    song = request.args.get('song')
    return str(google_song_sentiment(artist, song)) + " HELLO " + str(microsoft_song_sentiment(artist, song))
    # return str(google_song_sentiment(artist, song)) + "HELLO" + str(microsoft_song_sentiment(artist, song))
    # return jsonify(score=google_song_sentiment(artist, song))



@app.route("/microsoft")
def microsoft():
    return json_creator("microsoft_score")

@app.route("/")
def main_page():
    get_all_song_data()
    return render_template('index.html')

@app.route("/song")
def song_page():
    return render_template('song.html')

@app.route("/google")
def google():
    return json_creator("google_score")

@app.route("/danceability")
def danceability():
    return json_creator("danceability")

@app.route("/energy")
def energy():
    return json_creator("energy")

# @app.route("/instrumentalness")
# def instrumentalness():
    # return json_creator("instrumentalness")

@app.route("/acousticness")
def acousticness():
    return json_creator("acousticness")

if __name__ == "__main__":
    app.run()
