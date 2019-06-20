"""
This class defines the methods your AI class need to implement.
Anything with a NotImplementedError, you need to implement.

Each method has access to the global variables.

There's a lot of havok you can do with that, please play fair!

There are two global variables you'll be mostly interested in:
  gv.BOARD: An object containing BOARD.territory_array, a 2d array of Territory objects.
    Territory objects have a name, owner, narmies, and neighbours.
  gv.CHESSBOARD: A 2d array of characters, either:
    - ' ' for no piece
    - the string name of the piece, if one is present (e.g. 'g' for king)

Also, for convenience:
  gv.TERRITORIES: A dictionary of territories keyed by name.

NB: Store variables globally in modules to get them
shared between instances of different AI players.
"""


class AiPlayer(object):

    def __init__(self):
        # These are tuples of answers, to allow you to write methods
        # that answer multiple related questions at once.
        self.__placement = None
        self.__move_piece = None
        self.__reinforce = None
        self.__attack_from_to = None

    def dispatch_message(self, message):
        """This is how we choose which method to run based on message contents."""
        message_dispatch = {
           'resolve (R)isk style, or (c)hess style?': self.risk_style_or_chess_style,
           'press enter to roll': lambda: '\n',
           'continue the battle': self.continue_to_attack,
           'how many files': self.choose_board_layout,
           'armies left': self.choose_chess_piece,
           'choose a piece to place': self.choose_piece_to_place,
           'please choose square': self.choose_square_to_place_it,
           'you have no valid moves': lambda: 'd',
           'choose a piece to move by entering its coordinates': self.choose_piece_to_move,
           'move to which square': self.choose_move_where,
           'pawn promoted': self.pawn_promoted,
           'add how many armies': self.add_how_many_armies,
           'select a territory to reinforce': self.select_territory_to_reinforce,
           'from:': self.attack_from,
           'to:': self.attack_to,
           'number of armies to attack with': self.num_armies_to_attack_with,
           'continue': self.continue_to_attack,  # to attack
           '(b)uild or (a)ttack': self.build_or_attack,
        }
        for k, v in message_dispatch:
            if k.lower() in message.lower():
                return v
        # If the message doesn't have an associated method, just 'press enter'
        return lambda: '\n'

    def name(self, gv):
        raise NotImplementedError

    def build_or_attack(self, gv):
        raise NotImplementedError

    def reinforce(self, gv):
        # Return territory to reinforce, and how many armies
        raise NotImplementedError

    def attack_from_to(self, gv):
        # Return territory to attack from and to and how many armies, as a tuple
        raise NotImplementedError

    def risk_style_or_chess_style(self, gv):
        raise NotImplementedError

    def continue_to_attack(self, gv):
        raise NotImplementedError

    def choose_board_layout(self, gv):
        raise NotImplementedError

    def choose_chess_piece(self, gv):
        raise NotImplementedError

    def place_piece(self, gv):
        # Return a piece to place AND where to place it, as a tuple
        raise NotImplementedError

    def move_piece(self, gv):
        # Return the coords of a piece to move AND where to move it, as a tuple
        raise NotImplementedError

    def pawn_promoted(self, gv):
        raise NotImplementedError

    def attack_from(self, gv):
        self.__attack_from_to = self.attack_from_to(gv)
        return self.__attack_from_to[0]

    def attack_to(self, gv):
        return self.__attack_from_to[1]

    def num_armies_to_attack_with(self, gv):
        return self.__attack_from_to[2]

    # def press_enter_to_roll(self):
    #     raise NotImplementedError

    # def hide_screen_and_press_enter(self):
    #     raise NotImplementedError

    def choose_piece_to_place(self, gv):
        self.__placement = self.place_piece(gv)
        return self.__placement[0]

    def choose_square_to_place_it(self, gv):
        return self.__placement[1]

    def select_territory_to_reinforce(self, gv):
        self.__reinforce = self.reinforce(gv)
        return self.__reinforce[0]

    def add_how_many_armies(self, gv):
        return self.__reinforce[1]

    def choose_piece_to_move(self, gv):
        self.__move_piece = self.move_piece(gv)
        return self.__move_piece[0]

    def choose_move_where(self, gv):
        return self.__move_piece[1]
