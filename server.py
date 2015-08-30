from flask import Flask, render_template, request
from riotpy import Riotpy, RIOT_KEY, champs, ranked
from twilio import twiml
from datetime import datetime, timedelta
import json, os

app = Flask(__name__)
riot = Riotpy(RIOT_KEY)

#####################################################
# Routes

@app.route("/", methods=['GET'])
def index():
	"""Renders the homepage"""

	return render_template('index.html')


@app.route("/find_game")
def find_game():
	"""Returns the summoner's current game, or None"""

	summoner_name = request.args.get('summoner')
	summoner_id = riot.get_summoner_id(summoner_name)
	game = riot.get_current_game(summoner_id)

	response = {'summonerId': summoner_id,
				'game': game}

	return json.dumps(response)


@app.route("/get_champs")
def return_champs():
	"""Returns a JSON object of the LoL champs, mapped by id"""

	return json.dumps(champs)


@app.route("/", methods=['POST'])
def respond():
	"""Sends a text response"""

	caller = request.values['From']
	summoner_name = request.values['Body'].strip()

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
				champ = champs[champ_id]
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
	app.run(debug=True)