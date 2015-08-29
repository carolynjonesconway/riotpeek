import requests
from os import environ

RIOT_KEY = environ['RIOT_API_KEY']

class Riotpy(object):

	def __init__(self, api_key, region='na'):
		self.api_key = api_key
		self.region = region

	def get_summoner_ids(self, names):
		"""Given a list of names, returns a list of summoner ids, in the same order

			>>> rp.get_summoner_ids(['icegirl2163', 'iceman2163'])
			[43265218, 22685864]

		"""

		names_str = ','.join(names)
		url = 'https://{}.api.pvp.net/api/lol/na/v1.4/summoner/by-name/{}?api_key={}'.format(self.region, names_str, self.api_key)
		response = requests.get(url).json()

		ids = [response[name]['id'] for name in names]
		return ids

	def get_summoner_id(self, name):
		"""Given a single summoner name, returns that summoner's id

			>>> rp.get_summoner_id('icegirl2163')
			43265218

		"""
		url = 'https://{}.api.pvp.net/api/lol/na/v1.4/summoner/by-name/{}?api_key={}'.format(self.region, name, self.api_key)
		try:
			response = requests.get(url).json()
			return response[name]['id']
		except KeyError:
			return None


	def get_current_game(self, summoner_id):
		"""Returns the entire JSON object representing the current game"""
		
		url = "https://{}.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/NA1/{}?api_key={}".format(self.region, summoner_id, self.api_key)
		try:
			response = requests.get(url).json()
			return response
		except ValueError:
			return None


rp = Riotpy(RIOT_KEY)