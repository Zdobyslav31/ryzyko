from flask import Flask, request, render_template, redirect, url_for
import random, os, pickle, importlib

app = Flask(__name__)
GAMES_LIST = {}


@app.route('/')
def hello():
    return render_template('hello.html')


"""
Test
"""
@app.route('/test')
def test(compvalue=None):

    if request.args.get('test'):
        return render_template('test.html', form=False, test=request.args.get('test'))
    elif compvalue:
        return render_template('test.html', form=False, test=compvalue)
    else:
        return render_template('test.html', form=True, test=None )


@app.route('/testing')
def testing():
    race = request.args.get('race')
    if race == 'computer':
        return test(31)
    elif race == 'human':
        return render_template('get_test_data.html')
    else:
        return 'Bad race'

"""
/test
"""


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


def new(map_name, players):
    # id = random.randrange(0,100)

    importlib.import_module('static.' + map_name)
    board = importlib.import_module('.board', package='static.' + map_name)

    board = board.create_map(players, map_name)
    # GAMES_LIST[id] = board
    # session['boardid'] = id
    return board


@app.route('/play/initial/<territory>', methods=['GET', 'POST'])
def initial(territory=None):
    board = pickle.load(open('board.pkl', 'rb'))
    active_player = board.active_player()
    if board.territories[territory].get_owner() == 'noplayer':
        board.set_owner(territory, 'player' + str(active_player.get_id()), 1)
        active_player.decrease_units(1)
    else:
        return 'Action not allowed!'

    board.new_turn()

    pickle.dump(board, open('board.pkl', 'wb'))
    active_territories = board.player_territories('player' + str(board.active_player()))
    active_territories += board.player_territories('noplayer')
    return render_board(board, active_territories)

@app.route('/newgame', methods=['GET', 'POST'])
def newgame():
    players = {}
    for i in range(1,int(request.args.get('players_num')) + 1):
        players[str(i)] = [request.args.get('player' + str(i)), request.args.get('player' + str(i) + 'name')]
    map_name = request.args.get('map_name')
    board = new(map_name, players)
    pickle.dump(board, open('board.pkl', 'wb'))
    active_territories = board.player_territories('player' + str(board.active_player()))
    active_territories += board.player_territories('noplayer')
    return render_board(board, active_territories)


@app.route('/play', methods=['GET', 'POST'])
def play():
    return 'Oooops'


def render_board(board, active_territories):
    return render_template('play.html', map=board.get_map_name(), territories=board.get_territories(),
                           continents=board.get_continents(), turn=board.turn(), player=board.active_player().get_name(),
                           active_territories=active_territories, units_left=board.active_player().get_units())


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run()

