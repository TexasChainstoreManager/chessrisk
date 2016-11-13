import unittest2 as unittest
import mock

from .. import risk, players


class TestBoard(unittest.TestCase):

    def setUp(self):
        mock.patch.object(risk.gv, 'PLAYERS',
                          {'pl1': players.Player('@'), 'pl2': players.Player('=')}
        ).start()
        self.brd = risk.Board(terr_names_file='/Users/staylor/Documents/chessrisk/v0_23/territory_names.chr')

    def tearDown(self):
        mock.patch.stopall()

    def test_save(self):
        print self.brd.save()

    def test_load(self):
        should_be_json = self.brd.save()
        self.brd.load(should_be_json)

if __name__ == "__main__":
    unittest.main()