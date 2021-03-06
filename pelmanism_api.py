#!/usr/bin/env python


"""
The Pelmanism API is made up of 12 endpoints, and these are built and
configured in pelmanism_api.py.

The endpoints are as follows: create_user, new_game, get_game,
make_move, get_scores, get_user_scores, get_average_attempts_remaining,
get_user_games, cancel_game, get_high_scores, get_user_rankings,
get_game_history.

The class definitions for the Google Datastore entities used by
Pelmanism are defined in the models package, and the game_logic.py
file contains several functions used in the make_move endpoint.

"""


import logging
import endpoints

from protorpc import remote, messages

from google.appengine.api import memcache, taskqueue
from google.appengine.ext import ndb

from models.user import User, UserRankings, StringMessage
from models.game import (Game,
                         GameForm,
                         GameForms,
                         NewGameForm,
                         MakeMoveForm,
                         ScoreForms,
                         GameHistory,
                         StringMessage)
from models.guess1 import Guess1
from models.score import Score, ScoreForms

import game_logic

from utils import get_by_urlsafe


# Define global variables
NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1),
    email=messages.StringField(2))
CANCEL_GAME = endpoints.ResourceContainer(
    user_name=messages.StringField(1),
    urlsafe_game_key=messages.StringField(2))
HIGH_SCORES = endpoints.ResourceContainer(
    number_of_results=messages.IntegerField(1))
MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'


# Define the endpoints class for the API
@endpoints.api(name='pelmanism', version='v1',
               description='Pelmanism API')
class PelmanismApi(remote.Service):
    """Define Pelmanism API v1"""


