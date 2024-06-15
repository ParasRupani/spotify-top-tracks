import pandas as pd, numpy as np
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import eli5
from eli5.sklearn import PermutationImportance

# # Set up Spotify API credentials
# secrets = dotenv_values(".env")
# client_id, client_secret = secrets.values()

client_id, client_secret = st.secrets()

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)


def truncate_title(title, max_len=45):
    if len(title) > max_len:
        return title[:max_len] + ".."
    else:
        return title

# Function to get top tracks and artists
def get_top_data():
    sp = spotipy.Spotify(auth_manager=auth_manager)
     
    # Users Top Tracks:
    top_tracks = sp.current_user_top_tracks(limit=5)

    # Users Top Artists:
    top_artists = sp.current_user_top_artists(limit=5)
    
    return top_tracks, top_artists


# Function to get Spotify access token
def get_spotify_token():
    body_params = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }
    response = requests.post('https://accounts.spotify.com/api/token', data=body_params)
    if response.status_code == 200:
        data = response.json()
        return data['access_token']
    return None

# Function to fetch track URI from Spotify API
def fetch_track_uri(track_name):
    token = get_spotify_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    params = {
        'q': track_name,
        'type': 'track,album',
        'limit': 1
    }
    response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['tracks']['items']:
            track_uri = data['tracks']['items'][0]['uri']
            return track_uri
    return None


def song_processing(track_name):
    result = sp.search(q=track_name, type='track', limit=1)
    features = sp.audio_features(result['tracks']['items'][0]['id'])[0]
    album_id = result['tracks']['items'][0]['album']['id']

    release_date = sp.album(album_id)['release_date']
    release_year = release_date.split('-')[0]

    explicit = int(result['tracks']['items'][0]['explicit'])
    bool_explicit = bool(explicit)

    counter = 0
    input_song = {}

    for i, v in (features.items()):
        counter += 1
        input_song.update({i: v})
        if counter == 11:
            break

    del input_song["key"]
    del input_song["mode"]

    input_song.update({"time_signature": features["time_signature"], "duration_ms": features["duration_ms"],
                    "key": features['key'],"year": release_year, "explicit": bool_explicit})

    return input_song


# def recommend_songs(song_name, n_recommendations=6):
#     # Load the dataset
#     df = pd.read_csv('./data/tracks_features.csv')

#     # Preprocess the dataset
#     # Normalize numerical features
#     scaler = MinMaxScaler()
#     numerical_features = ['danceability', 'energy', 'loudness', 'speechiness', 
#                           'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
#                           'time_signature', 'duration_ms',  'key', 'year']
#     df[numerical_features] = scaler.fit_transform(df[numerical_features])

#     # Convert 'explicit' to numerical
#     df['explicit'] = df['explicit'].astype(int)

#     # Extract the relevant features for similarity
#     features = numerical_features + ['explicit']
#     X = df[features]

#     # Use NearestNeighbors for approximate nearest neighbors
#     nn = NearestNeighbors(metric='cosine', algorithm='brute')
#     nn.fit(X)
    
#     input_song_df = pd.DataFrame([song_name], columns=numerical_features + ['explicit'])
#     input_song_df[numerical_features] = scaler.transform(input_song_df[numerical_features])
#     input_song_df['explicit'] = input_song_df['explicit'].astype(int)
#     input_song_features = input_song_df[features]

#     # Get the distances and indices of the nearest neighbors
#     distances, indices = nn.kneighbors(input_song_features, n_neighbors=n_recommendations+1)
    
#     # Exclude the first one as it will be the song itself
#     similar_indices = indices.flatten()[1:]
    
#     # Return the top n most similar songs
#     return df.iloc[similar_indices]


def recommend_songs(song_example, n_recommendations=6):
    # Load the dataset
    df = pd.read_csv('./data/tracks_features.csv')

    # Preprocess the dataset
    # Normalize numerical features
    scaler = MinMaxScaler()
    numerical_features = ['danceability', 'energy', 'loudness', 'speechiness', 
                          'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
                          'time_signature', 'duration_ms',  'key', 'year']
    df[numerical_features] = scaler.fit_transform(df[numerical_features])

    # Convert 'explicit' to numerical
    df['explicit'] = df['explicit'].astype(int)

    # Extract the relevant features for similarity
    features = numerical_features + ['explicit']
    X = df[features]

    # Use NearestNeighbors for approximate nearest neighbors
    nn = NearestNeighbors(metric='cosine', algorithm='brute')
    nn.fit(X)
    
    input_song_df = pd.DataFrame([song_example], columns=numerical_features + ['explicit'])
    input_song_df[numerical_features] = scaler.transform(input_song_df[numerical_features])
    input_song_df['explicit'] = input_song_df['explicit'].astype(int)
    input_song_features = input_song_df[features]

    # Get the distances and indices of the nearest neighbors
    distances, indices = nn.kneighbors(input_song_features, n_neighbors=n_recommendations+1)
    
    # Exclude the first one as it will be the song itself
    similar_indices = indices.flatten()[1:]
    
    # Explain the model using custom feature importance approach
    def calculate_similarity(X, nn, input_song_features, feature_index):
        X_permuted = X.copy()
        np.random.shuffle(X_permuted[:, feature_index])
        permuted_nn = NearestNeighbors(metric='cosine', algorithm='brute')
        permuted_nn.fit(X_permuted)
        permuted_distances, _ = permuted_nn.kneighbors(input_song_features, n_neighbors=n_recommendations+1)
        return permuted_distances
    
    base_distances = distances[0]
    feature_importance = []
    
    for i in range(len(features)):
        permuted_distances = calculate_similarity(X.values, nn, input_song_features.values, i)
        importance = np.mean(permuted_distances - base_distances)
        feature_importance.append(round(importance,4))
    
    feature_importance_df = pd.DataFrame({
        'feature': features,
        'importance': feature_importance
    }).sort_values(by='importance', ascending=False)

    # Return the top n most similar songs and the feature importance
    similar_songs = df.iloc[similar_indices]
    return similar_songs, feature_importance_df
