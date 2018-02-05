from flask import Flask, request, render_template, redirect, url_for, make_response, flash
import os
import pickle
import importlib
import game
import shutil
import random

app = Flask(__name__)
GAMES_LIST = {}
MESSAGES = {
    'illegal-initial': 'Ruch niedozwolony! W tej fazie możesz zajmować tylko niczyje terytoria.',
    'illegal-deployment': 'Hola hola! Możesz wzmacniać tylko swoje terytoria.',
    'illegal-chose': 'Ruch niedozwolony! Na te ziemie nie sięga Twoja władza. Jeśli chcesz nim zarządzać, to musisz je najpierw podbić.',
    'illegal-too-little': 'Ruch niedozwolony! Masz za mało wojska na tym terytorium, by atakować',
    'illegal-not-neighbour': 'Ruch niedozwolony! Atakować wolno tylko z terytoriów granicznych.',
    'illegal-no-group': 'To terytorium nie jest połączone z żadnym innym należącym do ciebie. Nigdzie stąd nie dojdziesz.',
    'illegal-no-connection': 'Ruch niedozwolony! Między tymi terytoriami nie ma połączenia.',
    'illegal-attack-self': 'Ruch niedozwolony! Atakujesz własne terytorium?',
    'illegal-movement': 'Ruch niedozwolony! Aby dotrzeć do tego terytorium, musiałbyś wytrenować spadochroniarzy. Ale nie ma ich w tej grze.',
    'wrong-phase': 'Ej, spokojnie, nie klikaj tak szybko bo nie nadążam. Pozwól mi się załadować.',
    'chose-cancelled': 'Wybór prowincji anulowany',
    'attack-success': 'Atak zakończył się powodzeniem',
    'attack-fail': 'Niestety, atak zakończył się porażką',
    'not-enough-units': 'Hola hola! Nie masz dość jednostek na takie zabawy.',
    'session-expired': 'Przepraszamy, Twoja sesja wygasła.',
    'game-created': 'Nowa gra utworzona',
    'game-deleted': 'Dotychczasowa gra została zakończona'
}


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


@app.route('/play/initial/<territory>', methods=['GET', 'POST'])
def initial(territory=None):
    """
    Initial controller
    :param territory: string
    :return: game -> render_template
    """
    board_id = request.cookies.get('board_id')
    if board_id and os.path.exists(GAMES_PATH + str(board_id) + '/board.pkl'):
        board = pickle.load(open(GAMES_PATH + str(board_id) + '/board.pkl', 'rb'))
    else:
        flash(MESSAGES['session-expired'], 'danger')
        return render_template('error.html')
    if board.get_phase() != 'initial':
        flash(MESSAGES['wrong-phase'], 'danger')
        return game.render_board(board)
    active_player = board.active_player()
    if board.get_territory(territory).get_owner() is None:
        board.set_owner(territory, active_player, 1)
        active_player.decrease_units(1)
    else:
        flash(MESSAGES['illegal-initial'], 'danger')
        return game.render_board(board)
    board.new_phase()
    pickle.dump(board, open(GAMES_PATH + str(board_id) + '/board.pkl', 'wb'))
    return game.game(board)


@app.route('/play/initial-reinforce/<territory>', methods=['GET', 'POST'])
def initial_reinforce(territory=None):
    """
    Initial reinforce controller
    :param territory: string
    :return: game -> render_template
    """
    board_id = request.cookies.get('board_id')
    if board_id and os.path.exists(GAMES_PATH + str(board_id) + '/board.pkl'):
        board = pickle.load(open(GAMES_PATH + str(board_id) + '/board.pkl', 'rb'))
    else:
        flash(MESSAGES['session-expired'], 'danger')
        return render_template('error.html')
    if board.get_phase() != 'initial-reinforce':
        flash(MESSAGES['wrong-phase'], 'danger')
        return game.render_board(board)
    active_player = board.active_player()
    if board.get_territory(territory).get_owner() == board.active_player():
        board.get_territory(territory).reinforce(1)
        active_player.decrease_units(1)
    else:
        flash(MESSAGES['illegal-deployment'], 'danger')
        return game.render_board(board)
    board.new_phase()
    pickle.dump(board, open(GAMES_PATH + str(board_id) + '/board.pkl', 'wb'))
    return game.game(board)


