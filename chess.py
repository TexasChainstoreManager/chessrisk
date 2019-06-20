import math
import random
import re
from time import sleep

from copy import deepcopy

import global_vars as gv
import save

NRANKS = 8
NFILES = 0


def play_chess(n_attack_armies, n_defend_armies, attacker, defender):
    save.checkpoint('before_battle')
    gv.UI.clear_inv_choices()
    gv.UI.set_inv_choice({
        "Please enter (r) or (c).":
        lambda x: x.lower() not in ['r', 'c', 'risk', 'chess']})

    style = gv.UI.handle_user_input("Resolve (R)isk style, or (c)hess style?")
    if style in ['r', 'risk']:
        result = risk_style(n_attack_armies, 
                            n_defend_armies, 
                            attacker, 
                            defender)
    if style in ['c', 'chess']:
        result = chess_style(n_attack_armies, 
                             n_defend_armies, 
                             attacker, 
                             defender)
    return result


def risk_style(n_attack_armies, n_defend_armies, attacker, defender):
    continue_fight = True
    while continue_fight:
        attack_dice = []
        defend_dice = []
        for i in range(min(n_attack_armies, 3)):
            attack_dice.append(random.randint(1,6))
        for i in range(min(n_defend_armies, 2)):
            defend_dice.append(random.randint(1,6))

        gv.UI.handle_user_input("{0}, press enter to roll:".format(attacker), player=attacker)
        for attd in attack_dice:
            gv.UI.handle_user_input("{0}".format(attd), player=attacker)
            if gv.AI_PLAYERS_ARE_PLAYING:
                sleep(gv.AI_PRINT_DELAY)
        gv.UI.handle_user_input("{0}, press enter to roll:".format(defender))
        for defd in defend_dice:
            gv.UI.handle_user_input("{0}".format(defd), player=defender)
            if gv.AI_PLAYERS_ARE_PLAYING:
                sleep(gv.AI_PRINT_DELAY)

        defend_dice.sort(reverse=True)
        attack_dice.sort(reverse=True)

        for dice in xrange(min(n_attack_armies, n_defend_armies,2)):
            if attack_dice[dice] > defend_dice[dice]:
                n_defend_armies = max(n_defend_armies-1, 0)
            else:
                n_attack_armies = max(n_attack_armies-1, 0)

        gv.prnt("{0}: {1}".format(attacker, str(n_attack_armies)))
        gv.prnt("{0}: {1}".format(defender, str(n_defend_armies)))
        if n_attack_armies == 0 or n_defend_armies == 0:
            continue_fight = False

        if continue_fight:
            carry_on = gv.UI.handle_user_input("Continue the battle, (y)es or (n)o?")
            if carry_on in ['y', 'yes']:
                continue_fight = True
                gv.prnt.clear_output()
            elif carry_on in ['n', 'no']:
                continue_fight = False

    return n_attack_armies, n_defend_armies


def chess_style(n_attack_armies, n_defend_armies, attacker, defender):
    gv.CHECK = {'attacker': False, 'defender': False}
    hide_message = '---{}, hide screen from {} and press enter---'
    fight_on_message = '---{} ({}), press enter to fight on---'

    if gv.RESTORING:
        gv.CHESSBOARD = gv.SAVED_GLOBALS['CHESSBOARD']
        attacker = gv.SAVED_GLOBALS['CURR_PLAYER']
        defender = gv.SAVED_GLOBALS['DEFENDER']
        def_pieces, att_pieces = get_pieces_from_board()
    else:
        # Defender chooses board layout
        choose_board_layout(defender)

        # Defender chooses pieces first, then attacker
        gv.UI.handle_user_input(hide_message.format(defender, attacker), clear=True, player=defender)
        def_pieces = choose_pieces(defender, n_defend_armies)
        gv.UI.handle_user_input(hide_message.format(attacker, defender), clear=True, player=attacker)
        att_pieces = choose_pieces(attacker, n_attack_armies)

        # Defender chooses first
        # Board layout: bottom half of board, defender's
        # unplaced pieces arranged at top
        gv.UI.handle_user_input(hide_message.format(defender, attacker), clear=True, player=defender)
        choose_placement('defender', defender, def_pieces)

        # Attacker chooses placement
        # Board layout: top half of board, attacker's
        # unplaced pieces arranged at top
        gv.UI.handle_user_input(hide_message.format(attacker, defender), clear=True, player=attacker)
        choose_placement('attacker', attacker, att_pieces)

    # Fight!
    # Attacker makes first move
    withdraw = False
    while def_pieces and att_pieces and not withdraw:
        save.checkpoint('during_battle')
