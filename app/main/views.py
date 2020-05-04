from flask import Blueprint, render_template
from flask_login import current_user


from app.models import EditableHTML, Game, Permission

main = Blueprint('main', __name__)


@main.route('/')
def index():
    games = Game.query.all()
    can_create = current_user.can(Permission.GAME_ADMIN)
    return render_template('main/index.html', games=games, can_create=can_create)


@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template(
        'main/about.html', editable_html_obj=editable_html_obj)
