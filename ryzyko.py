from flask import Flask, request, render_template, redirect, url_for, make_response, flash
import os
import pickle
import importlib
import game
import shutil
import random

app = Flask(__name__)
GAMES_LIST = {}


def id_iterator():
    i = 0
    while True:
        i += 1
        yield i


GAMES_PATH = os.path.dirname(os.path.abspath(__file__)) + '/static/games/'
ID_GENERATOR = id_iterator()


@app.route('/')
def hello():
    """
    Starting screen
    :return: render_template
    """
    player_id = request.cookies.get('player_id')
    # if player_id -> write out player's games
    # player can choose: to continue started game, to create new or to join open one
    response = make_response(render_template('hello.html'))
    if player_id:
        pass
    else:
        response.set_cookie('player_id', str(next(ID_GENERATOR)))
    return response


"""Function waiting_room"""


@app.route('/customize')
def customize():
    """
    Customize game
    :return: render_template
    """
    board_id = request.cookies.get('board_id')
    overwrite = False
    if board_id and os.path.exists(GAMES_PATH + str(board_id) + '/board.pkl'):
        overwrite = True
    return render_template('customize.html', overwrite=overwrite)


@app.route('/choose_players')
def choose_players():
    """
    Choose players
    gets map_name and players (number)
    :return: render_template
    """
    if request.args.get('newgame'):
        map_name = request.args.get('map_name')
        players_num = int(request.args.get('players'))
        game_name = request.args.get('game_name')
        return render_template('choose_players.html', players_num=players_num, map_name=map_name, game_name=game_name)
    else:
        return redirect(url_for('customize'))


@app.route('/play', methods=['GET', 'POST'])
@app.route('/play/<phase>', methods=['GET', 'POST'])
@app.route('/play/<phase>/<territory>', methods=['GET', 'POST'])
@app.route('/play/<phase>/<territory>/<destination>', methods=['GET', 'POST'])
def play(phase=None, territory=None, destination=None):
    """
    Function play - front controller
    :param phase: str/None
    :param territory: str/None
    :param territory_from: str/None
    :param territory_to: str/None
    :return:
    """
    """Check player and load board"""
    board_id = request.cookies.get('board_id')
    if board_id and os.path.exists(GAMES_PATH + str(board_id) + '/board.pkl'):
        board = pickle.load(open(GAMES_PATH + str(board_id) + '/board.pkl', 'rb'))
    else:
        flash(game.MESSAGES['session-expired'], 'danger')
        return render_template('error.html')

    """Check phase correction"""
    if not phase:
        return game.game(board)
    if board.get_phase() != phase:
        flash(game.MESSAGES['wrong-phase'], 'danger')
        return game.render_board(board)

    if phase == 'initial':
        return game.initial(board, territory)
    elif phase == 'initial-reinforce':
        return game.initial_reinforce(board, territory)
    elif phase == 'deployment':
        return game.deploy(board, territory)
    elif phase == 'attack':
        return game.attack(board, territory, destination)
    elif phase == 'fortify':
        return game.fortify(board, territory, destination)


@app.route('/newgame', methods=['GET', 'POST'])
def newgame():
    """
    New game controller
    :return: game -> render_template
    """
    players = {}
    online = False
    for i in range(1, int(request.args.get('players_num')) + 1):
        players[str(i)] = [
            request.args.get('player' + str(i)),
            request.args.get('player' + str(i) + 'name'),
            request.args.get('player' + str(i) + 'algorithm')
        ]
        if players[str(i)][0] == 'self-player':
            players[str(i)].append(request.cookies.get('player_id'))
        else:
            players[str(i)].append(None)
            online = True
    map_name = request.args.get('map_name')
    game_name = request.args.get('game_name')
    board = new(map_name, game_name, players)
    # if online -> waiting room
    response = make_response(game.game(board))
    response.set_cookie('board_id', str(board.get_id()))
    return response


@app.route('/new_phase', methods=['GET'])
def new_phase():
    """
    New phase controller
    Called after finishing attack or omitting fortification
    :return: game -> render_template
    """
    board_id = request.cookies.get('board_id')
    if board_id and os.path.exists(GAMES_PATH + str(board_id) + '/board.pkl'):
        board = pickle.load(open(GAMES_PATH + str(board_id) + '/board.pkl', 'rb'))
    else:
        flash(game.MESSAGES['session-expired'], 'danger')
        return render_template('error.html')
    board.new_phase()
    pickle.dump(board, open(GAMES_PATH + str(board_id) + '/board.pkl', 'wb'))
    return game.game(board)


@app.route('/end_game', methods=['GET'])
def end_game():
    """
    Render board after game finishes
    :return: game -> render_template
    """
    board_id = request.cookies.get('board_id')
    if board_id and os.path.exists(GAMES_PATH + str(board_id) + '/board.pkl'):
        board = pickle.load(open(GAMES_PATH + str(board_id) + '/board.pkl', 'rb'))
    else:
        flash(game.MESSAGES['session-expired'], 'danger')
        return render_template('error.html')
    winner = board.alive_players()[0]
    shutil.rmtree(GAMES_PATH + str(board_id))
    flash(game.MESSAGES['game-deleted'], 'success')
    return render_template('end_game.html', map=board.get_map_name(), territories=board.repr_territories(),
                           continents=board.repr_continents(),
                           round=board.get_round(), player=[winner.repr_id(), winner.get_name()])


@app.route('/abandon_game', methods=['GET'])
def abandon_game():
    """
    Abandon game
    :return: redirect -> hello()
    """
    board_id = request.cookies.get('board_id')
    if board_id and os.path.exists(GAMES_PATH + str(board_id) + '/board.pkl'):
        board = pickle.load(open(GAMES_PATH + str(board_id) + '/board.pkl', 'rb'))
    else:
        flash(game.MESSAGES['session-expired'], 'danger')
        return render_template('error.html')
    if request.args.get('confirm'):
        shutil.rmtree(GAMES_PATH + str(board_id))
        flash(game.MESSAGES['game-deleted'], 'success')
        return redirect(url_for('hello'))
    else:
        return game.render_board(board, abandon=True)


"""Funkcje pomocnicze"""


def new(map_name, game_name, players):
    """
    New game creator
    :param map_name: string
    :param players: dict
    :return: Board
    """
    board_id = request.cookies.get('board_id')
    if board_id and os.path.exists(GAMES_PATH + str(board_id) + '/board.pkl'):
        shutil.rmtree(GAMES_PATH + str(board_id))
        flash(game.MESSAGES['game-deleted'], 'success')
    board_id = next(ID_GENERATOR)
    importlib.import_module('static.maps.' + map_name)
    board = importlib.import_module('.board', package='static.maps.' + map_name)
    board = board.create_map(players, map_name, game_name, board_id)
    os.mkdir(GAMES_PATH + str(board_id))
    flash(game.MESSAGES['game-created'], 'success')
    pickle.dump(board, open(GAMES_PATH + str(board_id) + '/board.pkl', 'wb'))
    return board


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(host="0.0.0.0", port=5017)
