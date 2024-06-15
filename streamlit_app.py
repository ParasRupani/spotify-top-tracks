import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
# from dotenv import dotenv_values

from helper import truncate_title, get_top_data, fetch_track_uri
from helper import song_processing, recommend_songs

# Set up Spotify API credentials
# secrets = dotenv_values(".env")
# client_id, client_secret = secrets.values()

# Loading Streamlit Secrets
client_id, client_secret = st.secrets()

# Set up Spotify authorization manager with Client Credentials Flow
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

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
        
# Run the app
if __name__ == "__main__":
    main()
