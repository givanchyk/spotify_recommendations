import sys
import json
from spotifyrequests import SpotifyReq
from model import kmeans_fit_predict
token_json = open('token.json')
token = json.load(token_json)['token']
sreq = SpotifyReq(token)
all_stream = sreq.dist_1()
reduced_stream = sreq.reduced(all_stream)
req_stream = sreq.audio_features(reduced_stream)
top_user = sreq.audio_features(sreq.reduced(sreq.get_all_top()))
kmeans_preds = kmeans_fit_predict(top_user, req_stream, n_clusters=10)
for i in range(len(kmeans_preds)):
    for j in range(len(kmeans_preds[i])):
        allowed_keys = ['artists', 'name', 'id']
        all_keys = list(kmeans_preds[i][j].keys())
        for key in all_keys:
            if key not in allowed_keys:
                kmeans_preds[i][j].pop(key)
with open('res.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(kmeans_preds, ensure_ascii=False))
print('Success!')
sys.stdout.flush()


