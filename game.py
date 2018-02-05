from flask import render_template, flash, request
from players import Human, Computer
import pickle
import collections
from ryzyko import end_game, GAMES_PATH


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


def initial(board, territory):
    """
    Initial phase controller
    :param board: Board
    :param territory: string
    :return:
    """
    active_player = board.active_player()
    if board.get_territory(territory).get_owner() is None:
        board.set_owner(territory, active_player, 1)
        active_player.decrease_units(1)
    else:
        flash(MESSAGES['illegal-initial'], 'danger')
        return render_board(board)
    board.new_phase()
    pickle.dump(board, open(GAMES_PATH + str(board.get_id()) + '/board.pkl', 'wb'))
    return game(board)


def initial_reinforce(board, territory):
    """
    Initial reinforce phase controller
    :param board: Board
    :param territory: string
    :return:
    """
    active_player = board.active_player()
    if board.get_territory(territory).get_owner() == board.active_player():
        board.get_territory(territory).reinforce(1)
        active_player.decrease_units(1)
    else:
        flash(MESSAGES['illegal-deployment'], 'danger')
        return render_board(board)
    board.new_phase()
    pickle.dump(board, open(GAMES_PATH + str(board.get_id()) + '/board.pkl', 'wb'))
    return game(board)


def deploy(board, territory):
    """
    Deployment phase controller
    :param board: Board
    :param territory: string
    :return:
    """
    active_player = board.active_player()
    if active_player.get_units() <= 0:
        flash(MESSAGES['not-enough-units'], 'danger')
        return render_board(board)
    if board.get_territory(territory).get_owner() != board.active_player():
        flash(MESSAGES['illegal-deployment'], 'danger')
        return render_board(board)
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
            return render_board(board, destination_territory=territory)
    if active_player.get_units() <= 0:
        board.new_phase()
    pickle.dump(board, open(GAMES_PATH + str(board.get_id()) + '/board.pkl', 'wb'))
    return game(board)


def attack(board, territory, destination):
    """
    Attack phase controller
    :param board: Board
    :param territory: string
    :param destination: string
    :return:
    """
    if not territory:
        return game(board)
    
    """Checking correction of territory"""
    territory = board.get_territory(territory)
    if territory.get_owner() != board.active_player():
        flash(MESSAGES['illegal-chose'], 'danger')
        return render_board(board)
    if territory.get_strength() < 2:
        flash(MESSAGES['illegal-too-little'], 'danger')
        return render_board(board)
    if territory.is_border() is False:
        flash(MESSAGES['illegal-not-neighbour'], 'danger')
        return render_board(board)
    
    """Choose destination"""
    if not destination:
        return render_board(board, chosen_territory=territory)

    """Chose canceled"""
    destination = board.get_territory(destination)
    if territory is destination:
        flash(MESSAGES['chose-cancelled'], 'info')
        return render_board(board)
    
    """Checking correction of destination"""
    if territory.get_owner() != board.active_player():
        flash(MESSAGES['illegal-chose'], 'danger')
        return render_board(board)
    if territory.get_strength() < 2:
        flash(MESSAGES['illegal-too-little'], 'danger')
        return render_board(board)
    if destination.get_owner() == board.active_player():
        flash(MESSAGES['illegal-attack-self'], 'danger')
        return render_board(board)
    if destination not in territory.get_neighbours():
        flash(MESSAGES['illegal-movement'], 'danger')
        return render_board(board)

    """Choose units"""
    if not request.args.get('units'):
        return render_board(board, chosen_territory=territory, destination_territory=destination)

    """Checking units"""
    units = int(request.args.get('units'))
    if units < 1 or units >= territory.get_strength():
        flash(MESSAGES['not-enough-units'], 'danger')
        return render_board(board)
    
    """Casting attack"""
    if board.attack(territory, destination, units):
        flash(MESSAGES['attack-success'], 'success')
        if board.check_elimination():
            pickle.dump(board, open(GAMES_PATH + str(board.get_id()) + '/board.pkl', 'wb'))
            return end_game()
    else:
        flash(MESSAGES['attack-fail'], 'danger')
    pickle.dump(board, open(GAMES_PATH + str(board.get_id()) + '/board.pkl', 'wb'))
    return render_board(board)


def fortify(board, territory, destination):
    """
    Fortification phase controller
    :param board: Board
    :param territory: string
    :param destination: string
    :return:
    """
    if not territory:
        return game(board)

    """Checking correction of territory"""
    territory = board.get_territory(territory)
    if territory.get_owner() != board.active_player():
        flash(MESSAGES['illegal-chose'], 'danger')
        return render_board(board)
    if territory.get_strength() < 2:
        flash(MESSAGES['illegal-too-little'], 'danger')
        return render_board(board)
    if len(territory.get_connected()) < 2:
        flash(MESSAGES['illegal-no-group'], 'danger')
        return render_board(board)

    """Choose destination"""
    if not destination:
        return render_board(board, chosen_territory=territory)

    """Chose canceled"""
    destination = board.get_territory(destination)
    if territory is destination:
        flash(MESSAGES['chose-cancelled'], 'info')
        return render_board(board)

    """Checking correction of destination"""
    if territory not in destination.get_connected():
        flash(MESSAGES['illegal-no-connection'], 'danger')
        return render_board(board)

    """Checking units"""
    if not request.args.get('units'):
        return render_board(board, chosen_territory=territory, destination_territory=destination)
    units = int(request.args.get('units'))
    if units < 1 or units >= territory.get_strength():
        flash(MESSAGES['not-enough-units'], 'danger')
        return render_board(board)

    """Casting fortification"""
    board.fortify(territory, destination, units)
    board.new_phase()
    pickle.dump(board, open(GAMES_PATH + str(board.get_id()) + '/board.pkl', 'wb'))
    return game(board)


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


def render_board(board, chosen_territory=None, destination_territory=None, log=None, abandon=False):
    """
    Board renderer
    Renders board for player according to phase
    :param board:
    :param chosen_territory: Territory/None
    :param destination_territory: Territory/None
    :param abandon: Bool
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
        if destination_territory:
            question_box = [destination_territory.get_title(), '', active_player.get_units()]
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
                           question_box=question_box, log=log, abandon=abandon, game_name=board.get_game_name(),
                           chosen_territory=chosen_territory, destination_territory=destination_territory)
