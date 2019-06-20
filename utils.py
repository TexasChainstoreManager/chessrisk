import errno
import sys
import os

from collections import OrderedDict

import global_vars as gv


class UserQuitException(Exception):
    message = "I don't know how to deal with rejection!"


class LoadException(Exception):
    message = "User has chosen to load a game."


class SendHttpResponse(Exception):
    pass


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class Printer(object):
    """Putting the print functions in a callable object makes mocking easier.
    Also serves as a namespace.
    """
    def __init__(self):
        pass

    def save(self):
        return '"Nothing to save"'

    def load(self, data):
        return '"Nothing to load"'

    def __call__(self, *args, **kwargs):
        """Wrap print so we can override it.
        """
        if 'clear' in kwargs.keys():
            if kwargs['clear'] is not False:
                self.clear_output()
        msg = args[0]
        if gv.RESTORING or gv.HEADLESS:
            if gv.DEBUG:
                print msg
            pass
        else:
            try:
                gv.PRINT_COUNT = len(msg)
                gv.PRINT_RECORD += '\n' + msg
                print msg
                sys.stdout.flush()
            except TypeError as e:
                if 'has no len' in e.message:
                    pass
                else:
                    raise e

    @staticmethod
    def clear_output():
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def blockprnt(self, list):
        self.clear_output()
        for line in list:
            self.__call__(line, clear=False)


from save import handle_save_request


class UserInputter():
    def __init__(self):
        pass

    def save(self):
        return '"Nothing to save"'

    def load(self, data):
        return '"Nothing to load"'

    def clear_inv_choices(self):
        self.inv_choices = OrderedDict({})

    def set_inv_choice(self, inv_choice):
        self.inv_choices.update(inv_choice)

    def user_input_check_choices(self, message, clear=False):
        if gv.RESTORING:
            user_input = fake_user_input_during_restore(message)
        elif gv.HEADLESS:
            gv.prnt(message, clear=clear)
            user_input = fake_user_input_from_http(message)
        else:
            valid_choice = False
            while valid_choice == False:
                user_input = self.handle_user_input(message, clear=clear)
                valid_choice = True
                if user_input == '':
                    valid_choice = False
                    continue
                for warning, condition in self.inv_choices.items():
                    if gv.DEBUG:
                        gv.prnt(warning, '*******', clear=False)
                    if condition(user_input):
                        gv.prnt(warning, clear=False)
                        valid_choice = False
                        break
        return user_input
        
    def handle_user_input(self, message, cast_lower=True, clear=False):
        if gv.RESTORING:
            if gv.DEBUG:
                gv.prnt(message)
            user_input = fake_user_input_during_restore(message)
        elif gv.HEADLESS:
            gv.prnt(message, clear=clear)
            user_input = fake_user_input_from_http(message)
        else:
            if message != '':
                gv.prnt(message, clear=clear)
            user_input = None
            while user_input in [None]:
                gv.prnt('>>')
                curr_player = gv.PLAYERS[gv.CURR_PLAYER]
                if gv.HEADLESS:
                    input_func = sys.stdin.readline
                elif curr_player.is_ai:
                    # If this is an AI player, dispatch to its turn processing methods
                    # This returns a function that, when called, returns the desired string
                    input_func = curr_player.dispatch_message(message)
                else:
                    input_func = raw_input
                # if cast_lower:
                #     user_input = sys.stdin.readline()
                # else:
                #     user_input = input_func()
                user_input = input_func()
                if cast_lower:
                    user_input = user_input.lower()
            if user_input in ['exit', 'x']:
                raise UserQuitException
            if user_input in ['s', 'save']:
                temp_inv_choices = self.inv_choices
                self.clear_inv_choices()
                handle_save_request()
                self.inv_choices = temp_inv_choices
                self.user_input_check_choices(message)
            if user_input in ['l', 'load']:
                raise LoadException
        return user_input


def fake_user_input_during_restore(message):
    answers = gv._RESTORE_PATHS[gv.SAVED_GLOBALS['GAME_STAGE']]
    return fake_user_input_from_dict(message, answers)


def fake_user_input_from_http(message):
    print 'Fake_user_input_from_http. Answers are:'
    print gv.ANSWERS
    if not gv.ANSWERS:
        if not gv.MESSAGE_NUMBER == 0:
            gv._RQ.put(gv._RESPONSE)
            gv._AQ.task_done()
        gv.ANSWERS = gv._AQ.get()
    return fake_user_input_from_dict(message, gv.ANSWERS)


def fake_user_input_from_dict(message, answers):
    # TODO: don't really need this print
    print 'Fake_user_input_from_dict. Answers are:'
    print answers
    for k, v in answers.iteritems():
        if k in message:
            return v
    return answers['default']