# Define the endpoints
    # CREATE USER endpoint ---
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a user; a unique user name is required"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A user with that name already exists.')
        user = User(name=request.user_name, email=request.email,
                    games_played=0, total_attempts=0, total_points=0,
                    points_per_attempt=0)
        user.put()
        return StringMessage(message='User {} created!'.format(
            request.user_name))

    # NEW GAME endpoint ---
    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Create a new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A user with that name does not exist!')

        # Set up game variables
        deck = game_logic.deck_creation()
        disp_deck = ['_' for x in range(len(deck))]
        attempts_made = 0
        match_list = []
        match_list_int = []
        matches_found = 0
        guess1_or_guess2 = 0
        guess_history = []

        # Attempt to create a new game object
        try:
            game = Game.new_game(
                user.key,
                request.attempts,
                deck,
                disp_deck,
                attempts_made,
                match_list,
                match_list_int,
                matches_found,
                guess1_or_guess2,
                guess_history)
        except ValueError:
            raise endpoints.BadRequestException(
                'Number of attempts must be more than 29 and less than 61')

        # Update the number of attempts remaining with a task queue
        taskqueue.add(url='/tasks/cache_average_attempts')

        # Call the to_form() function, which fills in GameForm
        # We pass in what will be the message as the argument
        return game.to_form('Good luck playing Pelmanism!')

    # GET GAME endpoint ---
    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current state of an active game"""
        # Check to see if the urlsafe_game_key matches a game
        # in the datastore
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if game.game_over:
                return game.to_form('The game is already over!')
            if game.cancelled:
                return game.to_form('The game has been cancelled!')
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    # MAKE MOVE endpoint ---
    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='POST')
    def make_move(self, request):
        """Make a move (or an attempt); this consists of two guesses,
        meaning that a user must call the make_move endpoint twice in
        order to make a move; at the conclusion of the move,
        return a game state with message"""
        # Set up variables for making the first and second guesses
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        user = User.query(game.user == User.key).get()
        deck = game.deck
        # A list of the integers that correspond to each card that
        # has been matched
        mli = game.match_list_int
        # A list of card values (e.g. 'B' or 'H') that have been matched
        match_list = game.match_list

        # FIRST GUESS
        # The guess1_or_guess2 property is used to determine if the player
        # is flipping over their first or second card of the move
        if game.guess1_or_guess2 % 2 == 0:

            # Retrieve the Guess1 model for this game and delete
            # the previous entities (this ensures only the most recent
            # guess1 is in the database, thus simplifying the second guess)
            guess1_old = Guess1.query(ancestor=game.key).get()
            if guess1_old is not None:
                guess1_old.key.delete()

            # Set up a variable for the integer representing the card
            guess1_int = request.guess

            # Reset the deck (make sure all cards are turned over)
            game_logic.reset_deck(game.disp_deck, mli)

            # Check to see if the game is over or cancelled
            if game.game_over:
                return game.to_form('The game is already over!')
            if game.cancelled:
                return game.to_form('The game has been cancelled!')

            # Handle a guess error
            game_logic.guess_error(guess1_int, mli)

            # Convert guess_int into a string variable containing
            # the actual card value (i.e. a letter, rather than a num)
            guess1 = deck[guess1_int]

            # Display the deck with the chosen card flipped over
            game.disp_deck[guess1_int] = guess1

            # Add the guess into the database, making game.key the parent
            guess1_db = Guess1(parent=game.key,
                               guess1=guess1,
                               guess1_int=guess1_int)
            guess1_db.put()

            game.guess1_or_guess2 += 1
            game.put()
            return game.to_form(
                'You turned over a %s. Turn over another card.' % guess1)

        # SECOND GUESS
        else:
            # Retrieve the guess1 model that matches this game
            # (this is done to check for a match later)
            guess1 = Guess1.query(ancestor=game.key).get()

            # Set up a variable for the integer representing the card
            guess2_int = request.guess

            # Handle a guess error
            game_logic.guess_error(guess2_int, mli)

            game.attempts_remaining -= 1
            game.attempts_made += 1
            game.guess1_or_guess2 += 1
            user.total_attempts += 1

            # Convert guess2_int into a string variable containing
            # the actual card value (i.e. a letter, rather than a num)
            guess2 = deck[guess2_int]
            msg = 'You turned over a %s. ' % guess2

            # Display the deck with the chosen card flipped over
            game.disp_deck[guess2_int] = guess2

            # Return an error if the same card was picked twice
            if guess1.guess1_int == guess2_int:
                raise endpoints.BadRequestException(
                    msg + 'You can\'t pick the same card twice!')

            # Determine if a match was found
            if guess1.guess1 == guess2:
                match_list.extend(guess1.guess1)
                match_list.extend(guess2)
                mli.append(guess1.guess1_int)
                mli.append(guess2_int)
                game.matches_found += 1
                match_msg = 'You found a match!'

            else:
                match_msg = 'Sorry, you didn\'t find a match.'

            # Determine if the game is over
            won_lost_msg = game_logic.won_or_lost(game, user,
                                                  guess1.guess1, guess2)
            # If the game is over, add up the points scored
            game_logic.points(
                game, game.attempts_made, game.matches_found, user)

            game.put()
            user.put()
            return game.to_form(msg + match_msg + won_lost_msg)

    # GET SCORES endpoint ---
    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores ordered by time_completed"""
        return ScoreForms(
            items=[score.to_form() for score in Score.query(
            ).order(-Score.time_completed)])

    # GET USER SCORES endpoint ---
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Return all of an individual user's scores ordered by points"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A user with that name does not exist!')
        scores = Score.query(Score.user == user.key).order(-Score.points)
        return ScoreForms(items=[score.to_form() for score in scores])

    # GET AVERAGE ATTEMPTS endpoint ---
    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts_remaining',
                      http_method='GET')
    def get_average_attempts(self, request):
        """Return the cached average attempts (or moves) remaining
        for all active games"""
        return StringMessage(message=memcache.get(
            MEMCACHE_MOVES_REMAINING) or '')

    @staticmethod
    def _cache_average_attempts():
        """Populate the memcache with the average attempts (or
        moves) remaining"""
        games = Game.query(Game.game_over == False).fetch()
        if games:
            count = len(games)
            total_attempts_remaining = sum([game.attempts_remaining
                                            for game in games])
            average = float(total_attempts_remaining) / count
            memcache.set(
                MEMCACHE_MOVES_REMAINING,
                'The average moves remaining is {:.2f}'.format(average))

    # GET USER GAMES endpoint ---
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='game/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return a user's active games ordered by the time each game
        was created"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A user with that name does not exist!')
        # Get a list of all of a user's games
        games = Game.query(
            Game.user == user.key).order(-Game.time_created).fetch()

        # Filter out completed and cancelled games; return what's left
        game_lst = []
        for g in games:
            if not g.game_over:
                if not g.cancelled:
                    game_lst.append(g)
        return GameForms(
            items=[g.to_form_user_games() for g in game_lst])

    # CANCEL GAME endpoint ---
    @endpoints.method(request_message=CANCEL_GAME,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}/user/{user_name}',
                      name='cancel_game',
                      http_method='POST')
    def cancel_game(self, request):
        """Cancel a game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A user with that name does not exist!')
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            raise endpoints.BadRequestException(
                'Sorry, you can\'t delete a completed game.')
        if user.key != game.user:
            raise endpoints.BadRequestException(
                'Sorry, you\'re not authorized to cancel this game.')
        game.cancelled = True
        game.put()
        return game.to_form('Game cancelled')

    # GET HIGH SCORES endpoint ---
    @endpoints.method(request_message=HIGH_SCORES,
                      response_message=ScoreForms,
                      path='high_scores',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """Return all scores ordered by points; an optional parameter
        (number_of_results) limits the number of results returned"""
        num = request.number_of_results
        if num:
            scores = Score.query().order(-Score.points).fetch(num)
        else:
            scores = Score.query().order(-Score.points).fetch()
        return ScoreForms(
            items=[score.to_form() for score in scores])

    # GET USER RANKINGS endpoint ---
    @endpoints.method(response_message=UserRankings,
                      path='user_rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return a list of users ranked by points_per_attempt
        (points_per_attempt is determined by total_points /
        total_attempts); a tie is broken by total_points"""
        u_rankings = User.query().order(
            -User.points_per_attempt, -User.total_points).fetch()
        return UserRankings(
            items=[user.to_rankings_form() for user in u_rankings])

    # GET GAME HISTORY endpoint ---
    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameHistory,
                      path='game_history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return a list of guesses made throughout the course of
        a completed game as well as the end result of the game"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if game.game_over:
                return game.to_form_game_history(
                    'Thanks for playing, Pelmanism.')
            elif game.cancelled:
                return game.to_form_game_history(
                    'The game has been cancelled!')
            else:
                return game.to_form_game_history(
                    'The game is not over yet!')
        else:
            raise endpoints.NotFoundException('Game not found!')


# Start the API server
api = endpoints.api_server([PelmanismApi])
