#!/usr/bin/env python2
import unittest2 as unittest
import mock

from .. import risk, players


class TestBoard(unittest.TestCase):
    """Test some things about the Board class."""

    def setUp(self):
        mock.patch.object(risk.gv, 'PLAYERS',
                          {'pl1': players.Player('@'), 'pl2': players.Player('=')}
        ).start()
        self.brd = risk.Board(terr_names_file='/Users/staylor/Documents/chessrisk/v0_23/territory_names.chr')

    def tearDown(self):
        mock.patch.stopall()

    def test_save(self):
        """Can save board object without getting exception."""
        print self.brd.save()

    def test_load(self):
        """Can load board object without getting exception."""
        should_be_json = self.brd.save()
        self.brd.load(should_be_json)


class TestRisk(unittest.TestCase):
    """Test miscallaneous aspects of the Risk module."""

    def fake_count_owned_territories(self, player):
        return_dict = {'Bob': 100,
                       'Fred': 0}
        return return_dict[player]

    def setUp(self):
        mock_players = {'Bob': players.Player('@'),
                        'Fred': players.Player('#')}
        mock.patch.dict(risk.gv.PLAYERS, mock_players).start()

    def tearDown(self):
        mock.patch.stopall()

    def test_eliminate_dead_players(self):
        """Dead players stay dead."""
        mock.patch.object(risk, 'count_owned_territories',
                          self.fake_count_owned_territories).start()
        risk.eliminate_dead_players()
        self.assertEqual(risk.gv.PLAYERS.keys(), ['Bob'])

    def test_check_for_victory(self):
        """If one player is left, that's victory."""
        self.assertFalse(risk.check_for_victory())
        del risk.gv.PLAYERS['Bob']
        self.assertTrue(risk.check_for_victory())


if __name__ == "__main__":
    unittest.main()