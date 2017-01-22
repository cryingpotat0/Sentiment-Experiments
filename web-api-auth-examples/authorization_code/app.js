/**
 * This is an example of a basic node.js script that performs
 * the Authorization Code oAuth2 flow to authenticate against
 * the Spotify Accounts.
 *
 * For more information, read
 * https://developer.spotify.com/web-api/authorization-guide/#authorization_code_flow
 */

var express = require('express'); // Express web server framework
var request = require('request'); // "Request" library
var querystring = require('querystring');
var cookieParser = require('cookie-parser');

var client_id = '9fff3ec0f724450d9c8ef35594ac4729'; // Your client id
var client_secret = '4eb6f9b4d06f4ae1bdfd1cdb9ae5a7de'; // Your secret
var redirect_uri = 'http://localhost:8888/callback'; // Your redirect uri
// const Language = require('@google-cloud/language');

var gcloud = require('google-cloud');
var language = gcloud.language;
var languageClient = language({
  projectId: 'sentiment-analysis',
  keyFilename: '/Users/muditgupta/Desktop/Feedback\ Sorter-fd2dda1678e8.json'
});



function analyzeSentimentOfText (text) {

  var document = languageClient.document(text);


  document.detectSentiment(function(err, sentiment) {
  // sentiment = 100 // Large numbers represent more positive sentiments. 
     console.log(sentiment);
  });
}


//   // Instantiates a client
//   const language = languageClient();

//   // Instantiates a Document, representing the provided text
//   const document = language.document({
//     // The document text, e.g. "Hello, world!"
//     content: text
//   });

//   // Detects the sentiment of the document
//   return document.detectSentiment()
//     .then((results) => {
//       const sentiment = results[0];

//       console.log(`Sentiment: ${sentiment >= 0 ? 'positive' : 'negative'}.`);

//       return sentiment;
//     });
// }


/**
 * Generates a random string containing numbers and letters
 * @param  {number} length The length of the string
 * @return {string} The generated string
 */
var generateRandomString = function(length) {
  var text = '';
  var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

  for (var i = 0; i < length; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
};

var stateKey = 'spotify_auth_state';

var app = express();

app.use(express.static(__dirname + '/public'))
   .use(cookieParser());

app.get('/login', function(req, res) {

  var state = generateRandomString(16);
  res.cookie(stateKey, state);

  // your application requests authorization
  var scope = 'user-read-private user-read-email';
  res.redirect('https://accounts.spotify.com/authorize?' +
    querystring.stringify({
      response_type: 'code',
      client_id: client_id,
      scope: scope,
      redirect_uri: redirect_uri,
      state: state
    }));
});

app.get('/callback', function(req, res) {

  // your application requests refresh and access tokens
  // after checking the state parameter

  var code = req.query.code || null;
  var state = req.query.state || null;
  var storedState = req.cookies ? req.cookies[stateKey] : null;

  if (state === null || state !== storedState) {
    res.redirect('/#' +
      querystring.stringify({
        error: 'state_mismatch'
      }));
  } else {
    res.clearCookie(stateKey);
    var authOptions = {
      url: 'https://accounts.spotify.com/api/token',
      form: {
        code: code,
        redirect_uri: redirect_uri,
        grant_type: 'authorization_code'
      },
      headers: {
        'Authorization': 'Basic ' + (new Buffer(client_id + ':' + client_secret).toString('base64'))
      },
      json: true
    };

    request.post(authOptions, function(error, response, body) {
      if (!error && response.statusCode === 200) {

        var access_token = body.access_token,
            refresh_token = body.refresh_token;

        var options = {
          url: 'https://api.spotify.com/v1/me',
          headers: { 'Authorization': 'Bearer ' + access_token },
          json: true
        };

        // use the access token to access the Spotify Web API
        request.get(options, function(error, response, body) {
          console.log(body);
        });

        // we can also pass the token to the browser to make requests from there
        res.redirect('/#' +
          querystring.stringify({
            access_token: access_token,
            refresh_token: refresh_token
          }));
      } else {
        res.redirect('/#' +
          querystring.stringify({
            error: 'invalid_token'
          }));
      }
    });
  }
});

app.get('/refresh_token', function(req, res) {

  // requesting access token from refresh token
  var refresh_token = req.query.refresh_token;
  var authOptions = {
    url: 'https://accounts.spotify.com/api/token',
    headers: { 'Authorization': 'Basic ' + (new Buffer(client_id + ':' + client_secret).toString('base64')) },
    form: {
      grant_type: 'refresh_token',
      refresh_token: refresh_token
    },
    json: true
  };

  request.post(authOptions, function(error, response, body) {
    if (!error && response.statusCode === 200) {
      var access_token = body.access_token;
      res.send({
        'access_token': access_token
      });
    }
  });
});



console.log('Listening on 8888');
app.get('/sentiment', function(req, res) {
  var document = languageClient.document(req.query.lyric);
  console.log(req.query.lyric);

  document.detectSentiment(function(err, sentiment) {
  // sentiment = 100 // Large numbers represent more positive sentiments. 
     res.json({score: sentiment})
  });
  
});
app.listen(8888);