#        gv.UI.handle_user_input(fight_on_message.format(attacker, 'attacker'), clear=True, player=attacker)

        ####
        # Attacker's move
        ###
        result = process_move('attacker', attacker, def_pieces)
        # Recalc the pieces lists. There may have been promotions.
        # This is a lazy programmer's way of ensuring accuracy.
        def_pieces, att_pieces = get_pieces_from_board()

        if result == 'withdraw':
            withdraw = True
        elif result == 'checkmate':
            def_pieces = []
            break
        if stalemate(att_pieces, def_pieces):
            break

        ####
        # Defender's move
        ###
#        gv.UI.handle_user_input(fight_on_message.format(defender, 'defender'), clear=True, player=defender)
        result = process_move('defender', defender, att_pieces)
        # Recalc the pieces lists. There may have been promotions.
        # This is a lazy programmer's way of ensuring accuracy.
        def_pieces, att_pieces = get_pieces_from_board()

        if result == 'checkmate':
            att_pieces = []
            break
        if stalemate(att_pieces, def_pieces):
            break
        # Board layout: Entire board. Pieces captured by
        # attacker are placed at top, defender bottom.
        # 'attacker' written at top, 'DEFENDER' at bottom


    n_attack_armies, n_defend_armies = \
        count_remaining_armies(att_pieces, def_pieces)

    return n_attack_armies, n_defend_armies


def stalemate(att_pieces, def_pieces):
    if att_pieces == ['g'] and def_pieces == ['g']:
        gv.prnt('STALEMATE!')
        return True
    return False


def choose_board_layout(player):
    """
    Board is stored as a list of lists.
    List is gv.CHESSBOARD[file_][rank].
    Each square contains a single character, either ' '
    or one of the characters representing a piece.
    Defender's pieces are upper-case, attackers are 
    lower-case.
    """
    global NRANKS, NFILES
    
    gv.prnt('{0}, choose the board layout.'.format(player))
    gv.prnt('You must have 8 ranks.')
    gv.UI.clear_inv_choices()
    gv.UI.set_inv_choice({
        "Please enter a number":
        lambda x: not x.isdigit()})
    gv.UI.set_inv_choice({
        "You can only have whole numbers of files!":
        lambda x: math.fmod(float(x), 1)})
    gv.UI.set_inv_choice({
        "Can't have more than 8 files.":
        lambda x: int(x) > 8})
    gv.UI.set_inv_choice({
        "Can't have less than 2 files.":
        lambda x: int(x) < 2})

    NFILES = int(
        gv.UI.user_input_check_choices(
            "How many files would you like (2 to 8)?",
            player=player,
        )
    )

    gv.CHESSBOARD = []
    for i in xrange(NFILES):
        gv.CHESSBOARD += [[' ']*NRANKS]

    print_board('all', clear=True)


def print_board(part, clear=False):
    """
    gv.CHESSBOARD[file_][rank]
    ranks are numbers 0-8
    ranks are up-down
    files are letters A-
    files are side-side
    """
    if clear:
        gv.prnt.clear_output()
    if part == 'all':
        prt = (0,7)
    elif part == 'top':
        prt = (0,3)
    elif part == 'bottom':
        prt = (4,7)
    else:
        raise Exception('Unexpected part of the board!')

    for irank in xrange(prt[0], prt[1]+1):
        if irank % 2:
            colour = ' '
        else:
            colour = '#'
        creamy_filling = {'top': '', 'mid': '', 'bot': ''}
        for ifile_ in xrange(NFILES):
            square = gv.CHESSBOARD[ifile_][irank]
            if colour == '#':
                colour = ' '
            elif colour == ' ':
                colour = '#'
            else:
                raise Exception('Unexpected colour!')
            creamy_filling['top'] += '|{0} {0}'.format(colour)
            creamy_filling['mid'] += '| {1} '.format(colour, square)
            creamy_filling['bot'] += '|{0} {0}'.format(colour)
        gv.prnt(' ' + '+---'*(NFILES) + '+')
        gv.prnt(' ' + creamy_filling['top'] + '|')
        gv.prnt(str(irank) + creamy_filling['mid'] + '|')
        gv.prnt(' ' + creamy_filling['bot'] + '|')
    gv.prnt(' ' + '+---'*(NFILES) + '+')

    files_string = ''
    for ifile_ in xrange(NFILES):
        file_name = chr(97 + ifile_).upper()
        files_string += '  {0} '.format(file_name)
    gv.prnt(' {0} '.format(files_string))
    if gv.AI_PLAYERS_ARE_PLAYING:
        sleep(gv.AI_PRINT_DELAY)


