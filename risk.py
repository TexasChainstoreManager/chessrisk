import math
import random

import global_vars as gv
import chess
import save
import players


TERRITORY_NAMES_FILE = 'territory_names.chr'


class Territory(object):
    def __init__(self, name, owner, narmies, neighbours):
        self.name = name
        self.lname = name.lower()
        self.owner = owner
        self.narmies = narmies
        self.neighbours = neighbours

    def reassign_owner(self, player):
        self.owner = player
        eliminate_dead_players()


class Board(object):

    class TerritoryNotFound(Exception):
        pass    

    def load(self, data):
        self.nrows = int(data['nrows'])
        self.ncols = int(data['ncols'])
        self.nterrs = self.nrows*self.ncols

        self.territory_array = []

        for irow, row in enumerate(data['territory_array']):
            self.territory_array.append([])
            for terr in row:
                self.territory_array[irow].append(Territory(terr['name'], terr['owner'],
                                                            terr['narmies'], None))

        self.figure_out_neighbours()

        gv.TERRITORIES = self.construct_territory_dict()

    def save(self):
        j = '{'

        j += '"nrows": {0}, '.format(self.nrows)
        j += '"ncols": {0}, '.format(self.ncols)

        j += '"territory_array": ['

        for row in self.territory_array:
            j += '['
            for terr in row:
                j += ('{"name": "%s", "owner": "%s", "narmies": %s},'
                      % (terr.name, terr.owner, terr.narmies))
            j = j.rstrip(',') + '],'
        j = j.rstrip(',') + ']'

        j += '}'

        return j

    def create_new(self, terr_names_file=TERRITORY_NAMES_FILE):
        self.nrows = random.randint(3,5)
        self.ncols = random.randint(3,5)
        self.nterrs = self.nrows*self.ncols
        self.territory_array = []
        # Construct the territory array and
        # assign the territory names (read in names from a .txt)
        with open(terr_names_file) as territory_name_file:
            for row in xrange(self.nrows):
                self.territory_array.append([])
                for col in xrange(self.ncols):
                    name = territory_name_file.readline()[:-1].replace('\r', '')
                    self.territory_array[row].append(
                        Territory(name, owner=None, narmies=0, neighbours = None)
                    )

        self.figure_out_neighbours()

        self.initial_territory_assignment()

        self.place_initial_armies()

        # set up global alias to board's territory array (I sure hope this works!)
        gv.TERRITORIES = self.construct_territory_dict()

    # board object should be a list of lists with a territory in each entry
    def __init__(self, load_string=None, terr_names_file=TERRITORY_NAMES_FILE, dummy=None):
        if dummy:
            pass
        elif load_string:
            self.load(load_string)
        else:
            self.create_new(terr_names_file)

    def figure_out_neighbours(self):
        for col in xrange(self.ncols):
            for row in xrange(self.nrows):
                self.territory_array[row][col].neighbours = []
                for col1, row1 in [
                                  (col+1, row),
                                  (col-1, row),
                                  (col, row+1),
                                  (col, row-1),
                                  ]:
                    if (col1 < self.ncols and col1 >= 0
                       and row1 < self.nrows and row1 >= 0):
                        self.territory_array[row][col].neighbours.append(
                                    self.territory_array[row1][col1]
                                    )

    def initial_territory_assignment(self):
        nterrs_empty = self.nterrs
        nterrs_per_player = self.n_initial_terrs_per_player()
        for player in gv.PLAYERS.keys():
            nterrs_left_for_player = nterrs_per_player
            while nterrs_left_for_player > 0 and nterrs_empty > 0:
                row = random.randint(0, self.nrows-1)
                col = random.randint(0, self.ncols-1)
                if self.territory_array[row][col].owner == None:
                    self.territory_array[row][col].owner = player
                    nterrs_left_for_player -= 1
                    nterrs_empty -= 1
        # assign any remainder to the player lucky enough to be at the top
        # of the dictionary. Does not affect # starting armies.
        for col in xrange(self.ncols):
            for row in xrange(self.nrows):
                if self.territory_array[row][col].owner == None:
                    self.territory_array[row][col].owner = gv.PLAYERS.keys()[0]

    def place_initial_armies(self):
        nterrs_per_player = self.n_initial_terrs_per_player()
        for player in gv.PLAYERS.keys():
            n_init_armies = math.floor(nterrs_per_player*2.5)
            for col in xrange(self.ncols):
                for row in xrange(self.nrows):
                    # put an army on each territory
                    if self.territory_array[row][col].owner == player:
                        self.territory_array[row][col].narmies += 1
                        n_init_armies -= 1
            while n_init_armies > 0:
                row = random.randint(0, self.nrows-1)
                col = random.randint(0, self.ncols-1)
                if self.territory_array[row][col].owner == player:
                    self.territory_array[row][col].narmies += 1
                    n_init_armies -= 1

    def n_initial_terrs_per_player(self):
        return self.nterrs/len(gv.PLAYERS.keys())                   

    def territory_by_name(self, name):
        # return the territory object with a given name!
        for col in xrange(self.ncols):
            for row in xrange(self.nrows):
                if self.territory_array[row][col].name == name:
                    return self.territory_array[row][col]
        raise self.TerritoryNotFound

    def construct_territory_dict(self):
        # {name: territory object}

        terrdict = gv.DontSaveDict()
        for col in xrange(self.ncols):
            for row in xrange(self.nrows):
                terrdict[self.territory_array[row][col].lname] = \
                                                self.territory_array[row][col]
        return terrdict
        
    def print_board(self):
        w = 10.
        gv.prnt(' '*int(float(self.ncols)*(w+1.)/2. - 8.) + "~~~ The World ~~~", clear=True)

        for row in xrange(self.nrows):
            subrows = ['']*4

            for col in xrange(self.ncols):
                mark = gv.PLAYERS[self.territory_array[row][col].owner].colour

                namelen = min(len(self.territory_array[row][col].name), int(w-2.))
                namestring = self.territory_array[row][col].name[0:namelen]

                ownerlen = min(len(self.territory_array[row][col].owner), int(w-2.))
                ownerstring = self.territory_array[row][col].owner[0:ownerlen]

                armystring = str(min(self.territory_array[row][col].narmies, 10**int(w-2)))
                armylen = len(armystring)
                
                lpad = lambda x: mark*int(math.floor((w-float(x))/2.)-1)
                rpad = lambda x: mark*int(math.ceil((w-float(x))/2.)-1)
                
                subrows[0] += '+' + '-'*int(w)
                subrows[1] += '|' + lpad(namelen) + ' ' + namestring + ' ' + rpad(namelen)
                subrows[2] += '|' + lpad(armylen) + ' ' + armystring + ' ' + rpad(armylen)
                subrows[3] += '|' + lpad(ownerlen) + ' ' + ownerstring + ' ' + rpad(ownerlen)
                
            subrows[0]+='+'

            for isr in xrange(1,4):
                subrows[isr]+='|'

            for subrow in subrows:
                gv.prnt(subrow)

        gv.prnt(('+' + '-'*int(w))*self.ncols+'+')

        gv.prnt(' '*int(float(self.ncols)*(w+1.)/2. - 8.) + "~~~~~~~~~~~~~~~~~")


