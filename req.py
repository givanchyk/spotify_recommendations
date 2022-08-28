import json
import sys
import requests
import numpy as np
import pandas as pd
from urllib.parse import urlencode
from sklearn.cluster import KMeans

token_json = open('data.json')
access_token = json.load(token_json)['token']
headers = { 'Authorization': 'Bearer ' + access_token }

def top_query(limit=20, offset=0, time_range='long_term'):
    #returns list of tracks 
    query_size = {'limit': limit, 'offset':offset, 'time_range': time_range}
    req = requests.get('https://api.spotify.com/v1/me/top/tracks?' + urlencode(query_size), headers=headers)
    if req.status_code != 200:
        raise RuntimeError(req.text)
    return req.json()['items']

def recommendation_query(limit=20, seed_tracks=None, seed_artists=None):
    #returns list of tracks
    artist_query = {limit:limit}
    if seed_tracks:
        artist_query['seed_tracks'] = seed_tracks
    if seed_artists:
        artist_query['seed_artists'] = seed_artists
    req = requests.get('https://api.spotify.com/v1/recommendations?' + urlencode(artist_query), headers=headers)
    return req.json()['tracks']

def print_name(tracks):
    #input - list of tracks, returns their names
    try:
        for track in tracks:
            print(', '.join([artist['name'] for artist in track['artists']]), "-", track['name'])
            
    except TypeError:
        print(', '.join([artist['name'] for artist in tracks['artists']]), "-", tracks['name'])

def get_track(id):
    #get track by id
    req = requests.get('https://api.spotify.com/v1/tracks/' + id, headers=headers)
    return req.json()

def get_all_top(time_range='long_term'):
    #max query, 50+49 tracks
    req1 = top_query(limit=49, time_range=time_range)
    req2 = top_query(limit=50, offset=49, time_range=time_range)
    return req1 + req2

def top_artist(id):
    req = requests.get('https://api.spotify.com/v1/tracks/artists/%s/top-tracks?country=US' % id, headers=headers)
    return req.json()['tracks']

def dist_1():
    track_hash = {}
    top_tracks = get_all_top()
    for track in top_tracks:
        track_hash[track['id']] = track
        req = recommendation_query(seed_tracks=track['id'])
        for track2 in req:
            track_hash[track2['id']] = track2
    return [track_hash[id] for id in track_hash]

def reduced(tracks):
    tracks_reduced = [{} for i in range(len(tracks))]
    for i in range(len(tracks)):
        tracks_reduced[i]['artists'] = ', '.join([artist['name'] for artist in tracks[i]['artists']])
        tracks_reduced[i]['name'] = tracks[i]['name']
        tracks_reduced[i]['duration_ms'] = tracks[i]['duration_ms']
        tracks_reduced[i]['id'] = tracks[i]['id']
        tracks_reduced[i]['popularity'] = tracks[i]['popularity']
    return tracks_reduced

def audio_features(tracks, add=False):
    req = []
    for i in range((len(tracks)+99)//100):
        track_batch = tracks[i*100:(i+1)*100]
        batch_id = ','.join([track['id'] for track in track_batch])
        batch_req = requests.get('https://api.spotify.com/v1/audio-features/?ids=%s' % batch_id, headers=headers).json()
        req += batch_req['audio_features']
    if add:
        tracks_req = tracks.copy()
        for i in range(len(tracks)):
            for feature in ['acousticness', 'danceability', 'energy', 'instrumentalness', 'speechiness', 'tempo', 'valence']:
                try:
                    tracks_req[i][feature] = req[i][feature]
                except:
                    tracks_req[i][feature] = None
        return tracks_req
    return req

megareq = dist_1()

req = audio_features(reduced(megareq), add=True)
top_artists = audio_features(reduced(get_all_top()), add=True)

def distance(track1, track2): #TODO USE THIS!!!
    d = 0
    for ch in ['popularity', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'speechiness', 'tempo', 'valence']:
        difference = abs(track1[ch] - track2[ch])
        if ch == 'popularity':
            difference /= 100
        elif ch == 'tempo':
            difference /= 400
        d += difference
    return d
def filter():
    pass
def kmeans_fit_predict(user_tracks, query_tracks, n_clusters=6): #TODO: split into 2 parts
    df_user_tracks = pd.DataFrame.from_records(user_tracks)
    df_user_tracks = df_user_tracks[['popularity', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'speechiness', 'tempo', 'valence']]
    df_user_tracks.dropna(inplace=True)
    df_user_tracks['popularity'] = df_user_tracks['popularity'] / 200
    df_user_tracks['tempo'] = df_user_tracks['tempo'] / 400
    df_query_tracks = pd.DataFrame.from_records(query_tracks)
    df_query_tracks = df_query_tracks[['popularity', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'speechiness', 'tempo', 'valence']]
    df_query_tracks.dropna(inplace=True)
    df_query_tracks['popularity'] = df_query_tracks['popularity'] / 200
    df_query_tracks['tempo'] = df_query_tracks['tempo'] / 400
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(df_user_tracks)
    res = []
    for cluster in kmeans.cluster_centers_:
        cluster_distances = [np.linalg.norm(cluster - df_query_tracks.iloc[i]) for i in range(len(df_query_tracks))]
        num = 10
        best_num = sorted(range(len(df_query_tracks)), key=lambda x: cluster_distances[x])
        res.append(best_num[:num])
    return res

kmeans_preds = kmeans_fit_predict(top_artists, req, n_clusters=10)
preds_val = [[req[i] for i in kmeans_preds[j]] for j in range(len(kmeans_preds))]
for i in range(len(preds_val)):
    for j in range(len(preds_val[i])):
        allowed_keys = ['artists', 'name', 'id']
        all_keys = list(preds_val[i][j].keys())
        for key in all_keys:
            if key not in allowed_keys:
                preds_val[i][j].pop(key)
with open('res.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(preds_val, ensure_ascii=False))
print('Success!')
sys.stdout.flush()