def choose_pieces(player, n_armies):
    gv.prnt('{0}, choose your pieces!'.format(player))
    gv.prnt('Values of pieces: ')
    gv.prnt('---------------------')
    gv.prnt('Pawn: {0}'.format(gv.CHESSMEN_VALUES['p']))
    gv.prnt('Knight: {0}'.format(gv.CHESSMEN_VALUES['k']))
    gv.prnt('Bishop: {0}'.format(gv.CHESSMEN_VALUES['b']))
    gv.prnt('Rook: {0}'.format(gv.CHESSMEN_VALUES['r']))
    gv.prnt('Queen: {0}'.format(gv.CHESSMEN_VALUES['q']))
    gv.prnt('---------------------')
    gv.prnt('You always start with one kin(g).')
    gv.prnt('Choose from (p)awn, (k)night, (b)ishop, (r)ook, (q)ueen:')

    gv.UI.clear_inv_choices()
    gv.UI.set_inv_choice({
        "Please enter p, k, b, r or q.":
        lambda x: x not in ['p', 'k', 'b', 'r', 'q']})
    gv.UI.set_inv_choice({
        "Not enough armies for that piece!":
        lambda x: gv.CHESSMEN_VALUES[x] > n_armies})

    pieces = ['g']
    while n_armies > 0:
        pieces.append(gv.UI.user_input_check_choices('{0} armies left.'.format(n_armies), player=player))
        n_armies -= gv.CHESSMEN_VALUES[pieces[-1]]
        gv.prnt("Your forces: {0}".format(pieces))

    return pieces


def choose_placement(player_type, player, pieces):
    unplaced_pieces = deepcopy(pieces)

    if player_type== 'attacker':
        gv.prnt('As the attacker, you start in the top half of the board:')
        board_part = 'top'
        valid_ranks = '[0-3]'
    elif player_type == 'defender':
        board_part = 'bottom'
        valid_ranks = '[4-7]'
    else:
        raise Exception('Invalid player_type.')

    while unplaced_pieces:
        gv.prnt('As the {}, you start in the {} half of the board:'.format(player_type, board_part), clear=True)
        print_board(board_part)

        gv.UI.clear_inv_choices()
        gv.UI.set_inv_choice({
            "Choose from {0}.".format(unplaced_pieces):
            lambda x: x not in unplaced_pieces})

        piece = gv.UI.user_input_check_choices('{0}: choose a piece to place from:'
                                                '\n{1}\n'.format(player, 
                                                                 unplaced_pieces), player=player)

        max_file = chr(NFILES+96)
        
        gv.UI.clear_inv_choices()
        gv.UI.set_inv_choice({
            "Invalid choice.\nPlease enter a string of the "
            "form XY with X in [A-{0}a-{1}] and Y in {2}."
            .format(max_file.upper(), max_file.lower(), valid_ranks):
            lambda x: not re.match(r'[a-{0}]{1}'
                                     .format(max_file.lower(), valid_ranks), x)})

        pos = gv.UI.user_input_check_choices('Please choose square, example: "G3"', player=player)

        file_, rank = coords(pos)
        if gv.CHESSBOARD[file_][rank] != ' ':
            gv.prnt("There's already a piece there, try again")
            continue

        if player_type == 'attacker':
            piece_symbol = piece.lower()
        elif player_type == 'defender':
            piece_symbol = piece.upper()
        gv.CHESSBOARD[file_][rank] = piece_symbol
        unplaced_pieces.remove(piece)

    gv.prnt(('---------------YOUR FINAL LAYOUT---------------'))
    print_board(board_part)
    gv.prnt(('-----------------------------------------------'))


