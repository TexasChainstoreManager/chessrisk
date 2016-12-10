"""
Chessrisk
If you thought Risk was too short...
"""
import sys
import os
import json
import argparse
import multiprocessing
from pprint import pprint

import global_vars as gv
import utils
import players
import risk
import save

from flask import Flask, render_template, request

app = Flask(__name__)

GAME_PROCS = {}
ANSWER_QUEUES = {}
RESPONSE_QUEUES = {}

game_id = None
next_game_stage = None


def print_welcome_message():
    gv.prnt.blockprnt([
        "---------------------------------------------------------------",
        "Welcome to Chessrisk v{0}.{1}".format(gv.ver_maj, gv.ver_min),
        "This version is a full square grid of territories with no sea.",
        "Battles can be resolved in Chess Style or traditional Risk style.",
        "Input is case insensitive and you can use short and long commands.",
        "Type e(x)it at any time to exit.",
        "Type (s)ave at any time to save.",
        "Type (l)oad at any time to load.",
        "---------------------------------------------------------------",
    ])
    gv.UI.handle_user_input('Press enter to begin')


def setup_game():
    print_welcome_message()
    players.choose_number_of_players()
    players.setup_players()
    import pdb
    pdb.set_trace()
    risk.setup_board()
    save.checkpoint('initial')


def process_round():
    # Slightly complicated way of iterating over players to allow restoring saved games.
    # Must maintain a list of players yet to go and pop the next players off the list.
    gv.PLAYERS_YET_TO_GO = []
    for player in gv.PLAYERS:
        gv.PLAYERS_YET_TO_GO.append(player)
    while gv.PLAYERS_YET_TO_GO:
        gv.CURR_PLAYER = gv.PLAYERS_YET_TO_GO.pop()
        if gv.DEBUG:
            print gv.CURR_PLAYER, 'PLAYER'
        save.checkpoint('beginning_of_player_turn')
        gv.UI.clear_inv_choices()
        gv.UI.set_inv_choice({'You can only choose to (b)uild or (a)ttack!':
                             lambda x: x not in ['a', 'attack', 'b', 'build']})
        action_choice = gv.UI.user_input_check_choices(
                              gv.PLAYERS[gv.CURR_PLAYER].colour + ' ' +
                              gv.CURR_PLAYER + ", (b)uild or (a)ttack?"
        )
        if action_choice in ['b', 'build']:
            if gv.DEBUG:
                print 'build selected'
            risk.process_build_turn()
        elif action_choice in ['a', 'attack']:
            risk.process_attack_turn()
            if gv.DEBUG:
                print 'attack selected'


def pre_round():
    gv.ROUND_NUMBER += 1
    save.checkpoint('round_start')

    gv.prnt("------------------------")
    gv.prnt("- Round: " + str(gv.ROUND_NUMBER) + "-")
    gv.prnt("------------------------")
    gv.BOARD.print_board()


def main_loop():
    while not risk.check_for_victory():
        pre_round()
        process_round()


def byteify(input):
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def restore_saved_game():
    gv.UI.clear_inv_choices()
    file_to_load = gv.UI.user_input_check_choices('Choose file to load. Type carefully!')

    gv.RESTORING = True

    with open(os.path.join('saves',file_to_load), 'r') as loadme:
        gv.SAVED_GLOBALS = byteify(json.loads(loadme.read()))['GLOBAL_VARIABLES']

    gv.RESTORE_GAME_STAGE = gv.SAVED_GLOBALS['GAME_STAGE']

    setup_game()
    main_loop()


def run_game(answer_queue, response_queue, worker=False, game_id=''):
    gv._AQ = answer_queue
    gv._RQ = response_queue
    gv.HEADLESS = worker
    gv.GAME_ID = game_id
    try:
        setup_game()
        main_loop()
    except utils.LoadException:
        restore_saved_game()
    except utils.UserQuitException:
        save.save('last_quit')
        gv.prnt("Byeeee!")
        sys.exit(0)


@app.route('/serverfunc', methods=['POST'])
def server_func():
    print '*********************************SERVER FUNC:'
    print "SERVER: request_form>>"
    pprint(dict(request.form))
    game_id = request.form['gameId']
    print "SERVER: game_id>>{0}".format(game_id)
    global_vars = json.loads(request.form['globalVars'])
    print "SERVER: global_vars>>"
    pprint(global_vars)
    func = request.form['func']
    print "SERVER: requested func>>{0}".format(func)
    args = request.form.get('args', [])
    print "SERVER: args>>{0}".format(args)
    kwargs = request.form.get('kwargs', {})
    print "SERVER: kwargs>>{0}".format(kwargs)
    module = risk
    print 'SERVER: copied risk module'

    module.create_dummy_globals()
    save.restore_saved_globals_into_module(module.gv, global_vars)

    print 'SERVER: restored globals into risk module'
    result = getattr(module, func)(*args, **kwargs)
    print 'SERVER: called function, result is>>{0}'.format(result)
    return json.dumps(result)


