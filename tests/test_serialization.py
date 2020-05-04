import unittest

from app import create_app, db
from flask import current_app
from app.models import *

import json
import jsonpickle
from json import JSONEncoder


class GameSerializationTestCase(unittest.TestCase):
    def setUp(self):
        self.game = GameState()

        self.clayton = self.game.add_player("Clayton")
        self.ariel = self.game.add_player("Ariel")
        self.jimbo = self.game.add_player("Jimbo")
        self.arcturus = self.game.add_player("Arcturus")

        self.game.start_game(shuffle=False)

    def tearDown(self):
        self.game = None

    def testPlayerSerialization(self):
        g = self.game

        for i in range(0, 6):
            g.cup_hit(self.jimbo.id)
        
        g.cup_hit(self.ariel.id)

        pickled = jsonpickle.encode(self.game)

        thawed = jsonpickle.decode(pickled)

        self.assertEquals(self.ariel.id,thawed.get_previous_player(self.arcturus.id).id)

        self.assertEquals(thawed.players[self.ariel.id].cups, 5)
