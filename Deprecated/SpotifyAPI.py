#This entire class is a mistake and I hate myself
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import datetime
import base64
import requests
import string
import secrets
import json
from urllib.parse import urlencode

class SpotifyAPI(object):
	access_token = None
	access_token_expires =  datetime.datetime.now()
	access_token_did_expire = True
	client_id = None
	client_secret = None
	authorize_url = "https://accounts.spotify.com/authorize"
	token_url = "https://accounts.spotify.com/api/token"
	player_url = "https://api.spotify.com/v1/me/player"
	next_url = "https://api.spotify.com/v1/me/player/next"
	play_url = "https://api.spotify.com/v1/me/player/play"
	pause_url = "https://api.spotify.com/v1/me/player/pause"
	redirect_uri = "http://localhost:8888/callback"
	scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing"
	sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))

	def __init__(self, client_id, client_secret, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.client_id = client_id
		self.client_secret = client_secret

	def get_client_credtials(self):
		"""
		Returns a base64 encoded string
		"""
		client_id = self.client_id
		client_secret = self.client_secret
		if client_secret == None or client_id == None:
			raise Exception("You must set client_id and client_secret")

		client_creds = f"{client_id}:{client_secret}"
		client_creds_b64 = base64.b64encode(client_creds.encode())
		
		return client_creds_b64.decode()

	def get_token_headers(self):
		client_creds_b64 = self.get_client_credtials()
		return {
			"Authorization": f"Basic {client_creds_b64}"
		}

	def get_token_data(self):
		return {
			"grant_type": "client_credentials"
		}

	def login(self):
		state = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))
		authorize_url = self.authorize_url
		redirect_uri = self.redirect_uri
		response_type = 'code'
		client_id = self.client_id
		scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing"
		headers = {
			"client_id": client_id,
			"response_type": response_type,
			"redirect_uri": redirect_uri,
			"scope": scope,
		}
		url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in headers.items()])
		auth_url = "{}/?{}".format(authorize_url, url_args)
		return redirect(auth_url)
		#r = make_response(redirect(f'{authorize_url}/?{urlencode(headers)}'))
		#r.set_cookie('spotify_auth_state', state)
		
		#return r

	def callback():
		error = request.args.get('error')

	def perform_auth(self):
		token_url = self.token_url
		token_data = self.get_token_data()
		token_headers = self.get_token_headers()
		r = requests.post(token_url, data=token_data, headers=token_headers)
		valid_request = r.status_code in range(200,299)
		if(not valid_request):
			return False
		data = r.json()
		access_token = data['access_token']
		now = datetime.datetime.now()
		expires_in = data['expires_in']#seconds
		expires = now + datetime.timedelta(seconds=expires_in)
		self.access_token = access_token
		self.access_token_expires = expires
		self.access_token_did_expire = expires < now
		did_expire = expires < now
		return True

	def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token() 
        return token

    def get_resource_header(self):
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers

    def skip_to_next_track(self):
    	access_token = self.get_access_token()
    	headers = get_resource_header()
   		r=requests.post(next_url, headers=headers)
   		if r.status_code in range (200,299):
   			return True
   		return False

    def pause_player(self):
    	access_token = self.get_access_token()

    def start_player(self):
    	access_token = self.get_access_token()
