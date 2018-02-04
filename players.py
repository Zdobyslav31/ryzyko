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
        self.log = {'player': (self.name, self.id), 'deploy': {}, 'attack': [], 'fortify': ()}

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

    def get_territories(self):
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
        self.log = {'player': (self.name, self.id), 'deploy': {}, 'attack': [], 'fortify': ()}
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
        territory = self.territory_to_reinforce(self.get_territories())
        territory.reinforce(1)
        self.decrease_units(1)
        if board.get_round() != 0:
            if territory.get_title() in self.log['deploy']:
                self.log['deploy'][territory.get_title()] += 1
            else:
                self.log['deploy'][territory.get_title()] = 1

    def deploy(self, board):
        while self.units:
            self.deploy_once(board)

    def cast_attacks(self, board):
        raise NotImplementedError

    def fortify(self, board):
        possible_territories_from = [ter for ter in self.get_territories()
                                     if len(ter.get_connected()) > 1 and ter.get_strength() > 1]
        if len(possible_territories_from) > 0:
            territory_from = self.territory_from_fortify(possible_territories_from)
            if territory_from:
                territory_to = self.territory_to_reinforce([ter for ter in territory_from.get_connected()
                                                            if ter is not territory_from])
                units = self.fortify_units(territory_from, territory_to)
                if units:
                    board.fortify(territory_from, territory_to, units)
                    self.log['fortify'] = (territory_from.get_title(), territory_to.get_title(), units)

    def territory_to_possess(self, board):
        raise NotImplementedError

    def territory_to_reinforce(self, territories):
        raise NotImplementedError

    def territory_from_fortify(self, territories):
        raise NotImplementedError

    def fortify_units(self, territory_from, territory_to):
        raise NotImplementedError


class RandomAI(Computer):
    """Class RandomAI - implementation of Computer Player
    Makes every mov random"""
    def territory_to_possess(self, board):
        territories = [ter for ter in board.get_territories() if ter.get_owner() is None]
        return self.random_territory(territories)

    def territory_to_reinforce(self, territories):
        return self.random_territory(territories)

    def cast_attacks(self, board):
        territories = [ter for ter in self.get_territories() if ter.is_border() and ter.get_strength() > 1]
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

    def territory_from_fortify(self, territories):
        return self.random_territory(territories)

    def fortify_units(self, territory_from, territory_to):
        return random.randrange(0, territory_from.get_strength())

    def random_territory(self, territories):
        ter_id = random.randrange(0, len(territories))
        return territories[ter_id]


class EasyAI(Computer):
    """Class RandomAI - implementation of Computer Player
    Makes every mov random"""
    def territory_to_possess(self, board):
        """
        Wybiera terytorium o największej liczbie sojuszniczych sąsiadów
        :param board: Board
        :return: Territory
        """
        territories = sorted(
            [ter for ter in board.get_territories() if ter.get_owner() is None],
            key=lambda territory: len([ter for ter in territory.get_neighbours()if ter.get_owner() == self]),
            reverse=True
        )
        return territories[0]

    def territory_to_reinforce(self, territories, reverse=False):
        """
        Wybiera  terytorium o największej dysproporcji sił na niekorzyść w stosunku do najsilniejszego wrogiego sąsiada
        :return: Territory
        """
        territories = sorted(
            [ter for ter in territories if ter.is_border()],
            key=lambda territory: (
                territory.get_strength() - max([ter.get_strength() for ter in territory.get_enemies()]),
                sum([ter.get_strength() for ter in territory.get_enemies()])
            ),
            reverse=reverse
        )
        return territories[0]

    def cast_attacks(self, board):
        """
        Atakuje tak długo, jak długo ma przewagę nad najsilniejszym z wrogich sąsiadów.
        Wybiera najsłabsze terytorium wroga do atakowania
        Ilość jednostek do ataku:
            if jest 1 wrogie terytorium: max
            elif mamy przewagę większą niż 2: atakujemy z przewagą 2
            else: max
        :param board: Board
        :return: void
        """
        territories = [ter for ter in self.get_territories() if ter.is_border() and ter.get_strength() > 1]
        for ter in territories:
            while ter.is_border() and ter.get_strength() > max([enemy.get_strength() for enemy in ter.get_enemies()]):
                enemies = sorted(
                    ter.get_enemies(),
                    key=lambda enemy: enemy.get_strength()
                )
                target = enemies[0]
                if len(enemies) == 1:
                    units = ter.get_strength() - 1
                elif ter.get_strength() - target.get_strength() > 2:
                    units = target.get_strength() + 2
                else:
                    units = ter.get_strength() - 1
                success = board.attack(ter, target, units)
                if success and target.get_strength() > 1:
                    territories.append(target)
                self.log['attack'].append((ter.get_title(), target.get_title(), units, success))

    def territory_from_fortify(self, territories):
        territories_from = sorted(
            [ter for ter in self.get_territories() if ter.is_border() is False and ter.get_strength() > 1],
            key=lambda ter: ter.get_strength(),
            reverse=True
        )
        if len(territories_from) > 0:
            return territories_from[0]
        else:
            return self.territory_to_reinforce(territories, reverse=True)

    def fortify_units(self, territory_from, territory_to):
        if len(territory_from.get_enemies()) == 0:
            return territory_from.get_strength() - 1
        else:
            diff_from = territory_from.get_strength() - max([enemy.get_strength() for enemy in territory_from.get_enemies()])
            diff_to = territory_to.get_strength() - max([enemy.get_strength() for enemy in territory_to.get_enemies()])
            return (diff_from - diff_to) // 2

