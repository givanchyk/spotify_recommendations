import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

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
    preds_val = [[query_tracks[i] for i in res[j]] for j in range(len(res))]
    return preds_val