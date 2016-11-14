import unittest2 as unittest
import mock

import sys

sys.path.append('../')

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
            raise FakeInputException

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


class TestIntegrationCmdLine(unittest.TestCase):
    """Test the commandline game.
    Mock out the user input and stdout, and some other things like saving and loading.
    """
    @classmethod
    def setUpClass(cls):
        inputs = {

        }
        # We might need to mock handle_user_input and prnt everywhere they're imported! :(
        mock.patch.object(
            chessrisk.utils.UserInputter,
            'handle_user_input',
            FakeInput(inputs)
        ).start()

        mock.patch.object(chessrisk.utils, 'prnt').start()

    @classmethod
    def tearDownClass(cls):
        mock.patch.stopall()

    def test_setup_and_quit(self):
        """Can set a game up, then quit"""

        # Set up a bunch of inputs for the setup stage
        chessrisk.utils.UserInputter.handle_user_input.inputs = {}

        # Run the game in cmdline mode. worker=False by default.
        chessrisk.run_game(None, None)


if __name__ == "__main__":
    unittest.main()