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

    def dispatch_message(self, message, gv):
        """This is how we choose which method to run based on message contents."""
        message_dispatch = {
           'resolve (R)isk style, or (c)hess style?': self.risk_style_or_chess_style,
           'press enter to roll': lambda *args: '\n',
           'continue the battle': self.continue_to_attack,
           'how many files': self.choose_board_layout,
           'armies left': self.choose_chess_piece,
           'choose a piece to place': self.choose_piece_to_place,
           'please choose square': self.choose_square_to_place_it,
           'you have no valid moves': lambda *args: 'd',
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
        for k, v in message_dispatch.items():
            if k.lower() in message.lower():
                return lambda: v(gv)
        # If the message doesn't have an associated method, just 'press enter'
        return lambda *args: '\n'

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

    def __multi_move(self, method, tuple_length, tuple_index):
        """This allows running one method for multiple questions. Call this in a question function.

        method: the method to call, it should return a tuple giving the answers to a series of questions.
        tuple_length: the length of the tuple it's supposed to return.
        tuple_index: the element of the tuple that we want to use for THIS answer.
        return value: a function that takes in gv (the globals module) and returns a string - this string is the answer.
        """
        def wrapped(gv):
            result = method(gv)
            if not isinstance(result, tuple) and len(result) != tuple_length:
                raise ValueError('return value of {} must be {}'.format(method, tuple_length))
            return result[tuple_index]
        return wrapped

    def attack_from(self, gv):
        return self.__multi_move(
            self.attack_from_to,
            tuple_length=3,
            tuple_index=0,
        )(gv)

    def attack_to(self, gv):
        return self.__multi_move(
            self.attack_from_to,
            tuple_length=3,
            tuple_index=1,
        )(gv)

    def num_armies_to_attack_with(self, gv):
        return self.__multi_move(
            self.attack_from_to,
            tuple_length=3,
            tuple_index=2,
        )(gv)

    def choose_piece_to_place(self, gv):
        return self.__multi_move(
            self.place_piece,
            tuple_length=2,
            tuple_index=0,
        )(gv)

    def choose_square_to_place_it(self, gv):
        return self.__multi_move(
            self.place_piece,
            tuple_length=2,
            tuple_index=1,
        )(gv)

    def select_territory_to_reinforce(self, gv):
        return self.__multi_move(
            self.reinforce,
            tuple_length=2,
            tuple_index=0,
        )(gv)

    def add_how_many_armies(self, gv):
        return self.__multi_move(
            self.reinforce,
            tuple_length=2,
            tuple_index=1,
        )(gv)

    def choose_piece_to_move(self, gv):
        return self.__multi_move(
            self.move_piece,
            tuple_length=2,
            tuple_index=0,
        )(gv)

    def choose_move_where(self, gv):
        return self.__multi_move(
            self.move_piece,
            tuple_length=2,
            tuple_index=1,
        )(gv)

    def save(self):
        """Convert any state this AI holds into bytes."""
        return NotImplementedError

    def load(self, data):
        """Convert a string of bytes into the state this AI holds."""
        return NotImplementedError
