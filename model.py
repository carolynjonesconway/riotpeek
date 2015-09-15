from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound

from os import environ
import requests

RIOT_KEY = environ['RIOT_API_KEY']
db = SQLAlchemy()

RANKED_IDS = [4, 6, 9, 41, 42]
platforms = {'na':'NA1', 'br':'BR1', 'lan':'LA1', 'las':'LA2', 'oce':'OC1', 'eun':'EUN1', 'tr': 'TR1', 'ru':'RU', 'euw':'EUW1', 'kr':'KR'}


# FIXME: How should I connect the Riotpy class with my DB? Some refactoring may be necessary.

class Champion(db.Model):

	__tablename__ = "Champions"

	champ_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
	champ_name = db.Column(db.String(30), nullable=False, unique=True)

	def __repr__(self):
		return "<{} ({})>".format(self.champ_name, self.champ_id)

	@staticmethod
	def load_champions():
		"""Retrieves all the champs from the Riot server and adds them to the DB"""

		url = "https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion?dataById=true&api_key={}".format(RIOT_KEY)
		champs = requests.get(url).json()['data']

		for id_ in champs:
			 # Check if they're already in the DB
			try:
				champ_id = int(id_)
				Champion.query.get(champ_id)

			# If not, add them!
			except NoResultFound:
				champ = Champion(champ_id=champ_id, champ_name=champs[id_]['name'])
				db.session.add(champ)
				db.session.commit()



class Summoner(db.Model):

	__tablename__ = "Summoners"

	summoner_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
	summoner_name = db.Column(db.String(30), nullable=False, unique=True)
	region = db.Column(db.String(5), nullable=False, default='na')

	def __repr__(self):
		return "<Summoner:{} ID:{}>".format(self.summoner_name, self.summoner_id)

	@classmethod
	def get_summoner_id(cls, name, region='na'):
		"""Given a single summoner name, returns that summoner's id

		This decreases the number of requests by storing info.

			>>> Summoner.get_summoner_id('icegirl2163')
			43265218

		"""

		# Look in the DB for the summoner
		try:
			summoner = cls.query.filter_by(summoner_name=name).one()
			return summoner.summoner_id

		# If they aren't in the DB, query the Riot server
		except NoResultFound:
			url = 'https://{0}.api.pvp.net/api/lol/{0}/v1.4/summoner/by-name/{1}?api_key={2}'.format(region, name, RIOT_KEY)
			# If they exist, return their id.
			try:
				print "Checking Riot servers..."
				response = requests.get(url).json()
				summoner = cls(summoner_name=name, summoner_id=response[name]['id'], region=region) # Add this summoner's info to the DB
				db.session.add(summoner)
				db.session.commit()
				return response[name]['id']
			# If they don't exist, return none.
			except:
				return None


	@classmethod # FIXME: In the future maybe this is instead an instance method?
	def get_current_game_info(cls, summoner_name, region="na"):

		print "\n\nCls: {}\n\n".format(cls)
		summoner_id = cls.get_summoner_id(summoner_name)
		platform = platforms[region]

		url = "https://{0}.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/{1}/{2}/?api_key={3}".format(region, platform, summoner_id, RIOT_KEY)
		response = requests.get(url)
		
		game_stats = {'summonerId': summoner_id,
				  'game': {'teamOne':[],
						   'teamTwo':[],
						   'startTime': None,
						   'gameType': None,
						   'champName': None
						   }
				  }

		# Check if a game was found
		if int(response.status_code) != 200:
			print '\n\nStatusCode: {}\nURL: {}\nSummoner: {} ({})\n\n'.format(response.status_code, url, summoner_name, summoner_id)
			# If no game was found, stop here, do not pass GO, do not collect $200.
			return game_stats

		game = response.json()

		# Check if the game is ranked
		if int(game['gameQueueConfigId']) in RANKED_IDS:
			game_type = 'ranked'
		else:
			game_type = 'normal'



	def get_win_rate(self, champion_id):
		"""Returns a summoner's win rate on a given champ

		If the summoner has no ranked games on that champ, returns None.
		"""

		url = "https://{0}.api.pvp.net/api/lol/{0}/v1.3/stats/by-summoner/{1}/ranked/?api_key={2}".format(self.region, self.summoner_id, RIOT_KEY)
		
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
			return None