def setup_board():
    gv.prnt("Setting up the risk board.")
    gv.prnt("In this version, territories are set up randomly.")
    gv.prnt("In this version, initial army placement is randomised.")
    gv.BOARD = Board()


def count_owned_territories(player):
    n_owned_territories = 0
    for territory in gv.TERRITORIES.keys():
        if gv.TERRITORIES[territory].owner == player:
            n_owned_territories += 1

    return n_owned_territories


def count_army_allowance():
    return int(math.floor(count_owned_territories(gv.CURR_PLAYER)/3.))


def choose_n_armies_to_add(n_reinforce_armies):
    gv.UI.clear_inv_choices()
    gv.UI.set_inv_choice({
            "Please enter a number":
            lambda x: not x.isdigit()})
    gv.UI.set_inv_choice({
            "You can only have whole numbers of armies!":
            lambda x: math.fmod(float(x), 1)})
    gv.UI.set_inv_choice({
            "You don't have that many armies, choose again!": 
            lambda x: int(x) > n_reinforce_armies})

    return int(gv.UI.user_input_check_choices("Add how many armies?"))


def reinforce_a_territory(n_reinforce_armies):
    gv.UI.clear_inv_choices()
    gv.UI.set_inv_choice({
            "Invalid territory choice, try again!":
            lambda x: x not in gv.TERRITORIES.keys()})
    gv.UI.set_inv_choice({
            "Not your territory!":
            lambda x: gv.TERRITORIES[x].owner != gv.CURR_PLAYER})

    territory_choice = gv.UI.user_input_check_choices(
                                "Select a territory to reinforce.")

    n_armies_to_add = choose_n_armies_to_add(n_reinforce_armies)
    gv.TERRITORIES[territory_choice].narmies += n_armies_to_add
    n_reinforce_armies -= n_armies_to_add
    gv.BOARD.print_board()

    return n_reinforce_armies


