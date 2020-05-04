import unittest

from app import create_app, db
from flask import current_app
from app.models import *

class GameStateTestCase(unittest.TestCase):
    def setUp(self):
        self.game = GameState()

        self.clayton = self.game.add_player("Clayton")
        self.ariel = self.game.add_player("Ariel")
        self.jimbo = self.game.add_player("Jimbo")
        self.arcturus = self.game.add_player("Arcturus")

        self.game.start_game(shuffle=False)

    def tearDown(self):
        self.game = None

    def testBasicGameFlows(self):
        g = self.game

        self.assertEquals(self.arcturus, g.get_previous_player(self.clayton.id))
        self.assertEquals(self.clayton, g.get_previous_player(self.ariel.id))

        g.cup_hit(self.arcturus.id)

        self.assertEquals(5, self.arcturus.cups)

        for i in range(0,6):
            g.cup_hit(self.clayton.id)
        
        self.assertEquals(3, len(g.board))
        self.assertEquals(1, len(g.eliminated))

        self.assertEquals(self.arcturus, g.get_previous_player(self.ariel.id))
        self.assertEquals(self.ariel, g.get_previous_player(self.jimbo.id))

        self.assertEquals(self.arcturus.id, self.clayton.knocked_out_by)

        self.assertEquals(6, self.arcturus.cups)



        
        