class Nickname(db.Model):

	__tablename__ = "Nicknames"

	nickname_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	phone_number = db.Column(db.String(12), nullable=False)
	summoner_id = db.Column(db.Integer,
						 db.ForeignKey('Summoners.summoner_id'),
						 nullable=False)
	name = db.Column(db.String(60), nullable=False)

	# Relationships
	summoner = db.relationship('Summoner', backref=db.backref("nickname"))

	def __repr__(self):
		return "<Phone: {} Nickname: {}>"



# FIXME: Setup tests for ALLLL of this!
class TextMessage(object):

	# FIXME: Does it actually make sense to pass in a riotpy_instance?
	def __init__(self, sms):
		self.sms = sms
		self.summoner = None
		self.nickname = None
		self.phone_number = sms['From']
		self.parse_command()


	def generate_response(self):
		"""Determines the correct response based on SMS content"""

		if self.command == 'invalid':
			response = "Invalid command."

		if self.command == 'find':
			response = self.find_summoner()
			
		elif self.command == 'nickname':
			response = self.set_nickname()

		return response


	def find_summoner(self):
		"""Finds a game for the requested summoner, and returns a success string"""

		if self.summoner:
			game_stats = Summoner.get_current_game_info(self.summoner)
			game = game_stats['game']

			if game['gameType'] is not None:
				# Determine game duration
				game_start = datetime.fromtimestamp(game['startTime'])
				duration = datetime.now() - game_start
				total_minutes = int(duration.total_seconds()/60)

				# Determine champion
				champ_id = None
				for player in game['teamOne']:
					if player['summonerId'] == game_stats['summonerId']:
						champ_id = player['championId']
						champ_name = Champion.query.get(champ_id).champ_name
						break

				if not champ_id:
					for player in game['teamTwo']:
						if player['summonerId'] == game_stats['summonerId']:
							champ_id = player['championId']
							champ_name = Champion.query.get(champ_id).champ_name
							break

				# Set response
				response = "{0} has been in a {1} game as {2} for {3} minutes.".format(self.summoner, game['gameType'], champ_name, total_minutes)
			
			elif game['gameType'] is None:
				response = "{0} is not currently in game.".format(self.summoner)
		
		elif not self.summoner:
			response = "Oops! We couldn't tell who you wanted us to find."

		return response


	def set_nickname(self):
		"""Assigns a nickname to a given summoner, and returns a success string"""

		if self.summoner and self.nickname:

			self.summoner_id = Summoner.get_summoner_id(self.summoner)
			# Check for an existing, identical nickname
			try:
				Nickname.query.filter_by(phone_number=self.phone_number, summoner_id=self.summoner_id, name=self.nickname).one()
				response = "You've already set that nickname!"

			# If there isn't an existing one, create a new one!
			except NoResultFound:
				n = Nickname(phone_number=self.phone_number,
							 summoner_id= self.summoner_id,
							 name=self.nickname
							 )
				db.session.add(n)
				db.session.commit()
				response = "Got it! I'll remember that nickname for you."
		else:
			response = "Oops! We couldn't tell who you wanted us to nickname."

		return response


	def parse_command(self):
		"""Determines what command was used"""

		self.content = self.sms['Body'].strip().lower().split()
		command = self.content[0].lower()

		if command == 'find':
			self.command = command

			if len(self.content) == 2:
				summoner_name = self.content[1]
				summoner_id = Summoner.get_summoner_id(summoner_name)
				if summoner_id:
					self.summoner = summoner_name
				else:
					self.summoner = None 

		elif command == 'nickname':
			self.command = command
			if len(self.content) == 3:
				self.summoner = self.content[1]
				self.nickname = self.content[2]

		else:
			print self.content[0].lower()
			self.command = 'invalid'

################################################################
# Helper Functions

def connect_to_db(app):
    """Connects the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///riotpeek.db'
    # app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
	from server import app
	connect_to_db(app)
	print "Connected to DB."