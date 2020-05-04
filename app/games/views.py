from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from flask_rq import get_queue

import sys

from app import db
from app.games.forms import (
    SetupGameForm,
)
from app.decorators import admin_required
from app.models import Game, GameState
from flask import Flask

games = Blueprint('games', __name__)

app = Flask(__name__)


@games.route('/')
@admin_required
def index():
    """Admin dashboard page."""
    return render_template('admin/index.html')

@games.route('/create')
@admin_required
def create_game():
    #Create the model
    g = Game(name="%s's Game" % current_user.first_name)

    db.session.add(g)
    db.session.commit()

    game_id = g.id

    #forward the user
    return redirect(url_for('games.setup_game', game_id=game_id))

@games.route('/<int:game_id>/play')
def play_game(game_id):
    game = Game.query.filter_by(id=game_id).first()

    gs = game.game_object

    return render_template('games/play_game.html', game=gs)

@games.route('/<int:game_id>/actions/cup_hit', methods=['POST'])
def cup_hit(game_id):
    game = Game.query.filter_by(id=game_id).first()

    gs = game.game_object

    gs.cup_hit(request.form['target_id'])

    game.update_game_state(gs)

    db.session.add(game)
    db.session.commit()

    return "hit"


@games.route('/<int:game_id>/setup', methods=['GET', 'POST'])
@login_required
@admin_required
def setup_game(game_id):
    game = Game.query.filter_by(id=game_id).first()
    if game is None:
        abort(404)
    if game.game_object and not game.game_object.is_in_setup():
        return redirect(url_for('games.play_game', game_id=game.id))
    form = SetupGameForm(obj = game)
    if form.validate_on_submit():
        game.name = form.name.data
        gs = GameState()

        for player in form.players.entries:
            player_name = player.data['name']
            if player_name:
                gs.add_player(player_name)

        game.game_object = gs
        gs.start_game()
        db.session.add(game)
        db.session.commit()
        return redirect(url_for('games.play_game', game_id=game.id))



    return render_template('games/setup_game.html', game=game, form=form)
