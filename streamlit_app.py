import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# from dotenv import dotenv_values
# # Set up Spotify API credentials
# secrets = dotenv_values(".env")
# client_id, client_secret = secrets.values()

# Loading Streamlit Secrets
client_id, client_secret = st.secrets["CLIENT_ID", "CLIENT_SECRET"]

# Set up Spotify authorization manager with Client Credentials Flow
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

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

# Main function to run the app
def main():
    st.title("Your Tracks and Artists on Spotify")
    
    # Get top tracks and artists
    tracks, artists = get_top_data()
    
    # Display top tracks and artists side by side
    col1, col2 = st.columns(2)

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

# Run the app
if __name__ == "__main__":
    main()
