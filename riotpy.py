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
		self.champs = self.load_champions() # FIXME: An API call is only necessary when a new champ is released. Can we improve this update method?
		# self.champs = champs
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

		url = "https://{0}.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/{1}/{2}/?api_key={3}".format(self.region, self.platform, summoner_id, self.api_key)
		response = requests.get(url)
		
		game_stats = {'summonerId': summoner_id,
				  'game': {'teamOne':[],
						   'teamTwo':[],
						   'startTime': None,
						   'gameType': None
						   }
				  }

		# Check if a game was found
		if int(response.status_code) != 200:
			print '\n\nStatusCode: {}\nURL: {}\nSummoner: {} ({})\n\n'.format(response.status_code, url, summoner_name, summoner_id)
			return game_stats

		game = response.json()

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

# FIXME: Setup tests for ALLLL of this!
class TextMessage(object):

	# FIXME: Does it actually make sense to pass in a riotpy_instance?
	def __init__(self, sms, riotpy_instance):
		self.sms = sms
		self.riot = riotpy_instance

		self.parse_command()


	def generate_response(self):
		"""Determines the correct response based on SMS content"""

		if self.command == 'invalid':
			response = "Invalid command."

		if self.command == 'find':
			response = self.find_response()
			
		elif self.command == 'nickname':
			response = self.nickname_response()

		return response


	def find_response(self):
		"""Finds a game for the requested summoner, and returns a success string"""

		if self.summoner:
			game_stats = self.riot.get_current_game_info(self.summoner)
			print "Game Stats: ", game_stats
			game = game_stats['game']

			if game:
				# Determine game duration
				start_epoch = float(game['gameStartTime'])/1000
				start = datetime.fromtimestamp(start_epoch)
				duration = datetime.now() - start
				total_minutes = int(duration.total_seconds()/60)

				# Determine champion
				champ_id = None
				for player in game['teamOne']:
					if player['summonerId'] == game_stats['summonerId']:
						champ_id = player['championId']
						champ_name = self.riot.champs[champ_id]
						break

				if not champ_id:
					for player in game['teamTwo']:
						if player['summonerId'] == game_stats['summonerId']:
							champ_id = player['championId']
							champ_name = self.riot.champs[champ_id]
							break

				# Set response
				response = "{0} has been in a {1} game as {2} for {3} minutes.".format(self.summoner, game['gameType'], champ_name, total_minutes)
			
			elif not game:
				response = "{0} is not currently in game.".format(self.summoner)
		
		elif not self.summoner:
			response = "Oops! We couldn't tell who you wanted us to find."

		return response


	def nickname_response(self):
		"""Assigns a nickname to a given summoner, and returns a success string"""

		pass


	def parse_command(self):
		"""Determines what command was used"""

		self.content = self.sms['Body'].strip().lower().split()
		command = self.content[0].lower()

		if command == 'find':
			self.command = command
			if len(self.content) == 2:
				self.summoner = self.content[1]

		elif command == 'nickname':
			self.command = command
			if len(self.content) == 4:
				self.nickname = [1]
				self.summoner = content[3]

		else:
			print self.content[0].lower()
			self.command = 'invalid'


