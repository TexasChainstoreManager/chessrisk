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
#
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

    def __init__(self, inputs):
        """
        @param inputs - list of inputs in the order they are expected
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
            user_input = user_input.pop()

        if user_input in ['exit', 'x']:
            raise utils.UserQuitException
        if user_input in ['s', 'save']:
            pass
        if user_input in ['l', 'load']:
            raise utils.LoadException


class TestIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        inputs = {

        }
        mock.patch.object(
            chessrisk.utils.UserInputter,
            'handle_user_input',
            FakeInput(inputs)
        ).start()

    @classmethod
    def tearDownClass(cls):
        mock.patch.stopall()

    def test_normal_game(self):
        chessrisk.run_game(None, None)


if __name__ == "__main__":
    unittest.main()