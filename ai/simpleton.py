from .base import AiPlayer

import random


class Simpleton(AiPlayer):
    number_of_us = 0

    def name(self, gv):
        type(self).number_of_us += 1
        return 'Simpleton{}'.format(type(self).number_of_us)

    def build_or_attack(self, gv):
        return random.choice(('b', 'a'))

    def reinforce(self, gv):
        return random.choice(gv.TERRITORIES)

    def attack_from_to(self, gv):
        return random.choice(gv.TERRITORIES), str(random.randint(1, 4))

    def risk_style_or_chess_style(self, gv):
        return random.choice(('r', 'c'))

    def continue_to_attack(self, gv):
        return random.choice(('y', 'n'))

    def choose_board_layout(self, gv):
        return str(random.randint(2, 8))

    def choose_chess_piece(self, gv):
        return random.choice(('p', 'k', 'b', 'r', 'q'))

    def place_piece(self, gv):
        return (
            # Piece to place
            random.choice(('p', 'k', 'b', 'r', 'q')),
            # Where to place:
            '{}{}'.format(
                random.choice(('A', 'B', 'C', 'D', 'E', 'F', 'G')),
                random.randint(0, 7)
            ),
        )

    def move_piece(self, gv):
        return (
            # Move from:
            '{}{}'.format(
                random.choice(('A', 'B', 'C', 'D', 'E', 'F', 'G')),
                random.randint(0, 7)
            ),
            # Move to:
            '{}{}'.format(
                random.choice(('A', 'B', 'C', 'D', 'E', 'F', 'G')),
                random.randint(0, 7)
            ),
        )

    def pawn_promoted(self, gv):
        return random.choice(('k', 'b', 'r', 'q'))
