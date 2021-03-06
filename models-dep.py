#!/usr/bin/env python


"""
NOTE: The models.py file has been deprecated and is therefore now called
models-dep.py. The file was refactored into a Python package called models.
The package includes four modules: user.py, game.py, guess1.py, and score.py.

The class definitions for the Google Datastore entities used by
Pelmanism are defined in models.py. Helper methods are also included.

Pelmansim is made up of four models: User, Game, Guess1 and Score.

Message classes are also included in models.py. These are: GameForm,
GameFormUserGame, GameForms, NewGameForm, MakeMoveForm, ScoreForm,
ScoreForms, UserRanking, UserRankings, GameHistory and StringMessage.

"""


from datetime import datetime
from protorpc import messages
from google.appengine.ext import ndb


# DEFINE GAME OBJECTS
class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    games_played = ndb.IntegerProperty(required=True)
    total_attempts = ndb.IntegerProperty(required=True)
    total_points = ndb.IntegerProperty(required=True)
    points_per_attempt = ndb.IntegerProperty(required=True)

    def to_rankings_form(self):
        """Return a UserRanking representation of the User"""
        return UserRanking(
            user_name=self.name,
            games_played=self.games_played,
            total_attempts=self.total_attempts,
            total_points=self.total_points,
            points_per_attempt=self.points_per_attempt)


class Game(ndb.Model):
    """Game object"""
    deck = ndb.StringProperty(repeated=True)
    disp_deck = ndb.StringProperty(repeated=True)
    attempts_allowed = ndb.IntegerProperty(required=True)
    attempts_remaining = ndb.IntegerProperty(required=True, default=30)
    game_over = ndb.BooleanProperty(required=True, default=False)
    attempts_made = ndb.IntegerProperty(required=True)
    match_list = ndb.StringProperty(repeated=True)
    match_list_int = ndb.IntegerProperty(repeated=True)
    matches_found = ndb.IntegerProperty(required=True)
    guess1_or_guess2 = ndb.IntegerProperty()
    cancelled = ndb.BooleanProperty(required=True, default=False)
    guess_history = ndb.StringProperty(repeated=True)
    time_created = ndb.StringProperty(required=True)
    user = ndb.KeyProperty(required=True, kind='User')

    @classmethod
    def new_game(cls, user, attempts, deck, disp_deck, attempts_made,
                 match_list, match_list_int, matches_found,
                 guess1_or_guess2, guess_history):
        """Create and return a new game"""
        if attempts < 30 or attempts > 60:
            raise ValueError(
                'Number of attempts must be more than 29 and less than 61')
        game = Game(
            user=user,
            deck=deck,
            attempts_allowed=attempts,
            attempts_remaining=attempts,
            disp_deck=disp_deck,
            attempts_made=attempts_made,
            match_list=match_list,
            match_list_int=match_list_int,
            matches_found=matches_found,
            guess1_or_guess2=guess1_or_guess2,
            game_over=False,
            cancelled=False,
            guess_history=guess_history,
            time_created=str(datetime.now()))
        game.put()
        return game

    def to_form(self, message):
        """Return a GameForm representation of the game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.attempts_remaining = self.attempts_remaining
        form.game_over = self.game_over
        form.cancelled = self.cancelled
        form.disp_deck = self.disp_deck
        form.attempts_made = self.attempts_made
        form.match_list = self.match_list
        form.matches_found = self.matches_found
        form.time_created = self.time_created
        form.message = message
        return form

    def to_form_user_games(self):
        """Return a GameFormUserGame representation of the game;
        this form displays a custom list of the game entities and is
        used in the get_user_games endpoint"""
        return GameFormUserGame(
            urlsafe_key=self.key.urlsafe(),
            user_name=self.user.get().name,
            attempts_remaining=self.attempts_remaining,
            game_over=self.game_over,
            disp_deck=self.disp_deck,
            attempts_made=self.attempts_made,
            match_list=self.match_list,
            matches_found=self.matches_found,
            time_created=self.time_created)

    def to_form_game_history(self, message):
        """Return a GameHistory representation of the game;
        this form displays a custom list of the game entities and is
        used in the get_game_history endpoint"""
        return GameHistory(
            user_name=self.user.get().name,
            guess_history=self.guess_history,
            attempts_made=self.attempts_made,
            match_list=self.match_list,
            matches_found=self.matches_found,
            deck=self.deck,
            time_created=self.time_created,
            message=message)

    def end_game(self, won=False):
        """End the game; if won is True, the player won;
        if won is False, the player lost"""
        self.game_over = True
        self.put()

        # Add the game to the score board
        # (a score is only returned when a game ends)
        points = self.points = (
            500 - ((self.attempts_made - self.matches_found) * 10))
        score = Score(
            user=self.user,
            time_completed=str(datetime.now()),
            won=won,
            attempts_made=self.attempts_made,
            game_deck=self.deck,
            matches_found=self.matches_found,
            points=points)
        score.put()


class Guess1(ndb.Model):
    """Guess1 object; each Guess1 model is given a parent (game.key) in
    pelmansim_api.py; the Guess1 model is compared with the guess2 and
    guess2_int attributes in the make_move endpoint in pelmansim_api.py"""
    guess1 = ndb.StringProperty(required=True)
    guess1_int = ndb.IntegerProperty(required=True)


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    time_completed = ndb.StringProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    attempts_made = ndb.IntegerProperty(required=True)
    game_deck = ndb.StringProperty(repeated=True)
    matches_found = ndb.IntegerProperty(required=True)
    points = ndb.IntegerProperty(required=True)

    def to_form(self):
        """Return a ScoreForm representation of the score"""
        return ScoreForm(
            user_name=self.user.get().name,
            won=self.won,
            time_completed=self.time_completed,
            attempts_made=self.attempts_made,
            game_deck=self.game_deck,
            matches_found=self.matches_found,
            points=self.points)


# MESSAGE DEFINITIONS
class GameForm(messages.Message):
    """Used for outbound game information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts_remaining = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)
    disp_deck = messages.StringField(6, repeated=True)
    attempts_made = messages.IntegerField(7, required=True)
    match_list = messages.StringField(8, repeated=True)
    matches_found = messages.IntegerField(9, required=True, default=0)
    cancelled = messages.BooleanField(10, required=True)
    time_created = messages.StringField(11, required=True)


