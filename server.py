from flask import Flask, render_template, request
from riotpy import Riotpy, RIOT_KEY

import json


app = Flask(__name__)
riot = Riotpy(RIOT_KEY)


#####################################################
# Routes

@app.route("/")
def index():

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

#####################################################
# Main

if __name__ == '__main__':
	app.run(debug=True)