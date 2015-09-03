# from lol_gradiusbot.libs.xmppbot import Xmppbot
from os import environ
import requests

RIOT_KEY = environ['RIOT_API_KEY']


class Riotpy(object):

	def __init__(self, api_key, region='na', platform='NA1'):
		self.api_key = api_key
		self.region = region
		self.platform = platform
		self.summoners = {'prohibit': 19936601, 'bruds': 19723956, 'mateeen': 21335177, 'icegirl2163': 43265218, 'charlimir': 67992136, 'iceman2163': 22685864, 'lolz2244': 33460853, 'japanman': 55963358, 'gunshymonkey': 39561509}
		self.champs = self.load_champions()
		self.ranked_ids = [4, 6, 9, 41, 42]

	def load_champions(self):
		"""Returns a dictionary of all the champions"""

		url = "https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion?dataById=true&api_key={}".format(self.api_key)
		champs = requests.get(url).json()['data']
		return champs

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
			return self.summoners[name]

		else:
			url = 'https://{0}.api.pvp.net/api/lol/{0}/v1.4/summoner/by-name/{1}?api_key={2}'.format(self.region, name, self.api_key)
			try:
				response = requests.get(url).json()
				self.summoners[name] = response[name]['id']
				return response[name]['id']
			except:
				return None


	def get_current_game_info(self, summoner_name):

		summoner_id = riot.get_summoner_id(summoner_name)

		url = "https://{0}.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/{1}/{2}?api_key={3}".format(self.region, self.platform, summoner_id, self.api_key)
		response = requests.get(url)
		try:
			game = response.json()
		except:
		# 	game = None
		# 	print dir(response), "No game found."
			return response

		game_stats = {'summonerId': summoner_id,
				  'game': {'teamOne':[],
						   'teamTwo':[],
						   'startTime': None,
						   'gameType': None
						   }
				  }

		if game:
			# Check if the game is ranked
			if int(game['gameQueueConfigId']) in self.ranked_ids:
				game_type = 'ranked'
			else:
				game_type = 'normal'

			# Set the game type & start time
			game_stats['startTime'] = float(game['gameStartTime'])/1000
			game_stats['gameType'] = game_type	   

			team_one_id = game['participants'][0]['teamId']

			# Add participant details to each team
			for participant in game['participants']:
				riot.summoners[participant['summonerName']] = participant['summonerId'] # Store their info to reduce API calls later!

				win_rate = riot.get_win_rate(participant['summonerId'], participant['championId'])
				if win_rate:
					win_rate = int(win_rate * 100)

				champ_id = str(participant['championId'])

				participant_info = {'summonerName': participant['summonerName'],
									'champName': self.champs[champ_id]['name'],
									'winRate': win_rate
									}

				if participant['teamId'] == team_one_id:
					game_stats['game']['teamOne'].append(participant_info)
				else:
					game_stats['game']['teamTwo'].append(participant_info)

		return game_stats

			

	def get_win_rate(self, summoner_id, champion_id):
		"""Returns a summoner's win rate on a given champ

		If the summoner has no ranked games on that champ, returns None.
		"""

		url = "https://{0}.api.pvp.net/api/lol/{0}/v1.3/stats/by-summoner/{1}/ranked/?api_key={2}".format(self.region, summoner_id, self.api_key)
		
		try:
			response = requests.get(url).json()
			champs = response['champions']

			# Find their win rate with this champ
			for champ in champs:
				if int(champ['id']) == int(champion_id):
					games_won = float(champ['stats']['totalSessionsWon'])
					games_played = float(champ['stats']['totalSessionsPlayed'])

					if games_played:
						win_rate = games_won/games_played
						return win_rate

			# If they have never played this champ in ranked, return None
		except:
			return


class TextMessage(object):

	def __init__(self, sms):
		self.sms = sms

	def parse_command(self):
		"""Determines what command was used"""

		pass

	def find_game(self):
		"""Finds a game for the requested summoner"""

		pass

	def nickname_summoner(self):
		"""Assigns a nickname to a given summoner"""

		pass

riot = Riotpy(RIOT_KEY)























