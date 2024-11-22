# %%
import requests
import base64
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth

# %%
#getting access token with client secrets
CLIENT_ID='46e038173abd4c32946bc979555ed98d'
CLIENT_SECRET='da0cfc26643340e595045a2a23ec5450'

#request token
url='https://accounts.spotify.com/api/token'
payload = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    #"scope": scope
}

response = requests.post(url, data=payload,timeout=20)
if response.status_code == 200:
    access_token = response.json().get("access_token")
    print("Access Token:", access_token)
else:
    print("Failed to obtain access token:", response.json())

# %%
# sp=spotipy.Spotify(auth=access_token)
# playlist_tracks = sp.playlist_tracks(playlist_id, fields='items(track(id, name, artists, album(id, name)))')
# playlist_tracks

# %%


# %%
def get_trending_playlist_data(playlist_id,access_token):
    sp = spotipy.Spotify(auth=access_token)
    playlist_tracks = sp.playlist_tracks(playlist_id, fields='items(track(id, name, artists, album(id, name)))')
    music_data = []
    for data in playlist_tracks['items']:
        track_name=data['track']['name']   
        artists = ', '.join([artist['name'] for artist in data['track']['artists']])
        album_name = data['track']['album']['name']
        album_id = data['track']['album']['id']
        track_id = data['track']['id']
    
        # Get audio features for the track
        audio_features = sp.audio_features(track_id)[0] if track_id != 'Not available' else None
        # Get release date of the album
        try:
            album_info = sp.album(album_id) if album_id != 'Not available' else None
            release_date = album_info['release_date'] if album_info else None
        except:
            release_date = None
        
        # Get popularity of the track
        try:
            track_info = sp.track(track_id) if track_id != 'Not available' else None
            popularity = track_info['popularity'] if track_info else None
        except:
            popularity = None
        ## Add additional track information to the track data
        track_data = {
            'Track Name': track_name,
            'Artists': artists,
            'Album Name': album_name,
            'Album ID': album_id,
            'Track ID': track_id,
            'Popularity': popularity,
            'Release Date': release_date,
            'Duration (ms)': audio_features['duration_ms'] if audio_features else None,
            'Explicit': track_info.get('explicit', None),
            'External URLs': track_info.get('external_urls', {}).get('spotify', None),
            'Danceability': audio_features['danceability'] if audio_features else None,
            'Energy': audio_features['energy'] if audio_features else None,
            'Key': audio_features['key'] if audio_features else None,
            'Loudness': audio_features['loudness'] if audio_features else None,
            'Mode': audio_features['mode'] if audio_features else None,
            'Speechiness': audio_features['speechiness'] if audio_features else None,
            'Acousticness': audio_features['acousticness'] if audio_features else None,
            'Instrumentalness': audio_features['instrumentalness'] if audio_features else None,
            'Liveness': audio_features['liveness'] if audio_features else None,
            'Valence': audio_features['valence'] if audio_features else None,
            'Tempo': audio_features['tempo'] if audio_features else None,
            # Add more attributes as needed
        }
        music_data.append(track_data)
    df = pd.DataFrame(music_data)
    return df

# %%
playlist_id= '37i9dQZF1DX76Wlfdnj7AP'
#playlist_id='4MKwSVleqMETr1wtBsfa4W'
music_df = get_trending_playlist_data(playlist_id, access_token)


# %%
music_df

# %%
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity

# %%
def calculate_weighted_popularity(release_date):
    if pd.isnull(release_date):
        return 0
    
    release_date = datetime.strptime(release_date, '%Y-%m-%d')
    #release_date = pd.to_datetime(release_date)
    # Calculate the time span between release date and today's date
    time_span = datetime.now() - release_date
    
    # Calculate the weighted popularity score based on time span (e.g., more recent releases have higher weight)
    weight = 1 / (time_span.days + 1)
    return weight

# %%
scaler = MinMaxScaler()
music_features=music_df[['Danceability', 'Energy', 'Key', 
                           'Loudness', 'Mode', 'Speechiness', 'Acousticness',
                           'Instrumentalness', 'Liveness', 'Valence', 'Tempo']]
music_features_scaled = scaler.fit_transform(music_features)


# %%
#recommending top songs based on content based filtering 
def content_based_recommendation(song,no_of_recommendations):
    if song not in music_df['Track Name'].values:
        return
    #Get the index of the song
    index=music_df[music_df['Track Name']==song].index.values.astype(int)
    #similarity scores of this song based on music features
    similarity_scores=cosine_similarity(music_features_scaled[index],music_features_scaled)
    #top song indeces of similar similarity scores
    top_indeces=similarity_scores.argsort()[0][::-1][1:no_of_recommendations+1]
    #top songs based on indeces
    top_songs=music_df.iloc[top_indeces]['Track Name']
    return top_songs

# %%
def hybrid_recommendation(input_song,no_of_recommendations):
    if input_song not in music_df['Track Name'].values:
        return
    # get content based recommendations
    content_based_rec=content_based_recommendation(input_song,no_of_recommendations)
    
    #content_based_rec['Weighted Popularity']=calculate_weighted_popularity(music_df.loc[music_df['Track Name']==song,'Release Date'].values[0])
     #popularity score of input song
    #popularity_score=music_df.loc[music_df['Track Name']==input_song,'Popularity'].values[0]
     #weighted popularity score
    #weighted_popularity_score=popularity_score*calculate_weighted_popularity(music_df.loc[music_df['Track Name']==input_song,'Release Date'].values[0])
    
    hybrid_recommendations=[]
    for song in content_based_rec:
        hyb_rec={
        'Track Name': song,
        'Artists': music_df.loc[music_df['Track Name'] == song, 'Artists'].values,
        'Album Name': music_df.loc[music_df['Track Name'] == song, 'Album Name'].values,
        'Release Date': music_df.loc[music_df['Track Name'] == song, 'Release Date'].values,
        'Weighted Popularity': (music_df.loc[music_df['Track Name']==song,'Popularity'].values)*
            calculate_weighted_popularity(music_df.loc[music_df['Track Name']==song,'Release Date'].values[0])
        }
        hybrid_recommendations.append(hyb_rec)
              
        
    #sort based on popularity
    hybrid_recommendations = pd.DataFrame(hybrid_recommendations).sort_values(by='Weighted Popularity', ascending=False)
    #exclude the input song
    hybrid_recommendations = hybrid_recommendations[hybrid_recommendations['Track Name'] != input_song]
    return hybrid_recommendations

# %%
input_song_name = "I'm Good (Blue)"
#input_song_name='Adivo Alladivo'
recommendations = hybrid_recommendation(input_song_name, no_of_recommendations=10)
print(f"Hybrid recommended songs for '{input_song_name}':")
print(recommendations)

# %%
#print(content_based_recommendation("I'm Good (Blue)",no_of_recommendations=5))

# %%



