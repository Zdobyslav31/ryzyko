from flask import Flask, request, render_template, redirect, url_for, make_response, flash
import os
import pickle
import importlib
import game
import shutil
import collections
from players import Human
from datetime import datetime
import hashlib

app = Flask(__name__)
GAMES_LIST = {}


def id_generator():
    m = hashlib.md5()
    line = str(datetime.now()).encode('utf-8')
    m.update(line)
    return m.hexdigest()


GAMES_PATH = os.path.dirname(os.path.abspath(__file__)) + '/static/games/'


@app.route('/')
def hello():
    """
    Starting screen
    :return: render_template
    """
    player_id = request.cookies.get('player_id')
    print('request - player ', request.cookies.get('player_id'))
    # if player_id -> write out player's games
    # player can choose: to continue started game, to create new or to join open one
    response = make_response(render_template('hello.html'))
    if not player_id:
        response.set_cookie('player_id', str(id_generator()))
    return response


@app.route('/join_game')
def join_game():
    """
    Join existing online game
    :return: render_template
    """
    player_id = request.cookies.get('player_id')
    if not player_id:
        flash(game.MESSAGES['session-expired'], 'error')
        return redirect(url_for('hello'))
    games = pickle.load(open(GAMES_PATH + '/games.pkl', 'rb'))
    open_games = [(game_id, game_properties) for game_id, game_properties in games.items() if game_properties['open']]
    return render_template('join_game.html', games=open_games, player_id=player_id)


@app.route('/select_game')
def select_game():
    """
    Join existing online game
    :return: render_template
    """
    player_id = request.cookies.get('player_id')
    if not player_id:
        flash(game.MESSAGES['session-expired'], 'error')
        return redirect(url_for('hello'))
    games = pickle.load(open(GAMES_PATH + '/games.pkl', 'rb'))
    player_games = []
    for game_id, game_properties in games.items():
        my_game = False
        for player in game_properties['players']:
            if player[1] == player_id:
                my_game = True
        if my_game:
            player_games.append((game_id, game_properties))
    return render_template('select_game.html', games=player_games, player_id=player_id)


@app.route('/join')
def join():
    """
    Join existing online game
    :return: render_template
    """
    player_id = request.cookies.get('player_id')
    if not player_id:
        return redirect(url_for('hello'))
    name = request.args.get('name')
    board_id, seat_id = request.args.get('player_id').split(',')
    board_id, seat_id = board_id, int(seat_id)
    games = pickle.load(open(GAMES_PATH + '/games.pkl', 'rb'))
    games[board_id]['players'][seat_id - 1][1] = player_id
    games[board_id]['players'][seat_id - 1][2] = name
    open_game = False
    for player in games[board_id]['players']:
        if not player[2]:
            open_game = True
    games[board_id]['open'] = open_game
    pickle.dump(games, open(GAMES_PATH + '/games.pkl', 'wb'))
    response = make_response(play(board_id=board_id))
    response.set_cookie('board_id', board_id)
    if os.path.exists(GAMES_PATH + board_id + '/board.pkl'):
        board = pickle.load(open(GAMES_PATH + board_id + '/board.pkl', 'rb'))
    else:
        flash(game.MESSAGES['game-not-found'], 'danger')
        return render_template('error.html')
    board.set_player(seat_id, player_id, name)
    pickle.dump(board, open(GAMES_PATH + str(board.get_id()) + '/board.pkl', 'wb'))
    return response


@app.route('/select')
def select():
    """
    Join existing online game
    :return: render_template
    """
    player_id = request.cookies.get('player_id')
    if not player_id:
        return redirect(url_for('hello'))
    board_id = request.args.get('game_id')
    response = make_response(play(board_id=board_id))
    response.set_cookie('board_id', board_id)
    if os.path.exists(GAMES_PATH + board_id + '/board.pkl'):
        board = pickle.load(open(GAMES_PATH + board_id + '/board.pkl', 'rb'))
    else:
        flash(game.MESSAGES['game-not-found'], 'danger')
        return render_template('error.html')
    return response


@app.route('/customize')
def customize():
    """
    Customize game
    :return: render_template
    """
    player_id = request.cookies.get('player_id')
    if not player_id:
        return redirect(url_for('hello'))
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
    player_id = request.cookies.get('player_id')
    if not player_id:
        flash(game.MESSAGES['session-expired'], 'error')
        return redirect(url_for('hello'))
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
def play(phase=None, territory=None, destination=None, board_id=None):
    """
    Function play - front controller
    :param phase: str/None
    :param territory: str/None
    :param territory: str/None
    :param destination: str/None
    :param board_id: str/None
    :return:
    """
    """Check player and load board"""
    if not board_id:
        board_id = request.cookies.get('board_id')
    player_id = request.cookies.get('player_id')
    if board_id and player_id and os.path.exists(GAMES_PATH + str(board_id) + '/board.pkl'):
        board = pickle.load(open(GAMES_PATH + str(board_id) + '/board.pkl', 'rb'))
        current_player_instances = board.get_player_instances(player_id)
    else:
        flash(game.MESSAGES['session-expired'], 'danger')
        return redirect(url_for('hello'))

    """Check if game is open"""
    games = pickle.load(open(GAMES_PATH + '/games.pkl', 'rb'))
    if games[board.get_id()]['open']:
        return game.waiting_room(board, games)

    if board.active_player() not in current_player_instances:
        return game.game(board)

    """Check phase correction"""
    if not phase:
        return game.game(board)
    if phase == 'new_phase':
        board.new_phase()
        pickle.dump(board, open(GAMES_PATH + str(board_id) + '/board.pkl', 'wb'))
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
            if players[str(i)][0] == 'human-player':
                online = True
    map_name = request.args.get('map_name')
    game_name = request.args.get('game_name')
    board = new(map_name, game_name, players)

    games = pickle.load(open(GAMES_PATH + '/games.pkl', 'rb'))
    games[board.get_id()] = {'game_name': board.get_game_name(),
                             'open': online,
                             'players': sorted([[pl.get_id(), pl.get_player_id(), pl.get_name()]
                                                for pl in board.get_players()])
                             }
    pickle.dump(games, open(GAMES_PATH + '/games.pkl', 'wb'))

    if online:
        response = make_response(game.waiting_room(board, games))
    else:
        response = make_response(game.game(board))
    response.set_cookie('board_id', str(board.get_id()))
    return response


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
    games = pickle.load(open(GAMES_PATH + '/games.pkl', 'rb'))
    shutil.rmtree(GAMES_PATH + str(board_id))
    del games[board_id]
    pickle.dump(games, open(GAMES_PATH + '/games.pkl', 'wb'))
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
    player_id = request.cookies.get('player_id')
    if board_id and player_id and os.path.exists(GAMES_PATH + str(board_id) + '/board.pkl'):
        board = pickle.load(open(GAMES_PATH + str(board_id) + '/board.pkl', 'rb'))
    else:
        flash(game.MESSAGES['session-expired'], 'danger')
        return redirect(url_for('hello'))
    if request.args.get('confirm'):
        games = pickle.load(open(GAMES_PATH + '/games.pkl', 'rb'))
        shutil.rmtree(GAMES_PATH + str(board_id))
        del games[board.get_id()]
        pickle.dump(games, open(GAMES_PATH + '/games.pkl', 'wb'))
        flash(game.MESSAGES['game-deleted'], 'success')
        return redirect(url_for('hello'))
    else:
        return game.render_board(board, abandon=True)


def new(map_name, game_name, players):
    """
    New game creator
    :param map_name: string
    :param game_name: string
    :param players: dict
    :return: Board
    """
    board_id = id_generator()
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
