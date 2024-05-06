import http.server
import socketserver
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import urllib.parse
import webbrowser
from dotenv import dotenv_values


# Set up Spotify API credentials
secrets = dotenv_values(".env")
client_id, client_secret = secrets.values()

redirect_uri = "http://localhost:8000/callback"
scope = "user-top-read"

# Set up Spotify authorization manager
auth_manager = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope
)

# Handler for HTTP requests
class CallbackHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if "code" in self.path:
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            authorization_code = params["code"][0]  # Extract the authorization code from the URL
            token_info = auth_manager.get_access_token(authorization_code)
            sp = spotipy.Spotify(auth=token_info['access_token'])

            # Retrieve user's top 10 tracks
            top_tracks = sp.current_user_top_tracks(limit=10)
            tracks_html = "<h2>Top 10 Tracks:</h2>"
            for idx, track in enumerate(top_tracks['items'], start=1):
                tracks_html += f"<p>{idx}. <a href='{track['external_urls']['spotify']}'>{track['name']}</a> - {', '.join(artist['name'] for artist in track['artists'])}</p>"

            # Retrieve user's top 5 artists
            top_artists = sp.current_user_top_artists(limit=5)
            artists_html = "<h2>Top 5 Artists:</h2>"
            for idx, artist in enumerate(top_artists['items'], start=1):
                artists_html += f"<p>{idx}. <a href='{artist['external_urls']['spotify']}'>{artist['name']}</a></p>"

            # HTML response to display top tracks and artists
            response_html = f"""
            <html>
                <head><title>Authorization successful!</title></head>
                <body>
                    <h1>Authorization successful!</h1>
                    {tracks_html}
                    {artists_html}
                </body>
            </html>
            """

            # Send response to browser
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(response_html.encode())
        else:
            # Send error response to browser
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Error: Authorization code not found in URL.</h1></body></html>')


# Start local HTTP server
def start_server():
    port = 8000
    while True:
        try:
            server_address = ('', port)
            httpd = socketserver.TCPServer(server_address, CallbackHandler)
            print(f"HTTP server is running on port {port}...")
            print("Please log in to your Spotify account and authorize the application:")
            auth_url = auth_manager.get_authorize_url()
            print(auth_url)
            webbrowser.open(auth_url, new=2)  # Open in new tab
            httpd.serve_forever()
        except OSError as e:
            if e.errno == 48:  # Address already in use
                port += 1
            else:
                raise


# Main function
def main():
    start_server()

if __name__ == "__main__":
    main()
