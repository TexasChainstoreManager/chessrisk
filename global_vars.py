ver_maj = 0
ver_min = 32

DEBUG = False
HEADLESS = False

GAME_ID = ''     # 0 is for cmdline games
GAME_STAGE = 'uninitialised'
RESTORE_GAME_STAGE = None
SAVED_GLOBALS = {}
ATTACK_FROM = None
ATTACK_TO = None
PLAYERS_YET_TO_GO = []

CMDLINE = True

# This is an ID for messages passed between processes.
# It allows us to be sure we have the right message.
MESSAGE_NUMBER = 0

_SERVER_STORED_GLOBALS = {}
_RESPONSE = None

PRINT_COUNT = 0
PRINT_RECORD = ''
AI_PLAYERS_ARE_PLAYING = False
AI_PRINT_DELAY = 0.5

RESTORING = False

ANSWERS = {}

CHECK = {'attacker': False, 'defender': False}


# Not currently used, there are problems creating objects with the correct type
# We have used a special-case PlayersDict class instead, since this is the only use
# for a SaveDict so far.
class SaveDict(dict):
    """ A dict whose values are objects with a save() method
    """
    def __init__(self, *args):
        dict.__init__(self, args)

    def save(self):
        j = '{'
        for name, value in self.iteritems():
            j += '"%s": {"type": %s, "value": %s},' % (name, type(value), value.save())
        j = j.rstrip(',') + '}'
        return j

    def load(self, data):
        self.clear()
        for key, value in data.iteritems():
            # Not yet done: we need to use value['type'] to get the class, e.g.
            # Class = globals()[value['type']]
            # init_param = value['value']
            # self[key] = Class[init_param]
            # (what if several params?)
            self[key] = value


class DontSaveDict(dict):
    """ A dict that we don't want to save
    """
    def __init__(self, *args):
        dict.__init__(self, args)

    def save(self):
        return None

    def load(self, data):
        pass


PLAYERS = {}

TERRITORIES = DontSaveDict()
BOARD = None

N_COMP_PLAYERS = 0
N_HUMAN_PLAYERS = 0
ROUND_NUMBER = 0
# Player whose turn it is
CURR_PLAYER = 0

# Keep track of this here because we want it to be saved
# (so we can restore during build turn)
N_REINFORCE_ARMIES = 0

# Stuff we want to keep track of from battle modes
ATTACKER = None
DEFENDER = None
N_DEFEND_ARMIES = None
N_ATTACK_ARMIES = None
# On load, we infer piece counts (n_attack_pieces, n_defend_pieces) and
# piece lists (att_pieces, def_pieces) from chessboard, to ensure consistency.
# Also must infer NRANKS, NFILES.
CHESSBOARD = None

from utils import UserInputter, Printer
UI = UserInputter()
prnt = Printer()

_CLASSIC_CHESSMEN_VALUES = {
                   'p': 1,
                   'k': 3,
                   'b': 3,
                   'r': 5,
                   'q': 9,
                   'g': 0
                   }

_BETTER_CHESSMEN_VALUES = {
                   'p': 1,
                   'k': 2,
                   'b': 2,
                   'r': 5,
                   'q': 9,
                   'g': 0
                   }                   

PLAYER_COLORS = ['bl', 'gr', 'lb', 'pi', 're', 'yl']

CHESSMEN_VALUES = _BETTER_CHESSMEN_VALUES

# Mapping between restore location and a series of
# user inputs to get you to the right checkpoint.
_RESTORE_PATHS = {
    'initial': {'default': '1'},
    'round_start': {'default': '1'},
    'beginning_of_player_turn': {'default': '1'},
    'start_of_build_turn': {'default': '1',
                            '(b)uild or (a)ttack?': 'b'},
    'start_of_attack_turn': {'default': '1',
                             '(b)uild or (a)ttack?': 'a'},
    'before_battle': {'default': '1',
                      '(b)uild or (a)ttack?': 'a',
                      'Choose number of armies to attack with:': '1',
                      'attack from': 'restoring',
                      'attack to': 'restoring'},
    'during_battle': {'default': '1',
                          '(b)uild or (a)ttack?': 'a',
                          'Choose number of armies to attack with:': '1',
                          'attack from': 'restoring',
                          'attack to': 'restoring',
                          'Resolve (R)isk style, or (c)hess style?': 'c',
                          'How many files would you like': '2',
                          'Choose from': 'p',
                          'choose a piece to place from': 'p',
                          'Please choose square': 'A1'
                          },
    'after_battle': {'default': '1',
                          '(b)uild or (a)ttack?': 'a',
                          'Choose number of armies to attack with:': '1',
                          'attack from': 'restoring',
                          'attack to': 'restoring',
                          'Resolve (R)isk style, or (c)hess style?': 'c',
                          'How many files would you like': '2',
                          'Choose from': 'p',
                          'choose a piece to place from': 'p',
                          'Please choose square': 'A1'
                          }
}