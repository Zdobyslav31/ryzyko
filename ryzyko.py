from flask import Flask, request, render_template, redirect, url_for
import random, os, pickle, importlib, game

app = Flask(__name__)
GAMES_LIST = {}


@app.route('/')
def hello():
    return render_template('hello.html')


@app.route('/customize')
def customize():
    return render_template('customize.html')


@app.route('/choose_players')
def choose_players():
    if request.args.get('newgame'):
        map_name = request.args.get('map_name')
        players_num = int(request.args.get('players'))
        return render_template('choose_players.html', players_num=players_num, map_name=map_name)
    else:
        return redirect(url_for('customize'))


@app.route('/play/initial/<territory>', methods=['GET', 'POST'])
def initial(territory=None):
    board = pickle.load(open('board.pkl', 'rb'))
    active_player = board.active_player()
    if board.territories[territory].get_owner() == 'noplayer':
        board.set_owner(territory, active_player, 1)
        active_player.decrease_units(1)
    else:
        return game.render_board(board, message='Ruch niedozwolony! W tej fazie możesz zajmować tylko niczyje terytoria.')
    board.new_turn()
    pickle.dump(board, open('board.pkl', 'wb'))
    return game.game(board)


@app.route('/play/initial-reinforce/<territory>', methods=['GET', 'POST'])
def initial_reinforce(territory=None):
    board = pickle.load(open('board.pkl', 'rb'))
    active_player = board.active_player()
    if board.territories[territory].get_owner() == board.active_player():
        board.territories[territory].reinforce(1)
        active_player.decrease_units(1)
    else:
        return game.render_board(board, message='Ruch niedozwolony! Miło z Twojej strony,  że chcesz pomóc wrogowi, ale możesz niestety wzmacniać tylko swoje terytoria.')
    board.new_turn()
    pickle.dump(board, open('board.pkl', 'wb'))
    return game.game(board)


@app.route('/play/attack-chose/<territory>', methods=['GET', 'POST'])
def attack_choose(territory=None):
    board = pickle.load(open('board.pkl', 'rb'))
    if board.territories[territory].get_owner() == board.active_player():
        return game.render_board(board, message='Ruch niedozwolony! Atakujesz własne terytorium, geniuszu?')
    board.new_turn()
    pickle.dump(board, open('board.pkl', 'wb'))
    return game.game(board)


@app.route('/newgame', methods=['GET', 'POST'])
def newgame():
    players = {}
    for i in range(1,int(request.args.get('players_num')) + 1):
        players[str(i)] = [request.args.get('player' + str(i)), request.args.get('player' + str(i) + 'name')]
    map_name = request.args.get('map_name')
    board = new(map_name, players)
    pickle.dump(board, open('board.pkl', 'wb'))

    return game.game(board)


@app.route('/play', methods=['GET', 'POST'])
def play():
    return 'Oooops'


"""Funkcje pomocnicze"""


def new(map_name, players):
    # id = random.randrange(0,100)

    importlib.import_module('static.' + map_name)
    board = importlib.import_module('.board', package='static.' + map_name)

    board = board.create_map(players, map_name)
    # GAMES_LIST[id] = board
    # session['boardid'] = id
    return board


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run()   #tu jako parametry host, port, debug - przykłady na wierzbie /home/zajecia/interfejs

