import os
import json
import shutil

from pprint import pprint

import global_vars as gv

from utils import mkdir_p


def serialise():
    j = '{'

    j += '"GLOBAL_VARIABLES": {'
    for var in dir(gv):
        if var[0] == '_':
            continue

        saveme = getattr(gv, var)

        if hasattr(saveme, '__name__'):
            # Must not attempt to save any modules we've imported into global_vars.
            continue

        if hasattr(saveme, 'save'):
            # Complicated stuff must be given a save() method
            # that returns a string of JSON representing the object.
            # Such objects must have a load() method to re-create
            # the object from the JSON representation.
            if saveme.save():
                j += '"%s": %s,' % (var, saveme.save())
        else:
            # For simple stuff, we can just json.dumps
            j += '"%s": %s,' % (var, json.dumps(saveme))
    j = j.rstrip(',') + '}'

    j = j.rstrip(',') + '}'
    return j


def save(filename):
    if not gv.RESTORING:
        j = serialise()
        mkdir_p(os.path.dirname(os.path.join('saves', filename)))
        with open(os.path.join('saves', filename), 'w') as save_file:
            save_file.write(j)


# TODO: Save any chess-based variables DONE
# TODO: Load methods for stuff DONE
# TODO: Test and debug the restore mechanism (and the save mechanism)


def checkpoint(game_stage):
    """ Save a file named 'autosave', and mark the game stage.
    Should be called at every point it makes sense to recover to.

    Whenever you add a new checkpoint, make sure you test/debug it thoroughly!

    @param game_stage       string describing the stage of the game we're at
    """
    gv.GAME_STAGE = game_stage
    if not gv.RESTORING:
        if gv.HEADLESS:
            print '************ADDING TO R QUEUE************'
            gv.ANSWERS = {}
            asdf = serialise()
            print asdf
            gv.MESSAGE_NUMBER += 1
            gv._RESPONSE = asdf
            #gv.ANSWERS = gv._AQ.get()
            print '***********DONE ADDING TO R QUEUE**************'
        save(gv.GAME_ID + game_stage)
        save(gv.GAME_ID + 'autosave')
    elif game_stage == gv.RESTORE_GAME_STAGE:
        gv.RESTORING = False
        restore_saved_globals()


def manualsave(filename):
    """ Since we have a finite set of restore points, a manual save
    is just renaming the autosave such that it is kept.
    """
    shutil.copy2(os.path.join('saves', 'autosave'), os.path.join('saves', filename))
    gv.prnt('Game saved as %s.' % filename)


def restore_saved_globals_into_module(modules_gv, saved_globals):
    for key, value in saved_globals.iteritems():
        if gv.DEBUG:
            print key, value
        try:
            global_var = getattr(modules_gv, key)
        except AttributeError as e:
            if 'object has no attribute' in e.message:
                # If global_var doesn't have this attribute,
                # the save file is probably from an older version.
                # Don't load this attribute, and hope for the best!
                # In future, could check version number in savefile
                # and load in specific ways depending on version.
                print e.message
                continue
        if hasattr(global_var, 'load'):
            # As with saving, more complex objects need specialised load() methods
            print 'LOADING >>> {0}'.format(key)
            global_var.load(value)
        else:
            # Simple data structures can use json.loads()
            print 'LOADING >>> {0}'.format(key)
            global_var = value
        # may not be necessary...
        setattr(modules_gv, key, global_var)


def restore_saved_globals():
    # Do some experimenting to ensure this works as expected - particularly with regards to scope.
    if gv.DEBUG:
        pprint(gv.SAVED_GLOBALS)
    restore_saved_globals_into_module(gv, gv.SAVED_GLOBALS)

    gv.BOARD.print_board()
    if gv.ATTACK_FROM and gv.ATTACK_TO:
        gv.prnt("{} is attacking from {} to {} with {} armies".format(gv.CURR_PLAYER, gv.ATTACK_FROM, gv.ATTACK_TO, gv.N_ATTACK_ARMIES))


def handle_save_request():
    gv.UI.clear_inv_choices()
    filename = gv.UI.handle_user_input('Filename (press enter for quicksave):')
    if filename:
        save(filename)
    else:
        save('quicksave')