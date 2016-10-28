#!/usr/bin/env python

"""Add docstring. Clean up sources at the bottom"""


import random
import endpoints


def deck_creation():
	"""Create a list of 20 cards selected at random"""
	# Create a starting deck of 20 cards
	cards = [
		'A',
		'A',
		'B',
		'B',
		'C',
		'C',
		'D',
		'D',
		'E',
		'E',
		'F',
		'F',
		'G',
		'G',
		'H',
		'H',
		'I',
		'I',
		'J',
		'J']

	# Set variable for a card list to modify
	selection_deck = cards
	# Variable for the deck used in the game
	game_deck = []
	game_deck_counter = 0

	# Build the game deck
	while (game_deck_counter < 20):
		ran_card = random.choice(cards)
		selection_deck.remove(ran_card)
		game_deck.extend(ran_card)
		game_deck_counter += 1
	return game_deck


def guess_error(guess_int, mli):
	"""Check to make sure the card is in the deck and is not
	already part of a matched pair"""
	deck_check = range(20)
	if guess_int not in deck_check:
		raise endpoints.BadRequestException(
			'Sorry, that\'s not a card in this deck. Try again.')
	if guess_int in mli:
		raise endpoints.BadRequestException(
			'Sorry, there isn\'t a card there. Try again.')


def reset_deck(disp_deck, mli):
	"""Reset the deck so that cards flipped over in the most
	recent turn are flipped back over when the next turn starts.
	Note: cards that have been matched are left as an X"""
	for x in range(len(disp_deck)):
		if x in mli:
			disp_deck[x] = 'X'
		else:
			disp_deck[x] = '_'


def won_or_lost(game):
	"""Add docstring"""
	if game.matches_found == 3:
		game.end_game(True)
		won_lost_msg = ' You win!'
	elif game.attempts_remaining < 1:
		game.end_game(False)
		won_lost_msg = ' Game over. You\'ve run out of guesses.'
	else:
		won_lost_msg = ''
	return won_lost_msg


# SOURCES

# SO user Peteris Caune helped me learn how to take a random
# object from a list; see http://stackoverflow.com/questions/
# 18265935/python-create-list-with-numbers-between-2-values

# My source for the deck_check list; SO: http://stackoverflow.com/
# questions/18265935/python-create-list-with-numbers-between-2-values

# A SO discussion helped me figure out how to display chosen cards;
# see http://stackoverflow.com/questions/2582138/finding-and-
# replacing-elements-in-a-list-python
