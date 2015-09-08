from flask import Flask, render_template, request
from model import *
from twilio import twiml
from os import environ
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

	summoner_name = request.args.get('summoner')
	game_info = Summoner.get_current_game_info(summoner_name)
	print "\n\nGame info: {}\n\n".format(game_info)
	return json.dumps(game_info)


@app.route("/api_key")
def return_api_key():
	"""Returns a JSON object containing the Riot API key"""

	return json.dumps({'api_key': RIOT_KEY})


@app.route("/", methods=['POST'])
def respond_to_sms():
	"""Sends a text response"""

	caller = request.values['From']
	summoner_name = request.values['Body'].strip()
	sms = request.values
	msg_obj = TextMessage(sms)
	response = msg_obj.generate_response()
	
	# Send message
	resp = twiml.Response()
	resp.message(response)

	return str(resp)

#####################################################
# Main

if __name__ == '__main__':
	app.run(debug=DEBUG, host="0.0.0.0", port=PORT)