from ryzyko import render_board
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
        elif turn[0] == 'deploy':
            board.new_turn()
        elif turn[0] == 'attack-chose':
            board.new_turn()
        elif turn[0] == 'attack-commit':
            board.new_turn()
        elif turn[0] == 'fortelify-chose':
            board.new_turn()
        elif turn[0] == 'fortify-commit':
            board.new_turn()
        else:
            return 'Error!'

    if type(active_player) is Human:
        if turn[0] == 'initial':
            return render_initial(board)
        if turn[0] == 'initial-reinforce':
            return render_initial(board)
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


def render_initial(board):
    active_territories = board.player_territories('player' + str(board.active_player()))
    active_territories += board.player_territories('noplayer')
    pickle.dump(board, open('board.pkl', 'wb'))
    return render_board(board, active_territories)