def process_move(player_type, player, opponents_pieces):

    print_board('all', clear=True)

    if gv.CHECK[player_type]:
        gv.prnt('~~~ CHECK! ~~~')

    # If it's the attacker's turn, 
    # give them the option to withdraw.
    if player_type == 'attacker':
        withdraw_string = " or 'w' to withdraw"
    elif player_type == 'defender':
        withdraw_string = ""
    else:
        raise Exception('Invalid player type')

#    max_rank = chr(len(chessboard[0])+97)

    # Check whether there are any valid moves for this player
    if not all_valid_moves(player_type):
        gv.UI.clear_inv_choices()
        gv.UI.set_inv_choice({
            "Please enter either 'w' or 'd'":
            lambda x: x not in ['w', 'd', 'withdraw', 'do nothing']})
        pos = gv.UI.user_input_check_choices("{0}, you have no valid moves available,"
                                             "enter 'd' to do nothing{1}."
                                             .format(player, withdraw_string), player=player)
        if pos in ['w', 'withdraw']:
            return 'withdraw'
        else:
            return False

    valid_squares = get_coords_by_player_type(player_type)

    # Get the player's choice of piece to move & calculate valid moves
    valid_moves = None
    while not valid_moves:    
        gv.UI.clear_inv_choices()
        if player_type == 'attacker':
            gv.UI.set_inv_choice({
                "No piece at that position!":
                lambda x: coords(x) not in valid_squares 
                          and x not in ['w', 'withdraw']})
        else:
            gv.UI.set_inv_choice({
                "No piece at that position!":
                lambda x: coords(x) not in valid_squares})

        pos = gv.UI.user_input_check_choices("{} ({}), choose a piece to move by "
                                             "entering its coordinates{}:"
                                             .format(player, player_type, withdraw_string), player=player)
    
        if pos in ['w', 'withdraw']:
            return 'withdraw'
    
        file_, rank = coords(pos)
    
        piece = gv.CHESSBOARD[file_][rank]
    
        valid_moves = valid_moves_one_piece(player_type, file_, rank, piece)

        if not valid_moves:
            gv.prnt("No valid moves for that piece, try again!")

    # Get the player's choice of move
    gv.UI.clear_inv_choices()
    gv.UI.set_inv_choice({
        "Illegal move, choose properly.":
        lambda x: coords(x) not in valid_moves})

    move_to = gv.UI.user_input_check_choices('Move to which square?', player=player)

    file_to, rank_to = coords(move_to)

    # Move the piece and capture any current occupant
    if gv.CHESSBOARD[file_to][rank_to] != ' ':
        captured_piece = gv.CHESSBOARD[file_to][rank_to]
        gv.UI.handle_user_input('{0} captured!'.format(captured_piece), player=player)
        opponents_pieces.remove(captured_piece.lower())
    gv.CHESSBOARD[file_to][rank_to] = piece
    gv.CHESSBOARD[file_][rank] = ' '
    if check_or_mate(player_type):
        gv.prnt('CHECKMATE!')
        return 'checkmate'

    if piece.lower() == 'p':
        promote_pawn(player_type, file_to, rank_to, player)

    # We return False because by this point,
    # withdraw has not been selected.
    return False


def check_or_mate(active_player_type):
    if active_player_type == 'attacker':
        inactive_player_type = 'defender'
    elif active_player_type == 'defender':
        inactive_player_type = 'attacker'

    # First, is opponent in check?
    gv.CHECK[inactive_player_type] = check_for_check(active_player_type)

    # Second, if there are no valid moves for the opponent, it's checkmate
    return not bool(all_valid_moves(inactive_player_type))

    #
    # # Second, perform all possible moves and check if we are still in check
    # # Monkey patch the board
    # mate_avoided = False
    # real_board_state = deepcopy(gv.CHESSBOARD)
    # for file_, rank in get_coords_by_player_type(other_player_type):
    #     piece = real_board_state[file_][rank]
    #     # try moves one by one for this piece
    #     for file_to, rank_to in valid_moves_one_piece(other_player_type, file_, rank, piece):
    #         gv.CHESSBOARD[file_to][rank_to] = piece
    #         gv.CHESSBOARD[file_][rank] = ' '
    #         # If other player is now not in check, mate has been avoided
    #         mate_avoided = not check_for_check(player_type) or mate_avoided
    #         gv.CHESSBOARD = deepcopy(real_board_state)
    #
    # return not mate_avoided


