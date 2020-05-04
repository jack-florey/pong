import time
import unittest

from app import create_app, db
from app.models import *

from datetime import datetime


class GameModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_phases(self):
        g = Game(name="test")

        db.session.add(g)
        db.session.commit()

        game = GameState()

        g.game_object = game

        db.session.add(g)
        db.session.commit()

        game.add_player("Clayton")
        game.add_player("Ariel")
        game.add_player("Jimbo")
        game.add_player("Arcturus")

        game.start_game(shuffle=False)

        g.update_game_state(game)

        db.session.add(g)
        db.session.commit()
