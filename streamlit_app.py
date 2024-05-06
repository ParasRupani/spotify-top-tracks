# import streamlit as st
# import spotipy
# import webbrowser
# from spotipy.oauth2 import SpotifyOAuth

# client_id = st.secrets["CLIENT_ID"]
# client_secret = st.secrets["CLIENT_SECRET"]
# redirect_uri = "https://spotify-user-tracks.streamlit.app/"  # Streamlit's default port

# # Set up Spotify authorization manager with Authorization Code Flow
# auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope="user-top-read", open_browser=False)

# spotify_token = None

# # Function to get top tracks and artists
# def get_top_data():
#     sp = spotipy.Spotify(auth_manager=auth_manager)
     
#     # Users Top Tracks:
#     top_tracks = sp.current_user_top_tracks(limit=5)

#     # Users Top Artists:
#     top_artists = sp.current_user_top_artists(limit=5)
    
#     return top_tracks, top_artists

# # Main function to run the app
# def main():
#     st.title("Your Tracks and Artists on Spotify")

#     # Add a button to initiate authentication
#     if "spotify_token_info" not in st.session_state:
#         global spotify_token
#         auth_url = auth_manager.get_authorize_url()
#         st.markdown(f'<a href="{auth_url}" target="_blank">Authenticate with Spotify</a>', unsafe_allow_html=True)
#         spotify_token = auth_manager.get_access_token(st.session.request_context.request.query_params.get("code"))["access_token"]

#     else:
#         # Get top tracks and artists if authentication is successful
#         tracks, artists = get_top_data()
        
#         # Display top tracks and artists side by side
#         col1, col2 = st.columns(2)

#         # Display top tracks
#         with col1:
#             st.subheader("Top 5 Tracks:")
#             for idx, track in enumerate(tracks['items'], start=1):
#                 truncated_title = truncate_title(track['name'])
#                 st.markdown(f"{idx}. [{truncated_title}]({track['external_urls']['spotify']})")

#         # Display top artists
#         with col2:
#             st.subheader("Top 5 Artists:")
#             for idx, artist in enumerate(artists['items'], start=1):
#                 st.write(f"{idx}. [{artist['name']}]({artist['external_urls']['spotify']})")

# # Run the app
# if __name__ == "__main__":
#     main()

import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.client import SpotifyException

client_id = st.secrets["CLIENT_ID"]
client_secret = st.secrets["CLIENT_SECRET"]

# Set up Spotify authorization manager with Authorization Code Flow
redirect_uri = "https://spotify-user-tracks.streamlit.app/"
auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope="user-top-read", open_browser=False)

# Function to get top tracks and artists
def get_top_data():
    try:
        sp = spotipy.Spotify(auth_manager=auth_manager)
        # Users Top Tracks:
        top_tracks = sp.current_user_top_tracks(limit=5)

        # Users Top Artists:
        top_artists = sp.current_user_top_artists(limit=5)
        
        return top_tracks, top_artists
    except SpotifyException as e:
        st.error("Authentication failed. Please authenticate with Spotify.")
        st.error(f"Error code: {e.http_status}, Reason: {e.msg}")
        return None, None

# Main function to run the app
def main():
    st.title("Your Tracks and Artists on Spotify")

    # Get top tracks and artists
    tracks, artists = get_top_data()
    
    if tracks is not None and artists is not None:
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
    else:
        authenticate()

# Function to authenticate with Spotify
def authenticate():
    auth_url = auth_manager.get_authorize_url()
    st.markdown(f'<script>window.open("{auth_url}", "_blank");</script>', unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()
