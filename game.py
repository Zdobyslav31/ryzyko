from flask import render_template
from players import Human, Computer
import pickle
import collections
from ryzyko import end_game, GAMES_PATH


def game(board):
    """
    Main game controller
    Called after each player's action
    Handles Computer's actions
    :param board: Board
    :return: render_board() -> render_template()
    """
    phase = board.get_phase()
    active_player = board.active_player()
    if len(board.alive_players()) <= 1:
        return end_game()
    current_log = {}

    while issubclass(type(active_player), Computer) or active_player.is_eliminated():
        if active_player.is_eliminated():
            board.new_turn()
            active_player = board.active_player()
            phase = board.get_phase()
        elif phase == 'initial':
            active_player.initial(board)
            board.new_phase()
            active_player = board.active_player()
            phase = board.get_phase()
        elif phase == 'initial-reinforce':
            active_player.deploy_once(board)
            board.new_phase()
            active_player = board.active_player()
            phase = board.get_phase()
        elif phase == 'deployment':
            active_player.deploy(board)
            board.new_phase()
            active_player = board.active_player()
            phase = board.get_phase()
        elif phase == 'attack':
            active_player.cast_attacks(board)
            if board.check_elimination():
                pickle.dump(board, open(GAMES_PATH + str(board.get_id()) + '/board.pkl', 'wb'))
                return end_game()
            board.new_phase()
            active_player = board.active_player()
            phase = board.get_phase()
        elif phase == 'fortify':
            active_player.fortify(board)
            current_log[board.get_turn()] = active_player.get_log()
            board.new_phase()
            active_player = board.active_player()
            phase = board.get_phase()
        else:
            return 'Error!'

    if type(active_player) is Human:
        log = collections.OrderedDict(sorted(current_log.items()))
        return render_board(board, log=log)


def render_board(board, chosen_territory=None, destination_territory=None, message=None, log=None):
    """
    Board renderer
    Renders board for player according to phase
    :param board:
    :param chosen_territory: Territory/None
    :param destination_territory: Territory/None
    :param message: string/None
    :param log: dict/none
    :return: render_template()
    """
    if len(board.alive_players()) <= 1:
        return end_game()
    phase = board.get_phase()
    active_player = board.active_player()
    active_territories = []
    question_box = []
    if phase == 'initial':
        if active_player.get_units() <= 0:
            board.new_phase()
            return game(board)
        active_territories = [ter.get_name() for ter in board.get_territories() if ter.get_owner() is None]
    if phase == 'initial-reinforce':
        if active_player.get_units() <= 0:
            board.new_phase()
            return game(board)
        active_territories = [ter.get_name() for ter in board.player_territories(active_player)]
    if phase == 'deployment':
        if active_player.get_units() <= 0:
            return game(board)
        active_territories = [ter.get_name() for ter in board.player_territories(active_player)]
    if phase == 'attack':
        if destination_territory:
            question_box = [chosen_territory.get_title(), destination_territory.get_title(),
                            chosen_territory.get_strength()-1]
        elif chosen_territory:
            active_territories = [ter.get_name() for ter in chosen_territory.get_neighbours()
                                  if ter.get_owner() != board.active_player()] + [chosen_territory.get_name()]
        else:
            active_territories = [ter.get_name() for ter in board.player_territories(active_player)
                                  if ter.get_strength() > 1 and ter.is_border()]
            if len(active_territories) == 0:
                board.new_phase()
                return game(board)
    if phase == 'fortify':
        if destination_territory:
            question_box = [
                chosen_territory.get_title(),
                destination_territory.get_title(),
                chosen_territory.get_strength()-1
            ]
        if chosen_territory:
            active_territories = [ter.get_name() for ter in list(chosen_territory.get_connected())]
        else:
            active_territories = [ter.get_name() for ter in board.player_territories(active_player)
                                  if ter.get_strength() > 1 and len(ter.get_connected()) > 1]
            if len(active_territories) == 0:
                board.new_phase()
                return game(board)

    pickle.dump(board, open(GAMES_PATH + str(board.get_id()) + '/board.pkl', 'wb'))
    if chosen_territory:
        chosen_territory = chosen_territory.get_name()
    if destination_territory:
        destination_territory = destination_territory.get_name()

    return render_template('play.html', map=board.get_map_name(), territories=board.repr_territories(),
                           continents=board.repr_continents(), phase=board.get_phase(), round=board.get_round(),
                           player=[board.active_player().repr_id(), board.active_player().get_name()],
                           active_territories=active_territories, units_left=board.active_player().get_units(),
                           message=message,  question_box=question_box, log=log,
                           chosen_territory=chosen_territory, destination_territory=destination_territory)
