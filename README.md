# Pelmanism

Pelmanism is a matching game API built on Google App Engine and written in Python.


## General game description

Also known as memory or concentration, Pelmanism is a simple one-player card-matching game. Each game begins with a randomly-sorted, even-numbered deck of cards. The cards are displayed face down and can be arranged in a grid or another type of pattern by a front-end developer. The player decides the maximum number of moves or attempts (the terms are used synonymously in this game) they will be allowed to take during the course of the game.

Each move consists of 'turning face up' or 'flipping over' two cards; each card 'turned over' is considered a guess. If the cards match, they are removed from the playing deck. If the cards do not match, they remain in the playing deck and are 'turned back over'. The player continues to make moves until either all of the pairs have been matched or the player runs out of attempts.


## Install and set-up instructions
1. Install Pelmanism by cloning the Pelmanism repository on GitHub: `$ git clone https://github.com/bencam/pelmanism.git`

1. Create a new project on the [Google API Console](https://console.developers.google.com/). Add the app ID of the new project to the application value in app.yaml (line 1). This app ID will be used to host your instance of the API.

1. Run the app locally with the `dev_appserver.py [DIRECTORY_NAME_OF_PROJECT]` command. Make sure the app is running by visiting Google's API Explorer (the default address is localhost:8080/_ah/api/explorer).

1. Deploy the app to Google App Engine. Do this by running the the following command: `appcfg.py update [DIRECTORY_NAME_OF_PROJECT]`. Test the deployment of the app by visiting [APP_ID].appspot.com/_ah/api/explorer.


## Game details

To play this version of Pelmanism, users first create a user by calling the `create_user` endpoint and entering in their name and (optionally) their email address. A user then calls the `new_game` endpoint and inputs their user name as well as the number of allowed attempts they would like for the game (by default, a user must choose between 30 and 60 attempts). The `new_game` endpoint will then return a game state, which includes a `urlsafe_game_key`.

A user then calls the `make_move` endpoint, pasting the `urlsafe_game_key` into the form and choosing a card to 'flip over' by entering a number between 0 and 19 in the 'guess' field (this constitutes the first guess of the move). The `make_move` endpoint will then return the game state, including information about which card the user turned over. In order to complete the move or attempt, the user calls the `make_move` endpoint a second time (the second guess of the move). The `urlsafe_game_key` field will remain populated with the correct key, so the user will only need to choose another card to 'flip over' by again inputing a number between 0 and 19 in the 'guess' field. A game state will be returned and include information on whether a match was found.

This process of calling the `make_move` endpoint twice for each move continues until the user either finds all of the matches in the deck or runs out of attempts (again, 'attempts' and 'moves' are used synonymously in this API). Details on how 'cards' are displayed during the game play can be found in the 'Adjusting the game' section below.

By default, Pelmanism uses a deck of 20 cards, but this can be adjusted (see the section below titled 'Adjusting the game').

Many users can play Pelmanism games at the same time, and each game can be played or retrieved by using the `urlsafe_game_key` path parameter.

Points are awarded at the end of each game. The following formula is used to determine how many points are awarded: `points = (500 - ((attempts_made - matches_found) * 10))`. Users can view points earned by themselves and other users with the `get_scores`, `get_user_scores`, and `get_high_scores` endpoints.

Each user profile includes `games_played`, `total_attempts`, `total_points`, and `points_per_attempt` properties. These are updated at the conclusion of each game played. The `points_per_attempt` property is determined with the following formula: `points_per_attempt = total_points / total_attempts`. Users can see how they rank against other users with the `get_user_rankings` endpoint. Users are ranked by the `points_per_attempt` property; in the event of a tie, users are ranked according to the `total_points` property.

The `get_game_history` endpoint provides a user with a summary of each move taken during the course of a completed game. The endpoint also indicates how the game ended (i.e. did the player win or lose?).

Pelmanism also uses a cronjob to notify users. The cronjob sends a reminder email every 24 hours to only those users who have at least one uncompleted game.

More details about the game Pelmanism--and variations of it--can be found [here](https://en.wikipedia.org/wiki/Concentration_(game)).


## Adjusting the game
In Pelmanism the 'face' of each card is, by default, simply a string variable set to a capital letter of the Roman alphabet (e.g. `'C'` and `'C'` are a match). This can be changed by adjusting the card variables in the `deck_creation()` function in game_logic.py.

A string variable set to `'_'` represents a card as being 'facedown'. This can be adjusted by changing the `disp_deck` variable in the `new_game` endpoint in pelmanism_api.py.

A string variable set to `'X'` indicates that there is no card in that particular spot on the board (i.e. that card has been matched with another and has, therefore, been removed). To change the `'X'` value, alter the `disp_deck[x]` variable in the `reset_deck()` function in game_logic.py.

By default, Pelmanism uses a deck of 20 cards, but this can be adjusted by altering several lines in game_logic.py. First, add more 'cards' to the `cards` variable in `deck_creation()`. Make sure each 'card' has a match. Next, change the number in the while loop (line 58) to reflect the updated total number of cards in the deck. Set the value of `deck_check` in the `guess_error()` function to the same number. Next, adjust the value of `game.matches_found` in the `won_or_lost()` function to half of the total cards in the deck. Do the same to the value of `game.matches_found` in the `points()` function.


## Files included
 - pelmanism_api.py: contains endpoints and part of the game-playing logic
 - models.py: defines entities and messages; contains helper methods
 - game_logic.py: contains five functions needed for the game play
 - main.py: contains handlers for the taskqueue and cronjob
 - utils.py: contains a helper function for retrieving game information
 - app.yaml: app configuration
 - cron.yaml: crongjob configuration
 - index.yaml: automatically updated with index information


## Endpoints included
 - **create_user**
 	- Path: 'user'
 	- Method: POST
 	- Parameters: user_name, email (optional)
 	- Returns: Message confirming creation of new User
 	- Description: Creates a new user; the user_name must be unique; an exception will be raised if a user registers under a user_name that already exists

 - **new_game**
 	- Path: 'game'
 	- Method: POST
 	- Parameters: user_name, attempts
 	- Returns: GameForm with initial game information
 	- Description: Creates a new game; the user_name sent in the request must correspond to an existing user; a NotFoundException will be raised otherwise; the number of attempts must be no more than 60 and no less than 30; a task is also added to the taskqueue to update the average attempts remaining for all active games

 - **get_game**
  - Path: 'game/{urlsafe_game_key}'
 	- Method: GET
 	- Parameters: urlsafe_game_key
 	- Returns: GameForm with current game information
 	- Description: Returns the current state of an active game

 - **make_move**
  - Path: 'game/{urlsafe_game_key}'
  - Method: PUT
 	- Parameters: urlsafe_game_key, guess
 	- Returns: GameForm with updated game information
 	- Description: Make a move (or an attempt); this consists of two guesses, meaning that a user must call the make_move endpoint twice in order to make a move; at the conclusion of the move, return a game state with message

 - **get_scores**
  - Path: 'scores'
 	- Method: GET
 	- Parameters: None
 	- Returns: ScoreForms
 	- Description: Returns all scores (ordered by time_completed)

 - **get_user_scores**
  	- Path: 'scores/user/{user_name}'
 	- Method: GET
 	- Parameters: user_name
 	- Returns: ScoreForms
 	- Description: Returns all of a user's scores (ordered by points); raises a NotFoundException if a user with the user_name provided in the request does not exist

 - **get_average_attempts_remaining**
  - Path: 'games/average_attempts'
 	- Method: GET
 	- Parameters: None
 	- Returns: StringMessage
 	- Description: Returns the cached average attempts remaining for all active games

 - **get_user_games**
  - Path: 'game/user/{user_name}'
 	- Method: GET
 	- Parameters: user_name
 	- Returns: GameForms
 	- Description: Returns a user's active games ordered by the time each game was created; raises a NotFoundException if a user with the user_name provided in the request does not exist

 - **cancel_game**
  - Path: 'game/{urlsafe_game_key}/user/{user_name}'
 	- Method: PUT
 	- Parameters: user_name, urlsafe_game_key
 	- Returns: GameForm
 	- Description: Cancels a game; returns the game information with the message 'Game cancelled'; raises a NotFoundException if a user with the user_name provided in the request does not exist; raises a BadRequestException if the urlsafe_game_key sent in the request is for a completed game; raises a BadRequestException if the user_name sent in the request is not connected with the game

 - **get_high_scores**
  - Path: 'high_scores'
 	- Method: GET
 	- Parameters: number_of_results (optional)
 	- Returns: ScoreForms
 	- Description: Returns all scores sorted by points; an optional parameter (number_of_results) limits the number of results returned

 - **get_user_rankings**
  - Path: 'user_rankings'
 	- Method: GET
 	- Parameters: None
 	- Returns: UserRankings
 	- Description: Returns a list of users ranked by points_per_attempt (points_per_attempt is determined by total_points / total_attempts); a tie is broken by total_points

 - **get_game_history**
  - Path: 'game_history'
 	- Method: GET
 	- Parameters: urlsafe_game_key
 	- Returns: GameHistory
 	- Description: Return a list of guesses made throughout the course of a completed game as well as the end result of the game; raises a NotFoundException if the urlsafe_game_key does not match a corresponding game in the database; a message will indicate if the game is still active or was cancelled


## License

Pelmanism is released under the [MIT License](http://opensource.org/licenses/MIT).
