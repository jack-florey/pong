from .. import db
from sqlalchemy import types

import json
from json import JSONEncoder
import jsonpickle
import random
import uuid
from functools import reduce
import datetime

class JsonType(types.TypeDecorator):    

    impl = types.Unicode

    def process_bind_param(self, value, dialect):
        if value :
            return unicode(jsonpickle.encode(value))
        else:
            return None

    def process_result_value(self, value, dialect):
        if value:
            return jsonpickle.decode(value)
        else:
            return None


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    time_started = db.Column(db.DateTime,default=datetime.datetime.utcnow)
    game_object = db.Column(JsonType())
    previous_game_object = db.Column(JsonType())

    def update_game_state(self, new_state):
        fresh = jsonpickle.decode(unicode(jsonpickle.encode(new_state)))
        self.previous_game_object = self.game_object
        self.game_object = fresh

class Player(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(64))
        wins = db.Column(db.Integer,default=0)
        kills = db.Column(db.Integer,default=0)
        deaths = db.Column(db.Integer,default=0)


AUTORUN_ON = "on"
AUTORUN_OFF = "off"

MODE_SETUP = "setup"
MODE_PLAYING = "playing"
MODE_COMPLETE = "complete"
MODE_ARCHIVED = "archived"


class GameState(object):
    def __init__(self):
        self.players = {}
        self.board = []
        self.eliminated = []

        self.current_index = None
        self.mode = MODE_SETUP

        self.date_finished = None

        self.num_cups = 6


    def init_players(self, players):
        for p in players:
            add_player(p)

    def add_player(self, player_name, id=None):
        if self.mode == MODE_SETUP:
            ps = PlayerState(player_name, self.num_cups, id)
            self.board.append(ps.id)
            self.players[ps.id] = ps
            return ps
        else: 
            raise Exception("Game is already in progress!!")

    def remove_player(self, uuid):
        if self.mode == MODE_SETUP:
            self.players.pop(uuid)
        else: 
            raise Exception("Game is already in progress!!")

    def start_game(self, shuffle=True):
        self.mode = MODE_PLAYING
        if len(self.players) == 0:
            raise Exception("No Players registered!")


        if shuffle:
            random.shuffle(self.board)

        self.current_index = self.board[0]

    def current_player(self):
        print self.players
        return self.players[self.current_index]

    def cup_hit(self, uuid): 
        p = self.players[uuid]
        if not p.hit():
            raise Exception("No cups to hit!")

        if not p.alive():
            self.kill(uuid)

    def player(self, name):
        for p in players:
            if p.name == name:
                return p
        raise Exception("No player %s" % name)
        
    def kill(self, uuid):
        if self.players[uuid].alive():
            raise Exception("can't kill living player")

        killer = self.get_previous_player(uuid)
        killed = self.players[uuid]

        self.board.remove(uuid)
        
        killed.knocked_out_by = killer.id
        self.eliminated.append(uuid)

        killer.add_cup()

        if len(self.board) == 1:
            self.trigger_end_game()

    def trigger_end_game(self):
        self.finished_time = datetime.datetime.utcnow
        self.mode = MODE_COMPLETE

    def is_playing(self):
        return self.mode == MODE_PLAYING

    def is_complete(self):
        return self.mode == MODE_COMPLETE or self.mode == MODE_ARCHIVED

    def is_archived(self):
        return self.mode == MODE_ARCHIVED

    def is_in_setup(self):
        return self.mode == MODE_SETUP

    def index(self, uuid):
        try:
            return self.board.index(uuid)
        except:
            raise Exception("Player %s isn't active" % self.players[uuid])

    def get_previous_player(self, uuid):
        return self.players[self.board[self.index(uuid) - 1 % len(self.board)]]


    def get_kills(self, player_id):
        return sum(1 for p in self.players.values() if p.knocked_out_by == player_id)
    
    def __str__(self):
        joined =", ".join([str(self.players[j]) for j in self.board])
        return "Mode: %s \r\nPlaying: %s \r\nKnocked Out: %s" % (self.mode, 
               ", ".join([str(self.players[j]) for j in self.board]),
               ", ".join([str(self.players[j]) for j in self.eliminated]))


STATUS_ELIMINATED = "eliminated"
STATUS_ALIVE = "alive"
    

class PlayerState(object):
    def __init__(self, name, num_cups, id=None):
        if not id:
            id = uuid.uuid4()
        self.id = str(id)
        self.name = name
        self.max_cups = num_cups
        self.cups = num_cups
        self.status = STATUS_ALIVE
        self.knocked_out_by = None

    def alive(self): 
        return self.cups > 0

    def hit(self):
        if self.cups > 0:
            self.cups = self.cups - 1
            return True
        return False

    def add_cup(self):
        if self.cups != self.max_cups:
            self.cups = self.cups + 1

    def __str__(self):
        return "%s{%s}: Cups [%d / %d]" % (self.name, self.id[:8], self.cups, self.max_cups)

    def __repr__(self):
        return "Player %s{%s}" % (self.name, self.id)