def check_for_check(active_player_type):
    if active_player_type == 'attacker':
        inactive_king_coords = get_coords_by_piece_type('G')
    elif active_player_type == 'defender':
        inactive_king_coords = get_coords_by_piece_type('g')

    for kcoords in inactive_king_coords:
        if kcoords in all_valid_moves(active_player_type, checking_check=True):
            return True
    return False


def promote_pawn(player_type, file_, rank, player):
    global NRANKS
    promote = False
    if player_type == 'attacker':
        if rank == NRANKS-1:
            promote = True
    if player_type == 'defender':
        if rank == 0:
            promote = True
    if promote:
        gv.UI.clear_inv_choices()
        gv.UI.set_inv_choice({
            "Please enter k, b, r or q.":
            lambda x: x not in ['k', 'b', 'r', 'q']})
        gv.CHESSBOARD[file_][rank] = gv.UI.user_input_check_choices(
            'Pawn promoted! Choose (k)night, (b)ishop, (r)ook or (q)ueen.', player=player)
        if player_type == 'defender':
            gv.CHESSBOARD[file_][rank] = gv.CHESSBOARD[file_][rank].upper()


def all_valid_moves(player_type, checking_check=False):
    valid_moves = []
    for file_, unused in enumerate(gv.CHESSBOARD):
        for rank, piece in enumerate(gv.CHESSBOARD[file_]):
            if (player_type == 'attacker' and piece.islower()
             or player_type == 'defender' and piece.isupper()):
                valid_moves.extend(valid_moves_one_piece(player_type,
                                                         file_, 
                                                         rank, 
                                                         piece,
                                                         checking_check=checking_check))
    return valid_moves


def valid_moves_one_piece(player_type, file_, rank, piece, checking_check=False):
    """
    Given a piece and its position, return a 
    list of the squares it can move to. Taking in 
    player_type is more explicit and allows us to 
    double-check we are moving that player's piece.
    """
    if player_type == 'attacker':
        opp_player_type = 'defender'
        if piece.isupper():
            raise Exception('Attacker moving invalid piece')
    elif player_type == 'defender':
        opp_player_type = 'attacker'
        if piece.islower():
            raise Exception('Defender moving invalid piece')        
    else:
        raise Exception('Invalid player_type')

    function_switcher = {'p': pawn_valid_moves,
                         'k': knight_valid_moves,
                         'b': bishop_valid_moves,
                         'r': rook_valid_moves,
                         'q': queen_valid_moves,
                         'g': king_valid_moves}

    valid_moves = function_switcher[piece.lower()](player_type, file_, rank)

    # Try all valid moves and only keep those that result in no check
    # In the special case that we are checking for check, it doesn't matter if moving would result in check
    if not checking_check:
        valid_moves_including_check = []
        real_board_state = deepcopy(gv.CHESSBOARD)
        if valid_moves:
            for file_to, rank_to in valid_moves:
                gv.CHESSBOARD[file_to][rank_to] = piece
                gv.CHESSBOARD[file_][rank] = ' '
                if not check_for_check(opp_player_type):
                    valid_moves_including_check.append((file_to, rank_to))
                gv.CHESSBOARD = deepcopy(real_board_state)
    else:
        valid_moves_including_check = valid_moves
    #
    # mate_avoided = False
    # real_board_state = deepcopy(gv.CHESSBOARD)
    # for file_, rank in get_coords_by_player_type(other_player_type):
    #     piece = real_board_state[file_, rank]
    #     # try moves one by one for this piece
    #     for file_to, rank_to in valid_moves_one_piece(other_player_type, file_, rank, piece):
    #         gv.CHESSBOARD[file_to][rank_to] = piece
    #         gv.CHESSBOARD[file_][rank] = ' '
    #         # If other player is now not in check, mate has been avoided
    #         mate_avoided = not check_for_check(player_type) or mate_avoided
    #         gv.CHESSBOARD = deepcopy(real_board_state)

    return valid_moves_including_check
    
    
def pawn_valid_moves(player_type, file_, rank):
    global NRANKS

    def get_moves(dirn, upper_lower):
