from flask import Flask, request, render_template, redirect, url_for
import random, os, pickle, importlib, game

app = Flask(__name__)
GAMES_LIST = {}
messages = {
    'illegal-initial': 'Ruch niedozwolony! W tej fazie możesz zajmować tylko niczyje terytoria.',
    'illegal-deployment': 'Ruch niedozwolony! Miło z Twojej strony,  że chcesz pomóc wrogowi, ale możesz niestety wzmacniać tylko swoje terytoria.',
    'illegal-chose': 'Ruch niedozwolony! Na te ziemie nie sięga Twoja władza. Jeśli chcesz nim zarządzać, to musisz je najpierw podbić.',
    'illegal-too-little': 'Ruch niedozwolony! Masz za mało wojska na tym terytorium, by atakować',
    'illegal-attack-self': 'Ruch niedozwolony! Atakujesz własne terytorium?',
    'illegal-movement': 'Ruch niedozwolony! Aby dotrzeć do tego terytorium, musiałbyś wytrenować spadochroniarzy. Ale nie ma ich w tej grze.',
    'wrong-phase': 'Zaraz, coś tu nie gra... Czy aby nie pomyliłeś fazy gry?',
    'chose-cancelled': 'Wybór prowincji anulowany'
}

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
        return game.render_board(board, message=messages['illegal-initial'])
    board.new_phase()
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
        return game.render_board(board, message=messages['illegal-deployment'])
    board.new_phase()
    pickle.dump(board, open('board.pkl', 'wb'))
    return game.game(board)


@app.route('/play/deployment/<territory>', methods=['GET', 'POST'])
def deploy(territory):
    board = pickle.load(open('board.pkl', 'rb'))
    active_player = board.active_player()
    if board.territories[territory].get_owner() == board.active_player():
        board.territories[territory].reinforce(1)
        active_player.decrease_units(1)
    else:
        return game.render_board(board, message=messages['illegal-deployment'])
    if active_player.get_units() <= 0:
        board.new_phase()
    pickle.dump(board, open('board.pkl', 'wb'))
    return game.game(board)


@app.route('/play/attack/<territory>', methods=['GET', 'POST'])
def attack_choose(territory):
    board = pickle.load(open('board.pkl', 'rb'))
    territory = board.territories[territory]
    if territory.get_owner() != board.active_player():
        return game.render_board(board, message=messages['illegal-chose'])
    if territory.get_strength() == 1:
        return game.render_board(board, message=messages['illegal-too-little'])
    pickle.dump(board, open('board.pkl', 'wb'))
    return game.render_board(board, chosen_territory=territory)

@app.route('/play/attack/<territory_from>/<territory_to>', methods=['GET', 'POST'])
def attack_commit(territory_from, territory_to):
    board = pickle.load(open('board.pkl', 'rb'))
    territory_from = board.territories[territory_from]
    territory_to = board.territories[territory_to]
    if territory_to == territory_from:
        return game.render_board(board, message=messages['chose-cancelled'])
    # do zrobienia: sprawdzenie poprawności, atak
    pickle.dump(board, open('board.pkl', 'wb'))
    return game.game(board)


@app.route('/play/fortify/<territory>', methods=['GET', 'POST'])
def fortify_choose(territory):
    board = pickle.load(open('board.pkl', 'rb'))
    territory = board.territories[territory]
    if territory.get_owner() != board.active_player():
        return game.render_board(board, message=messages['illegal-chose'])
    if territory.get_strength() == 1:
        return game.render_board(board, message=messages['illegal-too-little'])
    pickle.dump(board, open('board.pkl', 'wb'))
    return game.render_board(board, chosen_territory=territory)

@app.route('/play/fortify/<territory_from>/<territory_to>', methods=['GET', 'POST'])
def fortify_commit(territory_from, territory_to):
    board = pickle.load(open('board.pkl', 'rb'))
    territory_from = board.territories[territory_from]
    territory_to = board.territories[territory_to]
    if territory_to == territory_from:
        return game.render_board(board, message=messages['chose-cancelled'])
    # do zrobienia: sprawdzenie poprawności, fortyfikacja
    board.new_phase()
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


@app.route('/newturn', methods=['GET'])
def newturn():
    board = pickle.load(open('board.pkl', 'rb'))
    board.new_phase()
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

