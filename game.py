from flask import render_template
from players import Human, Computer
import pickle
from ryzyko import end_game


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

    while type(active_player) is Computer or active_player.is_eliminated():
        if active_player.is_eliminated():
            board.new_turn()
            active_player = board.active_player()
        elif phase == 'initial':
            board.new_phase()
            active_player = board.active_player()
        elif phase == 'initial-reinforce':
            board.new_phase()
            active_player = board.active_player()
        elif phase == 'deployment':
            board.new_phase()
            active_player = board.active_player()
        elif phase == 'attack':
            board.new_phase()
            active_player = board.active_player()
        elif phase == 'fortify':
            board.new_phase()
            active_player = board.active_player()
        else:
            return 'Error!'

    if type(active_player) is Human:
        return render_board(board)


def render_board(board, chosen_territory=None, destination_territory=None, message=None):
    """
    Board renderer
    Renders board for player according to phase
    :param board:
    :param chosen_territory: Territory/None
    :param destination_territory: Territory/None
    :param message: string/None
    :return: render_template()
    """
    if len(board.alive_players()) <= 1:
        return end_game()
    phase = board.get_phase()
    active_player = board.active_player()
    active_territories = []
    question_box=[]
    if phase == 'initial':
        if active_player.get_units() <= 0:
            return game(board)
        active_territories = [ter.get_name() for ter in board.get_territories() if ter.get_owner() is None]
    if phase == 'initial-reinforce':
        if active_player.get_units() <= 0:
            return game(board)
        active_territories = [ter.get_name() for ter in board.player_territories(active_player)]
    if phase == 'deployment':
        if active_player.get_units() <= 0:
            return game(board)
        active_territories = [ter.get_name() for ter in board.player_territories(active_player)]
    if phase == 'attack':
        if destination_territory:
            question_box = [chosen_territory.get_title(), destination_territory.get_title(), chosen_territory.get_strength()-1]
        elif chosen_territory:
            active_territories = [ter.get_name() for ter in chosen_territory.get_neighbours()
                                  if ter.get_owner() != board.active_player()] + [chosen_territory.get_name()]
        else:
            active_territories = [ter.get_name() for ter in board.player_territories(active_player)
                                  if ter.get_strength() > 1 and ter.is_border()]
    if phase == 'fortify':
        if destination_territory:
            question_box = [chosen_territory.get_title(), destination_territory.get_title(), chosen_territory.get_strength()-1]
        if chosen_territory:
            active_territories = [ter.get_name() for ter in list(chosen_territory.get_connected())]
        else:
            active_territories = [ter.get_name() for ter in board.player_territories(active_player)
                                  if ter.get_strength() > 1 and len(ter.get_connected()) > 1]

    pickle.dump(board, open('board.pkl', 'wb'))
    if chosen_territory:
        chosen_territory = chosen_territory.get_name()
    if destination_territory:
        destination_territory = destination_territory.get_name()

    return render_template('play.html', map=board.get_map_name(), territories=board.repr_territories(),
                           continents=board.repr_continents(), phase=board.get_phase(), round=board.get_round(),
                           player=[board.active_player().repr_id(), board.active_player().get_name()],
                           active_territories=active_territories, units_left=board.active_player().get_units(),
                           message=message,  question_box=question_box,
                           chosen_territory=chosen_territory, destination_territory=destination_territory)