from flask import Flask, render_template, request
from os import environ
from riotpy import *
from twilio import twiml
from datetime import datetime, timedelta
import json

PORT = int(environ.get('PORT', 5000))
DEBUG = 'DEBUG' in environ # This will evaluate to True or False

app = Flask(__name__)


#####################################################
# Routes

@app.route("/", methods=['GET'])
def index():
	"""Renders the homepage"""

	return render_template('index.html')


@app.route("/find_game")
def find_game():
	"""Returns the summoner's current game info"""

	# FIXME: What do I do with summoners who aren't in game?
	summoner_name = request.args.get('summoner')
	game_info = riot.get_current_game_info(summoner_name)
	print "\n\nGame info: {}\n\n".format(game_info)
	return json.dumps(game_info)


@app.route("/api_key")
def return_api_key():
	"""Returns a JSON object containing the Riot API key"""

	return json.dumps({'api_key': RIOT_KEY})

@app.route("/", methods=['POST'])
def respond():
	"""Sends a text response"""

	caller = request.values['From']
	summoner_name = request.values['Body'].strip()
	print request.values

	summoner_id = riot.get_summoner_id(summoner_name)
	game = riot.get_current_game(summoner_id)

	if game:
		# Determine game duration
		game_start_epoch = float(game['gameStartTime'])/1000
		game_start = datetime.fromtimestamp(game_start_epoch)
		duration = datetime.now() - game_start
		minutes = int(duration.total_seconds()/60)

		# Determine champion
		for player in game['participants']:
			if player['summonerId'] == summoner_id:
				champ_id = player['championId']
				champ = riot.champs[champ_id]
				break

		# Determine game type
		if int(game['gameQueueConfigId']) in ranked:
			game_type = 'ranked'
		else:
			game_type = 'normal'
			print int(game['gameQueueConfigId'])

		# Create message
		msg = "{0} has been in a {1} game as {2} for {3} minutes.".format(summoner_name, game_type, champ, minutes)
	else:
		msg = "{0} is not currently in game.".format(summoner_name)

	# Send message
	resp = twiml.Response()
	resp.message(msg)

	return str(resp)

#####################################################
# Main

if __name__ == '__main__':
	app.run(debug=DEBUG, host="0.0.0.0", port=PORT)