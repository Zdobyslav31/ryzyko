import random

class Player:
    """Abstract class Player"""
    def __init__(self, id, name, units):
        """
        Class constructor
        :param id: int
        :param name: string
        :param units: int
        """
        self.id = id
        self.name = name
        self.units = units
        self.territory_list = []
        self.eliminated = False
        self.log = {'player': self.name, 'deploy': {}, 'attack': [], 'fortify': ()}

    def get_units(self):
        """
        Units getter
        :return: int
        """
        return self.units

    def get_name(self):
        """
        Name getter
        :return: string
        """
        return self.name

    def get_id(self):
        """
        Id getter
        :return: int
        """
        return self.id

    def repr_id(self):
        """
        Writes out full-id of the player
        :return: string
        """
        return 'player' + str(self.id)

    def get_terriitories(self):
        """
        Territories getter
        :return: list
        """
        return self.territory_list

    def possess_territory(self, territory):
        """
        Appends territory to territory_list
        :param territory: Territory
        :return: void
        """
        self.territory_list.append(territory)

    def abandon_territory(self, territory):
        """
        Removes  territory from territory_list
        :param territory: Territory
        :return: void
        """
        self.territory_list.remove(territory)

    def increase_units(self, number):
        """
        Increases units number
        :param number: int
        :return: void
        """
        self.units += number

    def decrease_units(self, number):
        """
        Decreases units number
        :param number: int
        :return: void
        """
        self.units -= number

    def check_for_elimination(self):
        """
        Checks if player is eliminated and if so, changes value and returns
        :return: bool
        """
        if len(self.territory_list) == 0:
            self.eliminated = True
        return self.eliminated

    def is_eliminated(self):
        """
        Checks if player is eliminated but doesn't change the value
        :return: bool
        """
        return self.eliminated

    def dump_log(self):
        log = self.log
        self.log = {'player': self.name, 'deploy': {}, 'attack': [], 'fortify': ()}
        return log

    def get_log(self):
        return self.log



class Human(Player):
    """Class Human Player"""
    pass


class Computer(Player):
    """Computer Player interface"""
    def initial(self, board):
        """
        Occupies single no-player territory
        :param board: Board
        :return: void
        """
        territory = self.territory_to_possess(board)
        board.set_owner(territory.get_name(), self, 1)

    def deploy_once(self, board):
        territory = self.territory_to_reinforce(board)
        territory.reinforce(1)
        self.decrease_units(1)
        if board.get_round() != 0:
            if territory.get_name() in self.log['deploy']:
                self.log['deploy'][territory.get_name()] += 1
            else:
                self.log['deploy'][territory.get_name()] = 1

    def deploy(self, board):
        while self.units:
            self.deploy_once(board)

    def cast_attacks(self, board):
        raise NotImplementedError

    def fortify(self, board):
        raise NotImplementedError

    def territory_to_possess(self, board):
        raise NotImplementedError

    def territory_to_reinforce(self, board):
        raise NotImplementedError


class RandomAI(Computer):
    """Class RandomAI - implementation of Computer Player
    Makes every mov random"""
    def territory_to_possess(self, board):
        territories = [ter for ter in board.get_territories() if ter.get_owner() is None]
        return self.random_territory(territories)

    def territory_to_reinforce(self, board):
        territories = self.get_terriitories()
        ter_id = random.randrange(0, len(territories))
        return self.random_territory(territories)

    def cast_attacks(self, board):
        territories = [ter for ter in self.get_terriitories() if ter.is_border() and ter.get_strength() > 1]
        for ter in territories:
            try:
                if random.getrandbits(1) and ter.is_border():
                    target = ter.get_enemies()[random.randrange(0, len(ter.get_enemies()))]
                    units = random.randrange(1, ter.get_strength())
                    success = board.attack(ter, target, units)
                    if success and target.get_strength() > 1:
                        territories.append(target)
                    self.log['attack'].append((ter.get_title(), target.get_title(), units, success))
            except ValueError:
                print('Error occured while seeking target for %s having %d enemies' % (ter.get_title(), len(ter.get_enemies())))
                print('Function is_border() returned %s for this element' % str(ter.is_border()))

    def fortify(self, board):
        if len(self.territory_list) > 1 and len([ter for ter in self.territory_list if ter.get_strength() > 1]) > 0:
            territory_from = self.random_territory([ter for ter in self.territory_list if ter.get_strength() > 1])
            group = [ter for ter in territory_from.get_connected() if ter != territory_from]
            if len(group) > 0:
                territory_to = self.random_territory(group)
                units = random.randrange(1, territory_from.get_strength())
                board.fortify(territory_from, territory_to, units)
                self.log['fortify'] = (territory_from.get_title(), territory_to.get_title(), units)

    def random_territory(self, territories):
        ter_id = random.randrange(0, len(territories))
        return territories[ter_id]




