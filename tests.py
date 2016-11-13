import unittest
import mock
import risk
import players
import global_vars as gv

class Test_risk(unittest.TestCase):

    def fake_count_owned_territories(self, player):
        return_dict = {'Bob': 100,
                       'Fred': 0}
        return return_dict[player]

    def setUp(self):
        mock_players = {'Bob': players.Player('@'),
                        'Fred': players.Player('#')}
        mock.patch.dict(gv.PLAYERS, mock_players).start()

    def tearDown(self):
        mock.patch.stopall()

    def test_eliminate_dead_players(self):
        mock.patch.object(risk, 'count_owned_territories',
                          self.fake_count_owned_territories).start()
        risk.eliminate_dead_players()
        self.assertEqual(gv.PLAYERS.keys(), ['Bob'])

    def test_check_for_victory(self):
        self.assertFalse(risk.check_for_victory())
        del gv.PLAYERS['Bob']
        self.assertTrue(risk.check_for_victory())

if __name__ == "__main__":
    unittest.main()