class GameFormUserGame(messages.Message):
    """Used for outbound information on the state of a
    user's active game"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts_remaining = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    user_name = messages.StringField(4, required=True)
    disp_deck = messages.StringField(5, repeated=True)
    attempts_made = messages.IntegerField(6, required=True)
    match_list = messages.StringField(7, repeated=True)
    matches_found = messages.IntegerField(8, required=True)
    time_created = messages.StringField(9, required=True)


class GameForms(messages.Message):
    """Outbound container for a list of GameFormUserGame forms"""
    items = messages.MessageField(GameFormUserGame, 1, repeated=True)


class NewGameForm(messages.Message):
    """Inbound form used to create a new game"""
    user_name = messages.StringField(1, required=True)
    attempts = messages.IntegerField(2, required=True)


class MakeMoveForm(messages.Message):
    """Inbound form used to make a move"""
    guess = messages.IntegerField(1, required=True)


class ScoreForm(messages.Message):
    """Used for outbound score information for finished games"""
    user_name = messages.StringField(1, required=True)
    time_completed = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    attempts_made = messages.IntegerField(4, required=True)
    game_deck = messages.StringField(5, repeated=True)
    matches_found = messages.IntegerField(6, required=True, default=0)
    points = messages.IntegerField(7, required=True, default=0)


class ScoreForms(messages.Message):
    """Outbound container for a list of ScoreForm forms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class UserRanking(messages.Message):
    """Used for outbound information regarding user rankings (players are
    ranked by points_per_attempt; total_points is used to break a tie)"""
    user_name = messages.StringField(1, required=True)
    games_played = messages.IntegerField(2, required=True)
    total_attempts = messages.IntegerField(3, required=True)
    total_points = messages.IntegerField(4, required=True)
    points_per_attempt = messages.IntegerField(5, required=True)


class UserRankings(messages.Message):
    """Outbound container for a list of UserRanking forms"""
    items = messages.MessageField(UserRanking, 1, repeated=True)


class GameHistory(messages.Message):
    """Used for outbound information on each guess made
    and the outcome of a game"""
    user_name = messages.StringField(1, required=True)
    guess_history = messages.StringField(2, repeated=True)
    attempts_made = messages.IntegerField(3, required=True)
    match_list = messages.StringField(4, repeated=True)
    matches_found = messages.IntegerField(5, required=True)
    deck = messages.StringField(6, repeated=True)
    time_created = messages.StringField(7, required=True)
    message = messages.StringField(8)


class StringMessage(messages.Message):
    """A single outbound string message"""
    message = messages.StringField(1, required=True)