def process_build_turn():
    gv.N_REINFORCE_ARMIES = count_army_allowance()

    while gv.N_REINFORCE_ARMIES > 0:
        save.checkpoint('during_build_turn')
        gv.prnt("You have " + str(gv.N_REINFORCE_ARMIES) + " armies to place.")
        gv.N_REINFORCE_ARMIES = reinforce_a_territory(gv.N_REINFORCE_ARMIES)


def choose_attack_from():
    gv.prnt("Choose territory to attack from, from the following list:")

    attack_from_list = []
    for territory in gv.TERRITORIES.values():
        if territory.owner == gv.CURR_PLAYER and territory.narmies > 1:
            for neighbour in territory.neighbours:
                if neighbour.owner != gv.CURR_PLAYER:
                    gv.prnt(territory.name)
                    attack_from_list.append(territory.lname)
                    break

    gv.UI.clear_inv_choices()
    gv.UI.set_inv_choice({
            "Can't attack from there, choose again!":
            lambda x: x not in attack_from_list})

    return gv.UI.user_input_check_choices('')


def choose_attack_to():
    gv.prnt("Choose territory to attack, from the following list:")

    attack_to_list = []
    for territory in gv.TERRITORIES[gv.ATTACK_FROM].neighbours:
        if territory.owner != gv.CURR_PLAYER:
            gv.prnt(territory.name)
            attack_to_list.append(territory.lname)

    gv.UI.clear_inv_choices()
    gv.UI.set_inv_choice({
            "Can't attack there, choose again!":
            lambda x: x not in attack_to_list})

    return gv.UI.user_input_check_choices('')


def choose_narmies_to_attack_with():
    gv.prnt("There are " + str(gv.TERRITORIES[gv.ATTACK_FROM].narmies-1)
                + " armies available for attack.")

    gv.UI.clear_inv_choices()
    gv.UI.set_inv_choice({
            "Please enter a number":
            lambda x: not x.isdigit()})
    gv.UI.set_inv_choice({
        "You can only have whole numbers of armies!":
        lambda x: math.fmod(float(x), 1)})
    gv.UI.set_inv_choice({
        "You must leave at least one army at home, try again!":
        lambda x: int(x) >= gv.TERRITORIES[gv.ATTACK_FROM].narmies})

    return int(gv.UI.user_input_check_choices(
                    "Choose number of armies to attack with:"))