@app.route('/', methods=['POST', 'GET'])
def entry_point():
    global game_id
    global next_game_stage

    if request.method == 'GET':
        return render_template('setup.html')
    elif request.method == 'POST':
        gv.DEBUG = True
        print '*********************************ROOT ROUTE:'
        print "SERVER: request_form>>{0}".format(request.form)
        print request.form['gameId']
        game_id = request.form['gameId']

        if str(request.form.get('starting', False)):
            # Begin a new game
            ANSWER_QUEUES[game_id] = multiprocessing.JoinableQueue()
            RESPONSE_QUEUES[game_id] = multiprocessing.Queue()
            GAME_PROCS[game_id] = multiprocessing.Process(
                target=run_game,
                args=(ANSWER_QUEUES[game_id], RESPONSE_QUEUES[game_id], True, game_id)
            )
            GAME_PROCS[game_id].start()

        elif str(request.form.get('restoreTo', False)):
            # Restore a game
            # Should also run restore in the case that the game process has died.
            # (Need a timeout on game processes.)
            # Could do send request->check for game process->response requests a restore if not found->send restore info
            pass
        req, next_game_stage = process_request(request)
        ANSWER_QUEUES[game_id].put(req)
        ANSWER_QUEUES[game_id].join()
        print 'SERVER: AQ'
        print ANSWER_QUEUES[game_id]
        print 'SERVER: /AQ'

        # TODO: The server is sitting idle while it waits for the queue to be populated.
        # TODO: Do this asynchronously in future.
        # TODO: Also, if the process crashes, this will wait forever.

        print 'SERVER: End of root route'
        # print 'now here'
        hahahaha = render_template('chessrisk.html')
        # print 'STUFFS!!!!!>>>>>' + hahahaha
        print 'SERVER: Current player: {0}'.format(gv.CURR_PLAYER)
        return hahahaha


def process_request(r):
    print '1'
    print r
    f = r.form
    print '2'
    print f
    fd = json.loads(f.get('formData', ''))
    print '3'
    print fd
    answers = {}

    next_game_stage = f['nextGameStage']
    print next_game_stage
    if f.get('starting', False):
        answers = {
            'enter to begin': '\n',
            'human players': int(fd['humanPlayers']),
            'computer players': int(fd['computerPlayers']),
        }
        for player in fd['playerInfo']:
            answers['Player {0}'.format(player['id'])] = str(player['name'])
            answers['{0}, choose a mark'.format(player['name'])] = str(player['mark'])
    elif next_game_stage == 'during_build_turn':
        answers = {
            '(b)uild or attack': 'b',
            'territory to reinforce': fd['territory'],
            'how many armies': fd['narmies']
        }

    return answers, next_game_stage


# This is a sensible way to get context into the template... right?
@app.context_processor
def response_data():
    global game_id
    global next_game_stage

    # Need to get everything off the queue until we've got the final entry (it's FIFO, we want LIFO)
    # Alternatively, should use a LIFO queue, see http://stackoverflow.com/questions/31981794/python-multiprocessing-with-lifo-queues
    res = None

    if game_id and next_game_stage:
        print 'RESPONSE_DATA--------------------------------------------------------'
        # print RESPONSE_QUEUES[game_id].qsize()
        while True:
            try:
                print '*********SERVER: GETTING FROM RESPONSE QUEUE************'
                res = json.loads(RESPONSE_QUEUES[game_id].get())
                if res['GLOBAL_VARIABLES'].GAME_STAGE == next_game_stage:
                    print '*********SERVER: FINAL GET FROM RESPONSE QUEUE***************'
                    break
                print 'SERVER: HACK LIFO QUEUE>>>>' + res + '<<<<<<'
                print '*********SERVER: DONE GETTING FROM RESPONSE QUEUE***************'
            except:
                print '*********SERVER: OOPS! EMPTIED RESPONSE QUEUE***************'
                print 'SERVER: response given by game process is>>'
                pprint(res)
                break
        try:
            # Server process needs a copy of the game process's globals
            # In order to make serverfunc work.
            print 'SERVER: Copying game process\'s stored globals'
            gv._SERVER_STORED_GLOBALS[game_id] = res['GLOBAL_VARIABLES']
            print 'SERVER: copy is>>{0}'.format(gv._SERVER_STORED_GLOBALS)
            print 'SERVER: Successfully made copy of game process\'s globals'
        except:
            print res['GLOBAL_VARIABLES']
            print 'SERVER: Could not make copy of game process\'s globals'
    else:
        res = {'a': 'a', 'b': 'b'},
    return res


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--cmdline', action='store_true',
                        help='Run in cmdline mode')
    parser.add_argument('--debug', action='store_true',
                        help='Run in debug mode')
    args = parser.parse_args(argv)

    if args.debug:
        gv.DEBUG = True
    if args.cmdline:
        gv.CMDLINE = True
        gv.HEADLESS = False
        gv.PLAYER_COLORS = ['@', '=', '+', '.', '-', '#']
        run_game(None, None)
    else:
        gv.CMDLINE = False
        app.debug = True
        app.run()


if __name__ == "__main__":
    main(sys.argv[1:])