var express = require('express'); // Express web server framework
var request = require('request'); // "Request" library
var querystring = require('querystring');
var cors = require('cors');
var cookieParser = require('cookie-parser');
var fs = require('fs');
// var mysql = require('mysql')

var client_id = '895a9b9070804bb1b15fbb1baf15a1f3'; // Your client id
var client_secret = 'dbaa400e7c7c49b78e7e21b03992f3ff'; // Your secret  
var redirect_uri = 'http://localhost:8888/callback'; // Your redirect uri
var stateKey = 'spotify_auth_state';

var app = express();
app.use(express.static(__dirname + '/public'))
   .use(cors())
   .use(cookieParser());

var generateRandomString = function(length) {
  var text = '';
  var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

  for (var i = 0; i < length; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
};
// function simple_request(){

//     url: 'https://api.spotify.com/v1/me',
// }
app.get('/666', (req, res) => {
    const spawn = require('child_process').spawn;
    const pythonProcess  = spawn('python', ['scripts/main.py']);
    pythonProcess.stdout.on('data', (x) => {
      fs.readFile('res.json', 'utf-8', function(err, data){
        console.log(data);
        var jdata = JSON.parse(data);
  
        var s = '';
        for (let i=0; i<jdata.length; i++){
          s += "-------------<br>";
          for (let j=0; j<jdata[i].length; j++){
            s += jdata[i][j]['name']+' - '+jdata[i][j]['artists'] + '<br>';
          }
        }
        res.send(s);
      })
    }); 
     
    // var body = '';
    // filePath = __dirname + '/public/data.txt';

})

app.get('/login', function(req, res) {
    var state = generateRandomString(16);
    var scope = 'user-read-private user-read-email user-library-read user-follow-read user-top-read';
    res.cookie(stateKey, state);
    res.redirect('https://accounts.spotify.com/authorize?' +
        querystring.stringify({
            response_type: 'code',
            client_id: client_id,
            scope: scope,
            redirect_uri: redirect_uri,
            state: state
        })
      );
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
            console.log(access_token);
            var token_json = {token: access_token}
            var data = JSON.stringify(token_json);
            fs.writeFileSync('token.json', data);
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
  
console.log('Listening on 8888');
app.listen(8888);