#        adj = (file_, min(max(rank+dirn, 0), NRANKS))
        adj = (file_, rank+dirn)
        # Can only move forward into empty square
        if gv.CHESSBOARD[adj[0]][adj[1]] == ' ':
            valid_moves.append(adj)

        # Any diagonally-adjacent squares with an
        # opposite-case letter can be moved into
        for ifile_, irank in [(file_-1, rank+dirn),
                              (file_+1, rank+dirn)]:
            if (irank < NRANKS and irank >= 0
            and ifile_ < NFILES and ifile_ >= 0
            and getattr(gv.CHESSBOARD[ifile_][irank], 'is' + upper_lower)()):  # .isupper() or .islower()
                valid_moves.append((ifile_, irank))

    valid_moves = []
    if player_type == 'attacker':
        # Can only move to higher-numbered ranks
        if rank < NRANKS-1:
            get_moves(+1, 'upper')
        else:
            valid_moves = []
        
    elif player_type == 'defender':
        # Can only move to lower-numbered ranks
        if rank > 0:
            get_moves(-1, 'lower')
        else:
            valid_moves = []

    else:
        raise Exception('Invalid player type')

    return valid_moves
    
    
def knight_valid_moves(player_type, file_, rank):
    valid_moves = [(file_+2, rank+1),
                   (file_+1, rank+2),
                   (file_+2, rank-1),
                   (file_+1, rank-2),
                   (file_-2, rank+1),
                   (file_-1, rank+2),
                   (file_-2, rank-1),
                   (file_-1, rank-2)]

    # Remove any that are off the board
    valid_moves = [move for move in valid_moves if
                   (move[0] < NFILES and move[0] >= 0 and
                    move[1] < NRANKS and move[1] >= 0)]

    # Remove any that contain a friendly unit
    if player_type == 'attacker':
        valid_moves = [move for move in valid_moves
                       if not gv.CHESSBOARD[move[0]][move[1]].islower()]
    if player_type == 'defender':
        valid_moves = [move for move in valid_moves
                       if not gv.CHESSBOARD[move[0]][move[1]].isupper()]

    return valid_moves


def bishop_valid_moves(player_type, file_, rank):
    valid_moves = []
    if player_type == 'attacker':
        ours = 'lower'
        theirs = 'upper'
    elif player_type == 'defender':
        ours = 'upper'
        theirs = 'lower'
    else:
        raise Exception('Invalid player_type')

    # project ahead from this square until you hit a friendly unit (exclusive)
    # or friendly unit (inclusive) or edge of map
    ifile_ = file_ + 1
    irank = rank + 1
    while ifile_ < NFILES and irank < NRANKS:
        if getattr(gv.CHESSBOARD[ifile_][irank], 'is' + ours)():
            break
        valid_moves.append((ifile_, irank))
        if getattr(gv.CHESSBOARD[ifile_][irank], 'is' + theirs)():
            break
        ifile_ += 1
        irank += 1

    ifile_ = file_ - 1
    irank = rank + 1
    while ifile_ >= 0 and irank < NRANKS:
        if getattr(gv.CHESSBOARD[ifile_][irank], 'is' + ours)():
            break
        valid_moves.append((ifile_, irank))
        if getattr(gv.CHESSBOARD[ifile_][irank], 'is' + theirs)():
            break
        ifile_ -= 1
        irank += 1

    ifile_ = file_ + 1
    irank = rank - 1
    while ifile_ < NFILES and irank >= 0:
        if getattr(gv.CHESSBOARD[ifile_][irank], 'is' + ours)():
            break
        valid_moves.append((ifile_, irank))
        if getattr(gv.CHESSBOARD[ifile_][irank], 'is' + theirs)():
            break
        ifile_ += 1
        irank -= 1

    ifile_ = file_ - 1
    irank = rank - 1
    while ifile_ >= 0 and irank >= 0:
        if getattr(gv.CHESSBOARD[ifile_][irank], 'is' + ours)():
            break
        valid_moves.append((ifile_, irank))
        if getattr(gv.CHESSBOARD[ifile_][irank], 'is' + theirs)():
            break
        ifile_ -= 1
        irank -= 1

    return valid_moves