def attackable_neighbours_exist():
    able_to_attack = False
    for unused_key, territory in gv.TERRITORIES.items():
        if territory.owner == gv.CURR_PLAYER and territory.narmies > 1:
            for neighbour in territory.neighbours:
                if neighbour.owner != gv.CURR_PLAYER:
                    able_to_attack = True
    if not able_to_attack:
        gv.prnt("No possiblities for attack!")
    return able_to_attack


def process_attack_turn():
    save.checkpoint('start_of_attack_turn')
    if not attackable_neighbours_exist() and not gv.RESTORING:
        gv.prnt("Not possible to attack! Build instead.")
        process_build_turn()

    while attackable_neighbours_exist() or gv.RESTORING:
        if not gv.RESTORING:
            gv.ATTACK_FROM = choose_attack_from()
            gv.ATTACK_TO = choose_attack_to()
            gv.N_ATTACK_ARMIES = choose_narmies_to_attack_with()
            gv.N_DEFEND_ARMIES = gv.TERRITORIES[gv.ATTACK_TO].narmies
            gv.DEFENDER = gv.TERRITORIES[gv.ATTACK_TO].owner
        else:
            gv.ATTACK_FROM = gv.SAVED_GLOBALS['ATTACK_FROM']
            gv.ATTACK_TO = gv.SAVED_GLOBALS['ATTACK_TO']
            gv.N_ATTACK_ARMIES = gv.SAVED_GLOBALS['N_ATTACK_ARMIES']
            gv.N_DEFEND_ARMIES = gv.SAVED_GLOBALS['N_DEFEND_ARMIES']
            gv.DEFENDER = gv.SAVED_GLOBALS['DEFENDER']
            gv.CURR_PLAYER = gv.SAVED_GLOBALS['CURR_PLAYER']
        narmies_attacker, narmies_defender = chess.play_chess(
                        gv.N_ATTACK_ARMIES,
                        gv.N_DEFEND_ARMIES,
                        gv.CURR_PLAYER,
                        gv.DEFENDER
                        )
        if narmies_defender == 0:
            gv.prnt("{0} defeated!".format(gv.TERRITORIES[gv.ATTACK_TO].owner))
            gv.TERRITORIES[gv.ATTACK_FROM].narmies -= gv.N_ATTACK_ARMIES
            gv.TERRITORIES[gv.ATTACK_TO].narmies = narmies_attacker
            gv.TERRITORIES[gv.ATTACK_TO].reassign_owner(gv.CURR_PLAYER)
        else:
            gv.prnt("{0} repelled!".format(gv.CURR_PLAYER))
            gv.TERRITORIES[gv.ATTACK_FROM].narmies -= \
                                gv.N_ATTACK_ARMIES - narmies_attacker
            gv.TERRITORIES[gv.ATTACK_TO].narmies = narmies_defender

        raw_input('<press enter>')
        save.checkpoint('after_battle')
        gv.BOARD.print_board()

        gv.prnt("Continue to attack, (y)es or (n)o?")
        attack_some_more = False
        while attack_some_more is False:
            response = gv.UI.handle_user_input('')
            if response in ['y', 'yes']:
                attack_some_more = True
            if response in ['n', 'no']:
                  return 'Chickened out'


def eliminate_dead_players():
    if gv.RESTORING:
        for player in gv.PLAYERS.keys():
            if count_owned_territories(player) == 0:
                gv.prnt("{0} is out!".format(player))
                del gv.PLAYERS[player]
    else:
        pass


def check_for_victory():
    if gv.RESTORING:
        return False
    else:
        if len(gv.PLAYERS) == 1:
            gv.prnt("{0} wins!".format(gv.PLAYERS.keys()[0]))
            return True
        else:
            return False


def create_dummy_globals():
    # Must create dummy globals so their load() method can be run
    # Can't define this in global_vars because circular imports
    gv.BOARD = Board(dummy=True)
    gv.PLAYERS = players.PlayersDict()

