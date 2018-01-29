from flask import render_template
from players import Human, Computer
import pickle


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

    while type(active_player) is Computer:
        if phase == 'initial':
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


def render_board(board, chosen_territory=None, message=None):
    """
    Board renderer
    Renders board for player according to phase
    :param board:
    :param chosen_territory: Territory
    :param message: string
    :return: render_template()
    """
    phase = board.get_phase()
    active_player = board.active_player()
    active_territories = []
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
        if chosen_territory:
            active_territories = [ter.get_name() for ter in chosen_territory.get_neighbours()
                                  if ter.get_owner() != board.active_player()] + [chosen_territory.get_name()]
        else:
            active_territories = [ter.get_name() for ter in board.player_territories(active_player)
                                  if ter.get_strength() > 1 and ter.is_border()]
    if phase == 'fortify':
        if chosen_territory:
            active_territories = [ter.get_name() for ter in list(chosen_territory.get_connected())]
        else:
            active_territories = [ter.get_name() for ter in board.player_territories(active_player)
                                  if ter.get_strength() > 1 and len(ter.get_connected()) > 1]

    pickle.dump(board, open('board.pkl', 'wb'))
    if chosen_territory:
        chosen_territory = chosen_territory.get_name()

    return render_template('play.html', map=board.get_map_name(), territories=board.repr_territories(),
                           continents=board.repr_continents(), phase=board.get_phase(), round=board.get_round(),
                           player=[board.active_player().repr_id(), board.active_player().get_name()],
                           active_territories=active_territories, units_left=board.active_player().get_units(),
                           message=message, chosen_territory=chosen_territory)