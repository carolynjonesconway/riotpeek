# from lol_gradiusbot.libs.xmppbot import Xmppbot
from os import environ
import requests

RIOT_KEY = environ['RIOT_API_KEY']

########################################
# Chatbot Setup

# user = environ['user']
# passwd = environ['passwd']
# region = environ['region']
# owner = environ['owner']
# bot = Xmppbot(user, passwd, region, owner)
# bot.connect()
# bot.bulk_load_plugins(plugins)
# bot.join_muc_room("general discussion")
# bot.leave_muc_room("testgradius")
# bot.join_muc_room("testgradius")

########################################

class Riotpy(object):

	def __init__(self, api_key, region='na', platform='NA1'):
		self.api_key = api_key
		self.region = region
		self.platform = platform

	def get_summoner_ids(self, names):
		"""Given a list of names, returns a list of summoner ids, in the same order

			>>> rp.get_summoner_ids(['icegirl2163', 'iceman2163'])
			[43265218, 22685864]

		"""

		names_str = ','.join(names)
		url = 'https://{0}.api.pvp.net/api/lol/{0}/v1.4/summoner/by-name/{1}?api_key={2}'.format(self.region, names_str, self.api_key)
		response = requests.get(url).json()

		ids = [response[name]['id'] for name in names]
		return ids

	def get_summoner_id(self, name):
		"""Given a single summoner name, returns that summoner's id

			>>> rp.get_summoner_id('icegirl2163')
			43265218

		"""
		url = 'https://{0}.api.pvp.net/api/lol/{0}/v1.4/summoner/by-name/{1}?api_key={2}'.format(self.region, name, self.api_key)
		try:
			response = requests.get(url).json()
			return response[name]['id']
		except:
			return None


	def get_current_game(self, summoner_id):
		"""Returns the entire JSON object representing the current game"""
		
		url = "https://{0}.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/{1}/{2}?api_key={3}".format(self.region, self.platform, summoner_id, self.api_key)
		try:
			response = requests.get(url).json()
			return response
		except ValueError:
			return None


rp = Riotpy(RIOT_KEY)