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
		self.summoners = {'icegirl2163':43265218,
						  'iceman2163':22685864}

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


		This decreases the number of requests by storing info.

			>>> rp.get_summoner_id('icegirl2163')
			43265218

		"""
		name = name.lower()

		if name in self.summoners:
			return summoners[name]

		else:
			url = 'https://{0}.api.pvp.net/api/lol/{0}/v1.4/summoner/by-name/{1}?api_key={2}'.format(self.region, name, self.api_key)
			try:
				response = requests.get(url).json()
				summoners[name] = response[name]['id']
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

champs = {1: 'Annie', 2: 'Olaf', 3: 'Galio', 4: 'Twisted Fate', 5: 'Xin Zhao', 6: 'Urgot', 7: 'LeBlanc', 8: 'Vladimir', 9: 'Fiddlesticks', 10: 'Kayle', 11: 'Master Yi', 12: 'Alistar', 13: 'Ryze', 14: 'Sion', 15: 'Sivir', 16: 'Soraka', 17: 'Teemo', 18: 'Tristana', 19: 'Warwick', 20: 'Nunu', 21: 'Miss Fortune', 22: 'Ashe', 23: 'Tryndamere', 24: 'Jax', 25: 'Morgana', 26: 'Zilean', 27: 'Singed', 28: 'Evelynn', 29: 'Twitch', 30: 'Karthus', 31: "Cho'Gath", 32: 'Amumu', 33: 'Rammus', 34: 'Anivia', 35: 'Shaco', 36: 'Dr. Mundo', 37: 'Sona', 38: 'Kassadin', 39: 'Irelia', 40: 'Janna', 41: 'Gangplank', 42: 'Corki', 43: 'Karma', 44: 'Taric', 45: 'Veigar', 48: 'Trundle', 50: 'Swain', 51: 'Caitlyn', 53: 'Blitzcrank', 54: 'Malphite', 55: 'Katarina', 56: 'Nocturne', 57: 'Maokai', 58: 'Renekton', 59: 'Jarvan IV', 60: 'Elise', 61: 'Orianna', 62: 'Wukong', 63: 'Brand', 64: 'Lee Sin', 67: 'Vayne', 68: 'Rumble', 69: 'Cassiopeia', 72: 'Skarner', 74: 'Heimerdinger', 75: 'Nasus', 76: 'Nidalee', 77: 'Udyr', 78: 'Poppy', 79: 'Gragas', 80: 'Pantheon', 81: 'Ezreal', 82: 'Mordekaiser', 83: 'Yorick', 84: 'Akali', 85: 'Kennen', 86: 'Garen', 89: 'Leona', 90: 'Malzahar', 91: 'Talon', 92: 'Riven', 96: "Kog'Maw", 98: 'Shen', 99: 'Lux', 101: 'Xerath', 102: 'Shyvana', 103: 'Ahri', 104: 'Graves', 105: 'Fizz', 106: 'Volibear', 107: 'Rengar', 110: 'Varus', 111: 'Nautilus', 112: 'Viktor', 113: 'Sejuani', 114: 'Fiora', 115: 'Ziggs', 117: 'Lulu', 119: 'Draven', 120: 'Hecarim', 121: "Kha'Zix", 122: 'Darius', 126: 'Jayce', 127: 'Lissandra', 131: 'Diana', 133: 'Quinn', 134: 'Syndra', 143: 'Zyra', 150: 'Gnar', 154: 'Zac', 157: 'Yasuo', 161: "Vel'Koz", 201: 'Braum', 222: 'Jinx', 236: 'Lucian', 238: 'Zed', 254: 'Vi', 266: 'Aatrox', 267: 'Nami', 268: 'Azir', 412: 'Thresh', 421: "Rek'Sai", 429: 'Kalista'}
ranked = [4, 6, 9, 41, 42]