from flask import render_template
from players import Human, Computer
import pickle


def game(board):
    turn = board.turn()
    active_player = board.active_player()

    while type(active_player) is Computer:
        if turn[0] == 'initial':
            board.new_turn()
            active_player = board.active_player()
        elif turn[0] == 'initial-reinforce':
            board.new_turn()
            active_player = board.active_player()
        elif turn[0] == 'deploy':
            board.new_turn()
            active_player = board.active_player()
        elif turn[0] == 'attack-chose':
            board.new_turn()
            active_player = board.active_player()
        elif turn[0] == 'attack-commit':
            board.new_turn()
            active_player = board.active_player()
        elif turn[0] == 'fortify-chose':
            board.new_turn()
            active_player = board.active_player()
        elif turn[0] == 'fortify-commit':
            board.new_turn()
            active_player = board.active_player()
        else:
            return 'Error!'

    if type(active_player) is Human:
        return render_board(board)


def render_board(board, chosen_territory=None, message=None):
    turn = board.turn()
    active_territories = []
    if turn[0] == 'initial':
        active_territories = board.player_territories('noplayer')
    if turn[0] == 'initial-reinforce':
        active_player = board.active_player()
        active_territories = board.player_territories(active_player)
    if turn[0] == 'deploy':
        pass
    if turn[0] == 'attack-chose':
        pass
    if turn[0] == 'attack-commit':
        pass
    if turn[0] == 'fortify-chose':
        pass
    if turn[0] == 'fortify-commit':
        pass

    pickle.dump(board, open('board.pkl', 'wb'))

    return render_template('play.html', map=board.get_map_name(), territories=board.get_territories(),
                           continents=board.get_continents(), turn=board.turn(), player=[board.active_player().repr_id(), board.active_player().get_name()],
                           active_territories=active_territories, units_left=board.active_player().get_units(), message=message)