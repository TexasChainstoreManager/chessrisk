import unittest2 as unittest
import mock

import sys
import os

import random
from copy import deepcopy

os.chdir('../')
sys.path.append('./')

import chessrisk
import utils


def read_territory_names():
    with open(chessrisk.risk.TERRITORY_NAMES_FILE) as f:
        return [x.strip() for x in f.readlines()]


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
                user_input = str(v)
                break
        else:
            raise FakeInputException('Message not found in self.inputs: {msg}'.format(msg=message))

        # If a list was given, pop from the list
        if isinstance(user_input, list):
            if len(user_input) > 1:
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
    """Base class for common mocking and main game setup
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


class RandomStringPicker(object):
    """When my string representation is produced, I pick one randomly from a list.
    """
    def __init__(self, pick_from):
        self.pick_from = pick_from
        self.last_choice = ''

    def __str__(self):
        self.last_choice = random.choice(self.pick_from)
        return self.last_choice


class DoThenString(object):
    """When my string representation is produced, I call a function first.
    """
    def __init__(self, do, string):
        self.do = do
        self.string = string

    def __str__(self):
        self.latest_return = self.do()
        return self.string


class TestIntegrationCmdLineRisk(TestIntegrationCmdLine):
    """Test for Risk parts of the game - building and risk-style battles.
    """
    def test_setup_and_quit(self):
        """Can set a game up, then quit"""
        self.inputs.update({
            'Fred, (b)uild or (a)ttack': 'x'
        })

        with self.assertRaises(SystemExit) as cm:
            # Run the game in cmdline mode. worker=False by default.
            chessrisk.run_game(None, None)

        self.assertEqual(cm.exception.code, 0)

    def test_build_quit(self):
        """Can set a game up, build 1 army, then quit
        """
        # We keep trying random territory names until one is valid.
        terr_names = [x.lower() for x in read_territory_names()]
        random_terr_name = RandomStringPicker(terr_names)

        board_then_b = DoThenString(
            lambda: deepcopy(chessrisk.gv.TERRITORIES), 'b')

        self.inputs.update({
            'Fred, (b)uild or (a)ttack': board_then_b,
            'Select a territory to reinforce': random_terr_name,
            'Invalid territory choice': '\n',
            'Not your territory': '\n',
            'Add how many armies': '1',
            'Jimbo, (b)uild or (a)ttack': 'x'
        })

        with self.assertRaises(SystemExit) as cm:
            # Run the game in cmdline mode. worker=False by default.
            chessrisk.run_game(None, None)
        self.assertEqual(cm.exception.code, 0)

        initial_board = board_then_b.latest_return
        self.assertEqual(
            initial_board[random_terr_name.last_choice].narmies + 1,
            chessrisk.gv.TERRITORIES[random_terr_name.last_choice].narmies
        )

    def test_build_build_quit(self):
        pass

    def test_risk(self):
        pass

    def test_chess(self):
        pass

    def test_build_risk(self):
        pass

    def test_build_chess(self):
        pass

    def test_build_risk_build(self):
        pass

    def test_build_build_risk(self):
        pass


class TestIntegrationCmdLineChess(TestIntegrationCmdLine):
    """Test for Chess parts of the game - the chess-style battle functionality.
    """

    def test_chess(self):
        pass


# TODO: classes to test save and load


if __name__ == "__main__":
    unittest.main()