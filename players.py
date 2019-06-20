import global_vars as gv
import random


class PlayersDict(dict):
    """ A dict whose values are objects with a save() method
    """
    def __init__(self, *args):
        dict.__init__(self, args)

    def save(self):
        j = '{'
        for name, value in self.iteritems():
            j += '"%s": %s,' % (name, value.save())
        j = j.rstrip(',') + '}'
        return j

    def load(self, data):
        self.clear()
        for key, value in data.iteritems():
            if gv.DEBUG:
                print data
            self[key] = Player(value['colour'])


class Player(object):
    def __init__(self, colour, ai_instance=None):
        self.colour = colour
        self.ai_instance = ai_instance
        self.is_ai = bool(self.ai_instance)

    def save(self):
        if self.colour == None:
            colour = 'null'
        else:
            colour = self.colour
        j = '{'
        j += '"colour": "%s"' % colour
        j += '}'
        return j

    def load(self, data):
        self.colour = data['colour']


def choose_number_of_players():
    gv.UI.clear_inv_choices()
    gv.UI.set_inv_choice({
            "Please enter a number":
            lambda x: not x.isdigit()})
    gv.UI.set_inv_choice({
            "You must have >=0.":
            lambda x: int(x) <= 0})
    gv.UI.set_inv_choice({
            "6 players is the maximum (have you never played Risk?)":
            lambda x: int(x) > 6})

    gv.N_HUMAN_PLAYERS = int(gv.UI.user_input_check_choices(
            "How many human players are there?", clear=True))

    gv.UI.clear_inv_choices()
    gv.UI.set_inv_choice({
            "Please enter a number":
            lambda x: not x.isdigit()})
    gv.UI.set_inv_choice({
            "Computer players not available yet!":
            lambda x: int(x) is not 0})

    player_module = ''
    while player_module not in ('p', 'play'):
        player_module = gv.UI.user_input_check_choices(
            "Adding computer players:\n"
            "  Type the name of a module in the 'ai' directory to add a player of that type.\n"
            "  Or type '(p)lay' to start playing.", clear=True)
        gv.CHOSEN_AI_MODULES.append(player_module)


def choose_colour(name):
    gv.UI.clear_inv_choices()
    gv.UI.set_inv_choice({
            "Do not disobey me.":
            lambda x: x not in gv.PLAYER_COLORS})

    return gv.UI.user_input_check_choices(name + ", choose a mark from {0}".format(' '.join(gv.PLAYER_COLORS)))


def choose_player_name(iplayer):
    return gv.UI.handle_user_input("Player " + str(iplayer+1) + ":\nWhat would you like to be called?",
                                   cast_lower=False, clear=True)


def setup_players():
    gv.PLAYERS = PlayersDict()
    for iplayer in xrange(gv.N_HUMAN_PLAYERS):
        name = choose_player_name(iplayer)
        gv.PLAYERS[name] = Player(choose_colour(name))

    for ai_class in gv.CHOSEN_AI_MODULES:
        ai_instance = ai_class()
        color = random.choice(gv.PLAYER_COLORS)
        gv.PLAYERS[ai_instance.name()] = Player(color, ai_instance=ai_instance)