@app.route('/play/deployment/<territory>', methods=['GET', 'POST'])
def deploy(territory):
    """
    Deployment controller
    :param territory: string
    :return: game -> render_template
    """
    board_id = request.cookies.get('board_id')
    if board_id and os.path.exists(GAMES_PATH + str(board_id) + '/board.pkl'):
        board = pickle.load(open(GAMES_PATH + str(board_id) + '/board.pkl', 'rb'))
    else:
        flash(MESSAGES['session-expired'], 'danger')
        return render_template('error.html')
    if board.get_phase() != 'deployment':
        flash(MESSAGES['wrong-phase'], 'danger')
        return game.render_board(board)
    active_player = board.active_player()
    if active_player.get_units() <= 0:
        flash(MESSAGES['not-enough-units'], 'danger')
        return game.render_board(board)
    if board.get_territory(territory).get_owner() != board.active_player():
        flash(MESSAGES['illegal-deployment'], 'danger')
        return game.render_board(board)
    else:
        territory = board.get_territory(territory)
        if request.args.get('units'):
            units = int(request.args.get('units'))
            territory.reinforce(units)
            active_player.decrease_units(units)
        elif active_player.get_units() == 1:
            territory.reinforce(1)
            active_player.decrease_units(1)
        else:
            return game.render_board(board, destination_territory=territory)
    if active_player.get_units() <= 0:
        board.new_phase()
    pickle.dump(board, open(GAMES_PATH + str(board_id) + '/board.pkl', 'wb'))
    return game.game(board)


@app.route('/play/attack/<territory>', methods=['GET', 'POST'])
def attack_choose(territory):
    """
    Attack-choosing controller
    :param territory: string
    :return: game -> render_template
    """
    board_id = request.cookies.get('board_id')
    if board_id and os.path.exists(GAMES_PATH + str(board_id) + '/board.pkl'):
        board = pickle.load(open(GAMES_PATH + str(board_id) + '/board.pkl', 'rb'))
    else:
        flash(MESSAGES['session-expired'], 'danger')
        return render_template('error.html')
    if board.get_phase() != 'attack':
        flash(MESSAGES['wrong-phase'], 'danger')
        return game.render_board(board)
    territory = board.get_territory(territory)
    if territory.get_owner() != board.active_player():
        flash(MESSAGES['illegal-chose'], 'danger')
        return game.render_board(board)
    if territory.get_strength() < 2:
        flash(MESSAGES['illegal-too-little'], 'danger')
        return game.render_board(board)
    if territory.is_border() is False:
        flash(MESSAGES['illegal-not-neighbour'], 'danger')
        return game.render_board(board)
    return game.render_board(board, chosen_territory=territory)


@app.route('/play/attack/<territory_from>/<territory_to>', methods=['GET', 'POST'])
def attack_commit(territory_from, territory_to):
    """
    Attack-committing controller
    :param territory_from: string
    :param territory_to: string
    :return: game -> render_template
    """
    board_id = request.cookies.get('board_id')
    if board_id and os.path.exists(GAMES_PATH + str(board_id) + '/board.pkl'):
        board = pickle.load(open(GAMES_PATH + str(board_id) + '/board.pkl', 'rb'))
    else:
        flash(MESSAGES['session-expired'], 'danger')
        return render_template('error.html')
    if board.get_phase() != 'attack':
        flash(MESSAGES['wrong-phase'], 'danger')
        return game.render_board(board)

    territory_from = board.get_territory(territory_from)
    territory_to = board.get_territory(territory_to)
    if territory_to == territory_from:
        flash(MESSAGES['chose-cancelled'], 'info')
        return game.render_board(board)

    if territory_from.get_owner() != board.active_player():
        flash(MESSAGES['illegal-chose'], 'danger')
        return game.render_board(board)
    if territory_from.get_strength() < 2:
        flash(MESSAGES['illegal-too-little'], 'danger')
        return game.render_board(board)
    if territory_to.get_owner() == board.active_player():
        flash(MESSAGES['illegal-attack-self'], 'danger')
        return game.render_board(board)
    if territory_to not in territory_from.get_neighbours():
        flash(MESSAGES['illegal-movement'], 'danger')
        return game.render_board(board)

    elif request.args.get('units'):
        units = int(request.args.get('units'))
        if units < 1 or units >= territory_from.get_strength():
            flash(MESSAGES['not-enough-units'], 'danger')
            return game.render_board(board)
        if board.attack(territory_from, territory_to, units):
            flash(MESSAGES['attack-success'], 'success')
            if board.check_elimination():
                pickle.dump(board, open(GAMES_PATH + str(board_id) + '/board.pkl', 'wb'))
                return end_game()
        else:
            flash(MESSAGES['attack-fail'], 'danger')
        pickle.dump(board, open(GAMES_PATH + str(board_id) + '/board.pkl', 'wb'))
        return game.render_board(board)
    else:
        return game.render_board(board, chosen_territory=territory_from, destination_territory=territory_to)


