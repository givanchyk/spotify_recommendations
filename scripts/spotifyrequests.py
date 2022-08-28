import requests
from urllib.parse import urlencode

class SpotifyReq:
    def __init__(self, token):
        self.headers = { 'Authorization': 'Bearer ' + token }

    def top_query(self, limit=20, offset=0, time_range='long_term'):
        #returns list of tracks 
        query_size = {'limit': limit, 'offset':offset, 'time_range': time_range}
        req = requests.get('https://api.spotify.com/v1/me/top/tracks?' + urlencode(query_size), headers=self.headers)
        if req.status_code != 200:
            raise RuntimeError(req.text)
        return req.json()['items']

    def recommendation_query(self, limit=20, seed_tracks=None, seed_artists=None):
        #returns list of tracks
        artist_query = {limit:limit}
        if seed_tracks:
            artist_query['seed_tracks'] = seed_tracks
        if seed_artists:
            artist_query['seed_artists'] = seed_artists
        req = requests.get('https://api.spotify.com/v1/recommendations?' + urlencode(artist_query), headers=self.headers)
        response = []
        if req.status_code == 200:
            response = req.json()['tracks']
        return response

    def get_track(self, id):
        #get track by id
        req = requests.get('https://api.spotify.com/v1/tracks/' + id, headers=self.headers)
        return req.json()

    def get_all_top(self, time_range='long_term'):
        #max query, 50+49 tracks
        req1 = self.top_query(limit=49, time_range=time_range)
        req2 = self.top_query(limit=50, offset=49, time_range=time_range)
        return req1 + req2
    
    def print_name(self, tracks):
        #input - list of tracks, returns their names
        try:
            for track in tracks:
                print(', '.join([artist['name'] for artist in track['artists']]), "-", track['name'])
                
        except TypeError:
            print(', '.join([artist['name'] for artist in tracks['artists']]), "-", tracks['name'])
        
    def get_track(self, id):
        #get track by id
        req = requests.get('https://api.spotify.com/v1/tracks/' + id, headers=self.headers)
        return req.json()
    
    def audio_features(self, tracks):
        req = []
        for i in range((len(tracks)+99)//100):
            track_batch = tracks[i*100:(i+1)*100]
            batch_id = ','.join([track['id'] for track in track_batch])
            batch_req = requests.get('https://api.spotify.com/v1/audio-features/?ids=%s' % batch_id, headers=self.headers).json()
            req += batch_req['audio_features']
        tracks_req = tracks.copy()
        for i in range(len(tracks)):
            for feature in ['acousticness', 'danceability', 'energy', 'instrumentalness', 'speechiness', 'tempo', 'valence']:
                try:
                    tracks_req[i][feature] = req[i][feature]
                except:
                    tracks_req[i][feature] = None
        return tracks_req
    
    def reduced(self, tracks):
        tracks_reduced = [{} for i in range(len(tracks))]
        for i in range(len(tracks)):
            tracks_reduced[i]['artists'] = ', '.join([artist['name'] for artist in tracks[i]['artists']])
            tracks_reduced[i]['name'] = tracks[i]['name']
            tracks_reduced[i]['duration_ms'] = tracks[i]['duration_ms']
            tracks_reduced[i]['id'] = tracks[i]['id']
            tracks_reduced[i]['popularity'] = tracks[i]['popularity']
        return tracks_reduced
    
    def dist_1(self):
        track_hash = {}
        top_tracks = self.get_all_top()
        for track in top_tracks:
            track_hash[track['id']] = track
            req = self.recommendation_query(seed_tracks=track['id'])
            for track2 in req:
                track_hash[track2['id']] = track2
        return [track_hash[id] for id in track_hash]

