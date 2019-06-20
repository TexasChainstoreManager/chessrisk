from ai.base import AiPlayer

import random
import json
import os

script_dir = os.path.dirname(__file__)

def weighted_choice(options, weights):
    # NB: This method not tested. Hey, it might work.
    # Normalise the weights so they sum to 1
    sum_weights = sum(weights)
    norm_weights = [w/sum_weights for w in weights]

    # This puts the weights on the number line mentioned below.
    cum_weights = [0]
    for w in norm_weights:
        cum_weights.append(cum_weights[-1] + w)

    picked = random.uniform(0, 1)

    # Imagine all the weights on a number line between 0 and 1.
    # If the picked number is immediately to the left of the nth weight,
    # that's the one we have chosen
    for i, w in enumerate(cum_weights):
        try:
            if picked > w:
                return options[i + 1]
        except IndexError:
            raise Exception("It should not be possible to get the last index in weighted_choice! The final cum_weight should be 1. Debug me please!")
        raise Exception("It should not be possible to not return in weighted_choice! The final cum_weight should be 1. Debug me please!")


class LearningSimpleton(AiPlayer):
    number_of_us = 0
    mutation_bounds = (0.9, 1.1)

    def __init__(self):
        super(LearningSimpleton, self).__init__()
        self.method_name = None
        self.weights = dict()
        self.load_weights()
        self.mutate_weights()

    def load_weights(self):
        current = os.path.join(script_dir, 'data', 'current.json')
        with open(current) as f:
            weights = f.read()
        if weights:
            self.weights = json.loads(weights)
            # Else, the weights dict auto-populates for any keys it can't find.

    def mutate_weights(self):
        for k in self.weights.keys():
            self.weights[k] = self.weights[k] * random.uniform(*self.mutation_bounds)

    def save_weights(self):
        current = os.path.join(script_dir, 'data', 'current.json')
        history_path = os.path.join(script_dir, 'data', 'history.json')
        with open(current, 'w') as f:
            f.write(json.dumps(self.weights))
        with open(history_path) as f:
            history = f.read()
        if history == '':
            history = []
        else:
            history = json.loads(history)
        history.append(self.weights)
        with open('data/history.json', 'w') as f:
            f.write(json.dumps(self.weights))

    def choice(self, options):
        if options not in self.weights:
            # If we've never seen these options before, assign them equal weights.
            self.weights[options] = [1]*len(options)

        return weighted_choice(options, self.weights[options])

    def randint(self, a, b):
        return self.choice(tuple(range(a, b + 1)))

    def name(self, gv):
        type(self).number_of_us += 1
        return '{}LSimpleton'.format(type(self).number_of_us)

    def build_or_attack(self, gv):
        return self.choice(('b', 'a'))

    def reinforce(self, gv):
        return random.choice(list(gv.TERRITORIES)), str(self.randint(1, 9))

    def attack_from_to(self, gv):
        return random.choice(list(gv.TERRITORIES)), random.choice(list(gv.TERRITORIES)), str(self.randint(1, 9))

    def risk_style_or_chess_style(self, gv):
        return self.choice(('r', 'c'))

    def continue_to_attack(self, gv):
        return self.choice(('y', 'n'))

    def choose_board_layout(self, gv):
        return str(self.randint(2, 8))

    def choose_chess_piece(self, gv):
        return self.choice(('p', 'k', 'b', 'r', 'q'))

    def place_piece(self, gv):
        return (
            # Piece to place
            self.choice(('g', 'p', 'k', 'b', 'r', 'q')),
            # Where to place:
            '{}{}'.format(
                self.choice(('A', 'B', 'C', 'D', 'E', 'F', 'G')),
                self.randint(0, 7)
            ),
        )

    def move_piece(self, gv):
        return (
            # Move from:
            '{}{}'.format(
                self.choice(('A', 'B', 'C', 'D', 'E', 'F', 'G')),
                self.randint(0, 7)
            ),
            # Move to:
            '{}{}'.format(
                self.choice(('A', 'B', 'C', 'D', 'E', 'F', 'G')),
                self.randint(0, 7)
            ),
        )

    def pawn_promoted(self, gv):
        return self.choice(('k', 'b', 'r', 'q'))

    def save(self):
        return '"Nothing to save"'

    def load(self, data):
        return '"Nothing to load"'

    def lose(self, gv):
        gv.prnt('{}: I still must learn!'.format(self.name(gv)))

    def win(self, gv):
        self.save_weights()
        gv.prnt('{}: I will only get stronger!'.format(self.name(gv)))