@app.route('/play/fortify/<territory>', methods=['GET', 'POST'])
def fortify_choose(territory):
    """
    Fortification-choosing controller
    :param territory: string
    :return: game -> render_template
    """
    board_id = request.cookies.get('board_id')
    if board_id and os.path.exists(GAMES_PATH + str(board_id) + '/board.pkl'):
        board = pickle.load(open(GAMES_PATH + str(board_id) + '/board.pkl', 'rb'))
    else:
        flash(MESSAGES['session-expired'], 'danger')
        return render_template('error.html')
    if board.get_phase() != 'fortify':
        flash(MESSAGES['wrong-phase'], 'danger')
        return game.render_board(board)

    territory = board.get_territory(territory)
    if territory.get_owner() != board.active_player():
        flash(MESSAGES['illegal-chose'], 'danger')
        return game.render_board(board)
    if territory.get_strength() < 2:
        flash(MESSAGES['illegal-too-little'], 'danger')
        return game.render_board(board)
    if len(territory.get_connected()) < 2:
        flash(MESSAGES['illegal-no-group'], 'danger')
        return game.render_board(board)

    pickle.dump(board, open(GAMES_PATH + str(board_id) + '/board.pkl', 'wb'))
    return game.render_board(board, chosen_territory=territory)


@app.route('/play/fortify/<territory_from>/<territory_to>', methods=['GET', 'POST'])
def fortify_commit(territory_from, territory_to):
    """
    Fortification-committing controller
    :param territory_from: string
    :param territory_to: string
    :return: game -> render_template
    """
    board_id = request.cookies.get('board_id')
    if board_id and os.path.exists(GAMES_PATH + str(board_id) + '/board.pkl'):
        board = pickle.load(open(GAMES_PATH + str(board_id) + '/board.pkl', 'rb'))
    else:
        flash(MESSAGES['session-expired'], 'danger')
        return render_template('error.html')
    if board.get_phase() != 'fortify':
        flash(MESSAGES['wrong-phase'], 'danger')
        return game.render_board(board)
    territory_from = board.get_territory(territory_from)
    territory_to = board.get_territory(territory_to)
    if territory_to == territory_from:
        flash(MESSAGES['chose-cancelled'], 'info')
        return game.render_board(board)

    if territory_from.get_owner() != board.active_player():
        flash(MESSAGES['illegal-chose'], 'danger')
        return game.render_board(board)
    if territory_from.get_strength() < 2:
        flash(MESSAGES['illegal-too-little'], 'danger')
        return game.render_board(board)
    if territory_from not in territory_to.get_connected():
        flash(MESSAGES['illegal-no-connection'], 'danger')
        return game.render_board(board)

    if request.args.get('units'):
        units = int(request.args.get('units'))
        if units < 1 or units >= territory_from.get_strength():
            flash(MESSAGES['not-enough-units'], 'danger')
            return game.render_board(board)
        board.fortify(territory_from, territory_to, units)
        board.new_phase()
        pickle.dump(board, open(GAMES_PATH + str(board_id) + '/board.pkl', 'wb'))
        return game.game(board)
    else:
        return game.render_board(board, chosen_territory=territory_from, destination_territory=territory_to)


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
        flash(MESSAGES['session-expired'], 'danger')
        return render_template('error.html')
    board.new_phase()
    pickle.dump(board, open(GAMES_PATH + str(board_id) + '/board.pkl', 'wb'))
    return game.game(board)


@app.route('/play', methods=['GET'])
def play():
    """
    Just render board
    In general unused
    :return: game -> render_template
    """
    board_id = request.cookies.get('board_id')
    if board_id and os.path.exists(GAMES_PATH + str(board_id) + '/board.pkl'):
        board = pickle.load(open(GAMES_PATH + str(board_id) + '/board.pkl', 'rb'))
    else:
        flash(MESSAGES['session-expired'], 'danger')
        return render_template('error.html')
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
        flash(MESSAGES['session-expired'], 'danger')
        return render_template('error.html')
    winner = board.alive_players()[0]
    shutil.rmtree(GAMES_PATH + str(board_id))
    flash(MESSAGES['game-deleted'], 'success')
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
        flash(MESSAGES['session-expired'], 'danger')
        return render_template('error.html')
    if request.args.get('confirm'):
        shutil.rmtree(GAMES_PATH + str(board_id))
        flash(MESSAGES['game-deleted'], 'success')
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
        flash(MESSAGES['game-deleted'], 'success')
    board_id = next(ID_GENERATOR)
    importlib.import_module('static.maps.' + map_name)
    board = importlib.import_module('.board', package='static.maps.' + map_name)
    board = board.create_map(players, map_name, game_name, board_id)
    os.mkdir(GAMES_PATH + str(board_id))
    flash(MESSAGES['game-created'], 'success')
    pickle.dump(board, open(GAMES_PATH + str(board_id) + '/board.pkl', 'wb'))
    return board


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(host="0.0.0.0", port=5017)