def rook_valid_moves(player_type, file_, rank):
    valid_moves = []
    if player_type == 'attacker':
        ours = 'lower'
        theirs = 'upper'
    elif player_type == 'defender':
        ours = 'upper'
        theirs = 'lower'
    else:
        raise Exception('Invalid player_type')
    
    # project ahead from this square until you hit an enemy unit (exclusive)
    # or friendly unit (inclusive) or edge of map
    for ifile_ in xrange(file_+1, NFILES):
        if getattr(gv.CHESSBOARD[ifile_][rank], 'is' + ours)():
            break
        valid_moves.append((ifile_, rank))
        if getattr(gv.CHESSBOARD[ifile_][rank], 'is' + theirs)():
            break

    for irank in xrange(rank+1, NRANKS):
        if getattr(gv.CHESSBOARD[file_][irank], 'is' + ours)():
            break
        valid_moves.append((file_, irank))
        if getattr(gv.CHESSBOARD[file_][irank], 'is' + theirs)():
            break

    for ifile_ in xrange(file_-1, -1, -1):
        if getattr(gv.CHESSBOARD[ifile_][rank], 'is' + ours)():
            break
        valid_moves.append((ifile_, rank))
        if getattr(gv.CHESSBOARD[ifile_][rank], 'is' + theirs)():
            break

    for irank in xrange(rank-1, -1, -1):
        if getattr(gv.CHESSBOARD[file_][irank], 'is' + ours)():
            break
        valid_moves.append((file_, irank))
        if getattr(gv.CHESSBOARD[file_][irank], 'is' + theirs)():
            break

    return valid_moves


def queen_valid_moves(player_type, file_, rank):
    return bishop_valid_moves(player_type, file_, rank) + rook_valid_moves(player_type, file_, rank)


def king_valid_moves(player_type, file_, rank):
    valid_moves = queen_valid_moves(player_type, file_, rank)
    valid_moves = [move for move in valid_moves
                   if move[0] < file_+2 and move[0] > file_-2
                   and move[1] < rank+2 and move[1] > rank-2]
    return valid_moves


def count_remaining_armies(att_pieces, def_pieces):
    n_attack_armies = 0
    n_defend_armies = 0
    for piece in att_pieces:
        n_attack_armies += gv.CHESSMEN_VALUES[piece.lower()]
    for piece in def_pieces:
        n_defend_armies += gv.CHESSMEN_VALUES[piece.lower()]

    if 'g' not in att_pieces:
        n_attack_armies = 0
    if 'G' not in def_pieces:
        n_defend_armies = 0

    return n_attack_armies, n_defend_armies


def get_coords_by_player_type(player_type):
    # Find the squares on which this player's pieces are
    valid_squares = []
    for file_, unused in enumerate(gv.CHESSBOARD):
        for rank, unused in enumerate(gv.CHESSBOARD[file_]):
            if (player_type == 'attacker'
                and gv.CHESSBOARD[file_][rank].islower()):
                valid_squares.append((file_, rank))
            elif (player_type == 'defender'
                  and gv.CHESSBOARD[file_][rank].isupper()):
                valid_squares.append((file_, rank))
    return valid_squares


def get_coords_by_piece_type(piece_type):
    global NRANKS, NFILES
    all_coords = []
    NFILES = len(gv.CHESSBOARD)
    NRANKS = len(gv.CHESSBOARD[0])
    for irank in xrange(NRANKS):
        for ifile_ in xrange(NFILES):
            if gv.CHESSBOARD[ifile_][irank]:
                if gv.CHESSBOARD[ifile_][irank] == piece_type:
                    all_coords.append((ifile_, irank))
    return all_coords


def get_pieces_from_board():
    global NRANKS, NFILES
    def_pieces = []
    att_pieces = []
    NFILES = len(gv.CHESSBOARD)
    NRANKS = len(gv.CHESSBOARD[0])
    for irank in xrange(NRANKS):
        for ifile_ in xrange(NFILES):
            if gv.CHESSBOARD[ifile_][irank]:
                if gv.CHESSBOARD[ifile_][irank].isupper():
                    def_pieces.append(gv.CHESSBOARD[ifile_][irank].lower())
                if gv.CHESSBOARD[ifile_][irank].islower():
                    att_pieces.append(gv.CHESSBOARD[ifile_][irank].lower())
    return def_pieces, att_pieces


def coords(coord_string):
    """
    Match a coordinate string (eg A7) to a gv.CHESSBOARD list index.
    Must check file string matches a regex in invalid input choices
    """
    if len(coord_string) == 2:
        file_ = ord(coord_string[0].lower()) - 97
        rank = int(coord_string[1])
        return file_, rank
    else:
        return None, None