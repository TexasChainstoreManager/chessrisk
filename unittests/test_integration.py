import unittest2 as unittest
import mock

import sys
import os

os.chdir('../')
sys.path.append('./')

import chessrisk
import utils


# from StringIO import StringIO
#
#
# def foo():
#     print 'something'
#
#
# # Test the print function like this, but test the rest of the game in terms of calls to the print function
# @patch('sys.stdout', new_callable=StringIO)
# def test(mock_stdout):
#     foo()
#     assert mock_stdout.getvalue() == 'something'
#
#
#
# class TestIntegration(unittest.TestCase):
#
#     @patch('sys.stdout', new_callable=StringIO)
#     def test_some_io(self, mock_stdout):
#
#         self.assertTrue(mock_stdout.getvalue() == 'Foo')


# class Mocker(object):
#     """ I wrote this when I thought I didn't have access to the mock module"""
#     def __init__(self):
#         self.patched = {}
#
#     def patch(self, obj, attrname, mock):
#         self.patched[(obj, attrname)] = obj.__getattr__(attrname)
#         obj.__setattr__(attrname, mock)
#
#     def unpatch(self, obj, attrname):
#         orig = self.patched[(obj, attrname)]
#         obj.__setattr__(attrname, orig)
#
#     def unpatch_all(self):
#         for (obj, attrname) in self.patched.keys():
#             self.unpatch(obj, attrname)


class FakeInputException(Exception):
    message = "No fake input found"


class FakeInput(object):
    """Fake the user interaction. Instantiate with mappings between question and answer.
    Replace the user input function with cls.fake_input to """

    def __init__(self, inputs):
        """
        @param inputs - dict of inputs, mapping prompt message to input
                        {what_am_i_being_asked: what_is_my_response}
                        what_is_my_response can be a list of responses, called in order.
                        If the list is exhausted, the final entry is used repeatedly.
        """
        self.inputs = inputs

    def fake_input(self, message):
        # only need to write part of the message
        for k, v in self.inputs.iteritems():
            if k in message:
                user_input = v
                break
        else:
            raise FakeInputException('Message not found in self.inputs: {msg}'.format(msg=message))

        # If a list was given, pop from the list
        if isinstance(user_input, list):
            if len(user_input) > 1 :
                user_input = user_input.pop()
            else:
                user_input = user_input[0]

        if user_input in ['exit', 'x']:
            raise utils.UserQuitException
        if user_input in ['s', 'save']:
            # We'll need to test the save function separately?
            pass
        if user_input in ['l', 'load']:
            raise utils.LoadException

        return user_input

    def __call__(self, message, cast_lower=True, clear=False):
        return self.fake_input(message)


class TestIntegrationCmdLine(unittest.TestCase):
    """Test the commandline game.
    Mock out the user input and stdout, and some other things like saving and loading.
    """
    @classmethod
    def setUpClass(cls):
        # Standard set of fake user input for setup
        cls.inputs = {
            'enter to begin': '\n',
            'How many human players are there': '2',
            'How many computer players would you like?': '0',
            'Player 1:\nWhat would you like to be called?': 'Jimbo',
            'Jimbo, choose a mark from': 'bl',
            'Player 2:\nWhat would you like to be called?': 'Fred',
            'Fred, choose a mark from': 're',
        }

        # Mock user input
        mock.patch.object(
            chessrisk.utils.UserInputter,
            'handle_user_input',
            FakeInput(cls.inputs)
        ).start()

        # Mock terminal output
        mock.patch.object(chessrisk.utils.Printer, '__call__').start()

    @classmethod
    def tearDownClass(cls):
        mock.patch.stopall()

    def test_setup_and_quit(self):
        """Can set a game up, then quit"""
        self.inputs.update({
            'Fred, (b)uild or (a)ttack': 'x'
        })

        with self.assertRaises(SystemExit) as cm:
            # Run the game in cmdline mode. worker=False by default.
            chessrisk.run_game(None, None)

        self.assertEqual(cm.exception.code, 0)


if __name__ == "__main__":
    unittest.main()