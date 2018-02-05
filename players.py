import random

class Player:
    """Abstract class Player"""
    def __init__(self, id_on_board, name, units):
        """
        Class constructor
        :param id_on_board: int
        :param name: string
        :param units: int
        """
        self.id_on_board = id_on_board
        self.name = name
        self.units = units
        self.territory_list = []
        self.eliminated = False
        self.log = {'player': (self.name, self.id_on_board), 'deploy': {}, 'attack': [], 'fortify': ()}

    def __repr__(self):
        return 'Player %s, id: %s type: %s' % (self.name, self.id_on_board, type(self))

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
        return self.id_on_board

    def repr_id(self):
        """
        Writes out full-id_on_board of the player
        :return: string
        """
        return 'player' + str(self.id_on_board)

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
        self.log = {'player': (self.name, self.id_on_board), 'deploy': {}, 'attack': [], 'fortify': ()}
        return log

    def get_log(self):
        return self.log



class Human(Player):
    """Class Human Player"""
    def __init__(self, id_on_board, name, units, player_id=None):
        super().__init__(id_on_board, name, units)
        self.player_id = player_id

    def get_player_id(self):
        return self.player_id


class Computer(Player):
    """Computer Player interface"""
    def initial(self, board):
        """
        Occupies single no-player territory
        :param board: Board
        :return: void
        """
        territory = self.territory_to_possess([ter for ter in board.get_territories() if ter.get_owner() is None])
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
        territories = [ter for ter in self.get_territories() if ter.is_border() and ter.get_strength() > 1]
        for ter in territories:
            while ter.is_border() and ter.get_strength() > 1 and self.attack_condition(ter):
                enemies = ter.get_enemies()
                target = self.select_target(enemies)
                units = self.attack_units(ter, target)
                if units > 0 and units < ter.get_strength():
                    success = board.attack(ter, target, units)
                    if success and target.get_strength() > 1:
                        territories.append(target)
                    self.log['attack'].append((ter.get_title(), target.get_title(), units, success))

    def fortify(self, board):
        possible_territories_from = [ter for ter in self.get_territories()
                                     if len(ter.get_connected()) > 1 and ter.get_strength() > 1]
        if len(possible_territories_from) > 0:
            territory_from = self.territory_from_fortify(possible_territories_from)
            if territory_from:
                try:
                    territory_to = self.territory_to_reinforce([ter for ter in territory_from.get_connected()
                                                                if ter is not territory_from])
                    units = self.fortify_units(territory_from, territory_to)
                    if units > 0:
                        board.fortify(territory_from, territory_to, units)
                        self.log['fortify'] = (territory_from.get_title(), territory_to.get_title(), units)
                except IndexError:
                    print('error while trying to fortify from %s in group consisted of %s' % (territory_from, [ter for ter in territory_from.get_connected() if ter is not territory_from]))

    def territory_to_possess(self, board):
        raise NotImplementedError

    def territory_to_reinforce(self, territories):
        raise NotImplementedError
    
    def attack_condition(self, territory):
        raise NotImplementedError
        
    def select_target(self, enemies):
        raise NotImplementedError
    
    def attack_units(self, attacker, target):
        raise NotImplementedError

    def territory_from_fortify(self, territories):
        raise NotImplementedError

    def fortify_units(self, territory_from, territory_to):
        raise NotImplementedError


class RandomAI(Computer):
    """Class RandomAI - implementation of Computer Player
    Makes every move random"""
    def territory_to_possess(self, territories):
        return self.random_territory(territories)

    def territory_to_reinforce(self, territories):
        return self.random_territory(territories)
    
    def attack_condition(self, territory):
        return bool(random.getrandbits(1))
        
    def select_target(self, enemies):
        return self.random_territory(enemies)
    
    def attack_units(self, attacker, target):
        return random.randrange(1, attacker.get_strength())

    def territory_from_fortify(self, territories):
        return self.random_territory(territories)

    def fortify_units(self, territory_from, territory_to):
        return random.randrange(0, territory_from.get_strength())

    def random_territory(self, territories):
        ter_id = random.randrange(0, len(territories))
        return territories[ter_id]


class EasyAI(Computer):
    """Class EasyAI - implementation of Computer Player
    Implements easy algorithms for AI"""
    def territory_to_possess(self, territories):
        """
        Wybiera terytorium o największej liczbie sojuszniczych sąsiadów
        :param board: Board
        :return: Territory
        """
        territories = sorted(
            territories,
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
    
    def attack_condition(self, territory):
        return bool(territory.get_strength() > max([enemy.get_strength() for enemy in territory.get_enemies()]))
        
    def select_target(self, enemies):
        enemies = sorted(enemies, key=lambda enemy: enemy.get_strength())
        return enemies[0]
    
    def attack_units(self, attacker, target):
        if len(attacker.get_enemies()) == 1:
            return attacker.get_strength() - 1
        elif attacker.get_strength() - target.get_strength() > 2:
            return max(target.get_strength() + 2, (attacker.get_strength() - target.get_strength()) // 2)
        else:
            return attacker.get_strength() - 1

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
            diff_from = territory_from.get_strength() - max([enemy.get_strength()
                                                             for enemy in territory_from.get_enemies()])
            diff_to = territory_to.get_strength() - max([enemy.get_strength() for enemy in territory_to.get_enemies()])
            return (diff_from - diff_to) // 2
