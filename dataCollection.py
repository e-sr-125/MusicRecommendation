import requests
import base64
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth

#playlist_id= '37i9dQZF1DX76Wlfdnj7AP'
CLIENT_ID='46e038173abd4c32946bc979555ed98d'
CLIENT_SECRET='da0cfc26643340e595045a2a23ec5450'

def get_accesstoken():
    #request token
    url='https://accounts.spotify.com/api/token'
    payload = {
       "grant_type": "client_credentials",
       "client_id": CLIENT_ID,
       "client_secret": CLIENT_SECRET,
    }

    response = requests.post(url, data=payload)
    if response.status_code == 200:
       access_token = response.json().get("access_token")
       return access_token
    else:
       return response.json()



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