riot = Riotpy(RIOT_KEY)
champs = {"35":{"id":35,
				"key":"Shaco",
				"name":"Shaco",
				"title":"the Demon Jester"},
		  "36":{"id":36,
		  		"key":"DrMundo",
		  		"name":"Dr. Mundo",
		  		"title":"the Madman of Zaun"},
		  "33":{"id":33,
		  		"key":"Rammus",
		  		"name":"Rammus",
		  		"title":"the Armordillo"},
		  "34":{"id":34,
		  		"key":"Anivia",
		  		"name":"Anivia",
		  		"title":"the Cryophoenix"},
		  "157":{"id":157,
		  		 "key":"Yasuo",
		  		 "name":"Yasuo",
		  		 "title":"the Unforgiven"},
		  "39":{"id":39,
		  		"key":"Irelia",
		  		"name":"Irelia",
		  		"title":"the Will of the Blades"},
		  "37":{"id":37,
		  		"key":"Sona",
		  		"name":"Sona",
		  		"title":"Maven of the Strings"},
		  "154":{"id":154,
		  		 "key":"Zac",
		  		 "name":"Zac",
		  		 "title":"the Secret Weapon"},
		  "38":{"id":38,"key":"Kassadin","name":"Kassadin","title":"the Void Walker"},"150":{"id":150,"key":"Gnar","name":"Gnar","title":"the Missing Link"},"43":{"id":43,"key":"Karma","name":"Karma","title":"the Enlightened One"},"42":{"id":42,"key":"Corki","name":"Corki","title":"the Daring Bombardier"},"41":{"id":41,"key":"Gangplank","name":"Gangplank","title":"the Saltwater Scourge"},"40":{"id":40,"key":"Janna","name":"Janna","title":"the Storm's Fury"},"201":{"id":201,"key":"Braum","name":"Braum","title":"the Heart of the Freljord"},"22":{"id":22,"key":"Ashe","name":"Ashe","title":"the Frost Archer"},"23":{"id":23,"key":"Tryndamere","name":"Tryndamere","title":"the Barbarian King"},"24":{"id":24,"key":"Jax","name":"Jax","title":"Grandmaster at Arms"},"25":{"id":25,"key":"Morgana","name":"Morgana","title":"Fallen Angel"},"26":{"id":26,"key":"Zilean","name":"Zilean","title":"the Chronokeeper"},"27":{"id":27,"key":"Singed","name":"Singed","title":"the Mad Chemist"},"28":{"id":28,"key":"Evelynn","name":"Evelynn","title":"the Widowmaker"},"29":{"id":29,"key":"Twitch","name":"Twitch","title":"the Plague Rat"},"161":{"id":161,"key":"Velkoz","name":"Vel'Koz","title":"the Eye of the Void"},"3":{"id":3,"key":"Galio","name":"Galio","title":"the Sentinel's Sorrow"},"2":{"id":2,"key":"Olaf","name":"Olaf","title":"the Berserker"},"1":{"id":1,"key":"Annie","name":"Annie","title":"the Dark Child"},"30":{"id":30,"key":"Karthus","name":"Karthus","title":"the Deathsinger"},"7":{"id":7,"key":"Leblanc","name":"LeBlanc","title":"the Deceiver"},"6":{"id":6,"key":"Urgot","name":"Urgot","title":"the Headsman's Pride"},"5":{"id":5,"key":"XinZhao","name":"Xin Zhao","title":"the Seneschal of Demacia"},"32":{"id":32,"key":"Amumu","name":"Amumu","title":"the Sad Mummy"},"4":{"id":4,"key":"TwistedFate","name":"Twisted Fate","title":"the Card Master"},"31":{"id":31,"key":"Chogath","name":"Cho'Gath","title":"the Terror of the Void"},"9":{"id":9,"key":"FiddleSticks","name":"Fiddlesticks","title":"the Harbinger of Doom"},"8":{"id":8,"key":"Vladimir","name":"Vladimir","title":"the Crimson Reaper"},"19":{"id":19,"key":"Warwick","name":"Warwick","title":"the Blood Hunter"},"17":{"id":17,"key":"Teemo","name":"Teemo","title":"the Swift Scout"},"18":{"id":18,"key":"Tristana","name":"Tristana","title":"the Yordle Gunner"},"15":{"id":15,"key":"Sivir","name":"Sivir","title":"the Battle Mistress"},"16":{"id":16,"key":"Soraka","name":"Soraka","title":"the Starchild"},"13":{"id":13,"key":"Ryze","name":"Ryze","title":"the Rogue Mage"},"14":{"id":14,"key":"Sion","name":"Sion","title":"The Undead Juggernaut"},"11":{"id":11,"key":"MasterYi","name":"Master Yi","title":"the Wuju Bladesman"},"12":{"id":12,"key":"Alistar","name":"Alistar","title":"the Minotaur"},"21":{"id":21,"key":"MissFortune","name":"Miss Fortune","title":"the Bounty Hunter"},"20":{"id":20,"key":"Nunu","name":"Nunu","title":"the Yeti Rider"},"107":{"id":107,"key":"Rengar","name":"Rengar","title":"the Pridestalker"},"106":{"id":106,"key":"Volibear","name":"Volibear","title":"the Thunder's Roar"},"105":{"id":105,"key":"Fizz","name":"Fizz","title":"the Tidal Trickster"},"104":{"id":104,"key":"Graves","name":"Graves","title":"the Outlaw"},"103":{"id":103,"key":"Ahri","name":"Ahri","title":"the Nine-Tailed Fox"},"99":{"id":99,"key":"Lux","name":"Lux","title":"the Lady of Luminosity"},"102":{"id":102,"key":"Shyvana","name":"Shyvana","title":"the Half-Dragon"},"101":{"id":101,"key":"Xerath","name":"Xerath","title":"the Magus Ascendant"},"412":{"id":412,"key":"Thresh","name":"Thresh","title":"the Chain Warden"},"98":{"id":98,"key":"Shen","name":"Shen","title":"Eye of Twilight"},"222":{"id":222,"key":"Jinx","name":"Jinx","title":"the Loose Cannon"},"96":{"id":96,"key":"KogMaw","name":"Kog'Maw","title":"the Mouth of the Abyss"},"223":{"id":223,"key":"TahmKench","name":"Tahm Kench","title":"the River King"},"92":{"id":92,"key":"Riven","name":"Riven","title":"the Exile"},"91":{"id":91,"key":"Talon","name":"Talon","title":"the Blade's Shadow"},"90":{"id":90,"key":"Malzahar","name":"Malzahar","title":"the Prophet of the Void"},"429":{"id":429,"key":"Kalista","name":"Kalista","title":"the Spear of Vengeance"},"10":{"id":10,"key":"Kayle","name":"Kayle","title":"The Judicator"},"421":{"id":421,"key":"RekSai","name":"Rek'Sai","title":"the Void Burrower"},"89":{"id":89,"key":"Leona","name":"Leona","title":"the Radiant Dawn"},"79":{"id":79,"key":"Gragas","name":"Gragas","title":"the Rabble Rouser"},"117":{"id":117,"key":"Lulu","name":"Lulu","title":"the Fae Sorceress"},"114":{"id":114,"key":"Fiora","name":"Fiora","title":"the Grand Duelist"},"78":{"id":78,"key":"Poppy","name":"Poppy","title":"the Iron Ambassador"},"115":{"id":115,"key":"Ziggs","name":"Ziggs","title":"the Hexplosives Expert"},"77":{"id":77,"key":"Udyr","name":"Udyr","title":"the Spirit Walker"},"112":{"id":112,"key":"Viktor","name":"Viktor","title":"the Machine Herald"},"113":{"id":113,"key":"Sejuani","name":"Sejuani","title":"the Winter's Wrath"},"110":{"id":110,"key":"Varus","name":"Varus","title":"the Arrow of Retribution"},"111":{"id":111,"key":"Nautilus","name":"Nautilus","title":"the Titan of the Depths"},"119":{"id":119,"key":"Draven","name":"Draven","title":"the Glorious Executioner"},"432":{"id":432,"key":"Bard","name":"Bard","title":"the Wandering Caretaker"},"245":{"id":245,"key":"Ekko","name":"Ekko","title":"the Boy Who Shattered Time"},"82":{"id":82,"key":"Mordekaiser","name":"Mordekaiser","title":"the Master of Metal"},"83":{"id":83,"key":"Yorick","name":"Yorick","title":"the Gravedigger"},"80":{"id":80,"key":"Pantheon","name":"Pantheon","title":"the Artisan of War"},"81":{"id":81,"key":"Ezreal","name":"Ezreal","title":"the Prodigal Explorer"},"86":{"id":86,"key":"Garen","name":"Garen","title":"The Might of Demacia"},"84":{"id":84,"key":"Akali","name":"Akali","title":"the Fist of Shadow"},"85":{"id":85,"key":"Kennen","name":"Kennen","title":"the Heart of the Tempest"},"67":{"id":67,"key":"Vayne","name":"Vayne","title":"the Night Hunter"},"126":{"id":126,"key":"Jayce","name":"Jayce","title":"the Defender of Tomorrow"},"69":{"id":69,"key":"Cassiopeia","name":"Cassiopeia","title":"the Serpent's Embrace"},"127":{"id":127,"key":"Lissandra","name":"Lissandra","title":"the Ice Witch"},"68":{"id":68,"key":"Rumble","name":"Rumble","title":"the Mechanized Menace"},"121":{"id":121,"key":"Khazix","name":"Kha'Zix","title":"the Voidreaver"},"122":{"id":122,"key":"Darius","name":"Darius","title":"the Hand of Noxus"},"120":{"id":120,"key":"Hecarim","name":"Hecarim","title":"the Shadow of War"},"72":{"id":72,"key":"Skarner","name":"Skarner","title":"the Crystal Vanguard"},"236":{"id":236,"key":"Lucian","name":"Lucian","title":"the Purifier"},"74":{"id":74,"key":"Heimerdinger","name":"Heimerdinger","title":"the Revered Inventor"},"238":{"id":238,"key":"Zed","name":"Zed","title":"the Master of Shadows"},"75":{"id":75,"key":"Nasus","name":"Nasus","title":"the Curator of the Sands"},"76":{"id":76,"key":"Nidalee","name":"Nidalee","title":"the Bestial Huntress"},"134":{"id":134,"key":"Syndra","name":"Syndra","title":"the Dark Sovereign"},"59":{"id":59,"key":"JarvanIV","name":"Jarvan IV","title":"the Exemplar of Demacia"},"133":{"id":133,"key":"Quinn","name":"Quinn","title":"Demacia's Wings"},"58":{"id":58,"key":"Renekton","name":"Renekton","title":"the Butcher of the Sands"},"57":{"id":57,"key":"Maokai","name":"Maokai","title":"the Twisted Treant"},"56":{"id":56,"key":"Nocturne","name":"Nocturne","title":"the Eternal Nightmare"},"55":{"id":55,"key":"Katarina","name":"Katarina","title":"the Sinister Blade"},"64":{"id":64,"key":"LeeSin","name":"Lee Sin","title":"the Blind Monk"},"62":{"id":62,"key":"MonkeyKing","name":"Wukong","title":"the Monkey King"},"268":{"id":268,"key":"Azir","name":"Azir","title":"the Emperor of the Sands"},"63":{"id":63,"key":"Brand","name":"Brand","title":"the Burning Vengeance"},"131":{"id":131,"key":"Diana","name":"Diana","title":"Scorn of the Moon"},"60":{"id":60,"key":"Elise","name":"Elise","title":"The Spider Queen"},"267":{"id":267,"key":"Nami","name":"Nami","title":"the Tidecaller"},"266":{"id":266,"key":"Aatrox","name":"Aatrox","title":"the Darkin Blade"},"61":{"id":61,"key":"Orianna","name":"Orianna","title":"the Lady of Clockwork"},"143":{"id":143,"key":"Zyra","name":"Zyra","title":"Rise of the Thorns"},"48":{"id":48,"key":"Trundle","name":"Trundle","title":"the Troll King"},"45":{"id":45,"key":"Veigar","name":"Veigar","title":"the Tiny Master of Evil"},"44":{"id":44,"key":"Taric","name":"Taric","title":"the Gem Knight"},"51":{"id":51,"key":"Caitlyn","name":"Caitlyn","title":"the Sheriff of Piltover"},"53":{"id":53,"key":"Blitzcrank","name":"Blitzcrank","title":"the Great Steam Golem"},"54":{"id":54,"key":"Malphite","name":"Malphite","title":"Shard of the Monolith"},"254":{"id":254,"key":"Vi","name":"Vi","title":"the Piltover Enforcer"},"50":{"id":50,"key":"Swain","name":"Swain","title":"the Master Tactician"}}
