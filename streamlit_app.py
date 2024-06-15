import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
# from dotenv import dotenv_values

import pandas as pd, numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
import eli5
from eli5.sklearn import PermutationImportance

# Set up Spotify API credentials
# secrets = dotenv_values(".env")
# client_id, client_secret = secrets.values()

# Loading Streamlit Secrets
client_id = st.secrets["CLIENT_ID"]
client_secret = st.secrets["CLIENT_SECRET"]

# Set up Spotify authorization manager with Client Credentials Flow
# auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

redirect_uri = "https://top-spotify-tracks.streamlit.app/"

# Set up Spotify authorization manager with Authorization Code Flow
auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope="user-top-read", open_browser=False)

# Main function to run the app
def main():
    st.title("Your Tracks and Artists on Spotify")
    
    # Get top tracks and artists
    tracks, artists = get_top_data()
    
    # Display top tracks and artists side by side
    col1, col2 = st.columns(2)

    titles = [track['name'] for track in tracks['items']]

    # Display top tracks
    with col1:
        st.subheader("Top 5 Tracks:")
        for idx, track in enumerate(tracks['items'], start=1):
            truncated_title = truncate_title(track['name'])
            st.markdown(f"{idx}. [{truncated_title}]({track['external_urls']['spotify']})")

    # Display top artists
    with col2:
        st.subheader("Top 5 Artists:")
        for idx, artist in enumerate(artists['items'], start=1):
            st.write(f"{idx}. [{artist['name']}]({artist['external_urls']['spotify']})")

    sp = spotipy.Spotify(auth_manager=auth_manager)

    st.write("")

    # Select a track to generate recommendations
    selected_option = st.selectbox('Generate Similar Songs:', titles)

    if st.button('Process'):
    # Action to perform when the button is clicked
        st.write('Processing...')

        input_song = song_processing(selected_option)
        
        # recommended_songs = recommend_songs(((input_song)))
        recommended_songs, explanation = recommend_songs(input_song, n_recommendations=6)
        # print(recommended_songs)
        print(explanation)

        recommended_songs["artists"] = recommended_songs["artists"].apply(lambda x: x.replace("[", "").replace("]", "").replace("'", ""))

        # st.write((recommended_songs[['name', 'album', 'artists']]))

        q0 = recommended_songs['name'].iloc[0] + " " + recommended_songs['artists'].iloc[0]
        q1 = recommended_songs['name'].iloc[1] + " " + recommended_songs['artists'].iloc[1]
        q2 = recommended_songs['name'].iloc[2] + " " + recommended_songs['artists'].iloc[2]
        q3 = recommended_songs['name'].iloc[3] + " " + recommended_songs['artists'].iloc[3]
        q4 = recommended_songs['name'].iloc[4] + " " + recommended_songs['artists'].iloc[4]
        q5 = recommended_songs['name'].iloc[5] + " " + recommended_songs['artists'].iloc[5]

        track_uri_0 = fetch_track_uri(q0)
        track_uri_1 = fetch_track_uri(q1)
        track_uri_2 = fetch_track_uri(q2)
        track_uri_3 = fetch_track_uri(q3)
        track_uri_4 = fetch_track_uri(q4)
        track_uri_5 = fetch_track_uri(q5)
        
        st.write("Listen to the recommendations below:")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f'<iframe src="https://open.spotify.com/embed/track/{track_uri_0.split(":")[2]}" style="width: 100%; border-radius: 15px; height: 80px; min-height: 10px; top-margin:10px; overflow: hidden;" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)    
            st.write("")
            
            st.write(f'<iframe src="https://open.spotify.com/embed/track/{track_uri_1.split(":")[2]}" style="width: 100%; border-radius: 15px; height: 80px; min-height: 10px; overflow: hidden;" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)    
            st.write("")
            
            st.write(f'<iframe src="https://open.spotify.com/embed/track/{track_uri_2.split(":")[2]}" style="width: 100%; border-radius: 15px; height: 80px; min-height: 10px; overflow: hidden;" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)

        with col2:
            st.write(f'<iframe src="https://open.spotify.com/embed/track/{track_uri_3.split(":")[2]}" style="width: 100%; border-radius: 15px; height: 80px; min-height: 10px; top-margin:10px; overflow: hidden;" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)    
            st.write("")
            
            st.write(f'<iframe src="https://open.spotify.com/embed/track/{track_uri_4.split(":")[2]}" style="width: 100%; border-radius: 15px; height: 80px; min-height: 10px; overflow: hidden;" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)    
            st.write("")
            
            st.write(f'<iframe src="https://open.spotify.com/embed/track/{track_uri_5.split(":")[2]}" style="width: 100%; border-radius: 15px; height: 80px; min-height: 10px; overflow: hidden;" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)

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

# Run the app
if __name__ == "__main__":
    main()
