$('#search-btn').click(findGame);

function findGame(evt) {
	evt.preventDefault();

	// Get summoner name from the DOM
	var summonerName = $('#summoner-name').val();
	var summonerInfo = {
		summoner: summonerName,
		region: $('#region').val()
	};
	
	// Update the DOM for loading
	$('img#search-btn').attr('src', '/static/img/loading.gif');
	$('table').addClass('hidden');
	$('#game-status').addClass('hidden');
	$('#teamOne').text('');
	$('#teamTwo').text('');


	// Get the game from the server
	$.get('/find_game', summonerInfo, function(response) {
		var response = JSON.parse(response);
		var summonerId = response.summonerId;
		var game = response.game;
		
		if (summonerId) {
			if (game.gameType) { // If the summoner exists and is in game

				// Set the game status
				var gameStart = moment.unix(game.startTime);
				var duration =  moment(gameStart).fromNow(true);
				var gameType = game['gameType'];

				var gameStatus = summonerName + ' has been in a ' + gameType + ' game for ' + duration + '.';

				// Iterate over teamOne participants, adding info to DOM
				for (var i = 0; i < game.teamOne.length; i++) {
					var player = game.teamOne[i];

					// Reformat winRate
					if (player.winRate) {
						var winRate = player.winRate + '%';
					} else {
						var winRate = 'unknown';
					};

					// Assemble participant info
					var participantInfo = '<tr>\
												<td>' + player.summonerName + '</td>\
												<td>' + player.champName + ' (Success: ' + winRate +') </td>\
											</tr>';
					$('#teamOne').append(participantInfo);
				};

				// Iterate over teamTwo participants, adding info to DOM
				for (var i = 0; i < game.teamTwo.length; i++) {
					var player = game.teamTwo[i];

					if (player.winRate) {
						var winRate = player.winRate + '%';
					} else {
						var winRate = 'unknown';
					};

					// Assemble participant info
					var participantInfo = '<tr>\
												<td>' + player.summonerName + '</td>\
												<td>' + player.champName + ' (Success: ' + winRate + ') </td>\
											</tr>';
					$('#teamTwo').append(participantInfo);
				};
				$('table').removeClass('hidden');

			} else { // If the summoner exists, but is not in game
				var gameStatus = summonerName + ' is not currently in game.'
			};

		} else { // If the summoner doesn't exist
			var gameStatus = 'No summoner by the name ' + summonerName + ' could be found.';
		};

		$('img#search-btn').attr('src', '/static/img/search.png');
		$('#game-status').text(gameStatus);
		$('#game-status').removeClass('hidden');

	});
}