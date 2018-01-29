from players import Player, Human, Computer


class Territory:
    """Class Territory"""
    def __init__(self, name, title, player=None, armies=0):
        """
        Class constructor
        :param name: string
        :param title: string
        :param player: Player/None
        :param armies: int
        """
        self.name = name
        self.player = player
        self.armies = armies
        self.connections = []
        self.title = title

    def make_connection(self, territory):
        """
        Makes connections
        :param territory:Territory
        :return: void
        """
        self.connections.append(territory)

    def get_name(self):
        """
        Name (shortened) getter
        :return name: string
        """
        return self.name

    def get_title(self):
        """
        Title (full-name) getter
        :return title: string
        """
        return self.title

    def get_owner(self):
        """
        Owner getter
        :return owner: Player/None
        """
        if self.player:
            return self.player
        else:
            return None

    def repr_owner(self):
        """
        Writes out owner's full-id
        :return owner: string
        """
        if self.player:
            return 'player' + str(self.player.get_id())
        else:
            return 'noplayer'

    def get_neighbours(self):
        """
        Returns connected territories
        :return connections: list
        """
        return self.connections

    def set_owner(self, newowner, armies):
        """
        Sets new owner of the territory
        :param newowner: Player
        :param armies: int
        :return: void
        """
        self.player = newowner
        self.armies = armies

    def get_strength(self):
        """
        Armies getter
        :return armies: int
        """
        return self.armies

    def reinforce(self, diff):
        """
        Increases armies
        :param diff: int
        :return: void
        """
        self.armies += diff

    def weaken(self, diff):
        """
        Decreases armies
        :param diff: int
        :return: void
        """
        self.armies -= diff

    def get_connected(self, connected=None):
        """
        Recursively returns group of connected territories belonging to one owner
        :param connected: set/None
        :return connected: set
        """
        if connected is None:
            connected=set()
        connected.add(self)
        for ter in self.connections:
            if ter.get_owner() == self.player and ter not in connected:
                connected = connected | ter.get_connected(connected)
        return connected

    def is_border(self):
        """
        If the territory is a border territory
        :return: bool
        """
        for ter in self.connections:
            if ter.get_owner() != self.player:
                return True
        return False


class Continent:
    """Class Continent"""
    def __init__(self, name, territorylist, units):
        """
        Class constructor
        :param name: string
        :param territorylist: list
        :param units: int
        """
        self.name = name
        self.territories = territorylist
        self.units = units

    def get_name(self):
        """
        Name getter
        :return: string
        """
        return self.name

    def get_owner(self):
        """
        Owner getter
        :return: Player/None
        """
        owner = self.territories[0].get_owner()
        for ter in self.territories:
            if ter.get_owner() != owner:
                owner = None
        return owner

    def repr_owner(self):
        """
        Writes out owner's full-id
        :return: string
        """
        owner = self.territories[0].repr_owner()
        for ter in self.territories:
            if ter.repr_owner() != owner:
                owner = 'noplayer'
        return owner

    def get_units(self):
        """
        Units getter
        :return: int
        """
        return self.units


class Board:
    """Class Board"""
    def __init__(self, territorylist, continentlist, playerslist, map_name, unitchart):
        """
        Class constructor
        :param territorylist: dict
        :param continentlist: dict
        :param playerslist: dict
        :param map_name: string
        :param unitchart: dict
        """
        self.map_name = map_name
        self.territories = territorylist
        self.continents = continentlist
        self.players = {}
        self.turn = 0
        self.phase = 1
        units = unitchart[len(playerslist)]
        for key, player in playerslist.items():
            if player[0] == 'self-player':
                self.players['player'+str(key)] = Human(key, player[1], units)
            elif player[0] == 'ai-player':
                self.players['player'+str(key)] = Computer(key, player[1], units)
        self.starting_units = len(playerslist) * units

    def get_map_name(self):
        """
        Map name getter
        :return: string
        """
        return self.map_name

    def get_territories(self):
        """
        Territories getter
        :return: list
        """
        terlist = []
        for key, ter in self.territories.items():
            terlist.append([ter.get_name(), ter.repr_owner(), ter.get_strength()])
        return terlist

    def get_continents(self):
        """
        Continents getter
        :return: list
        """
        conlist = []
        for key, con in self.continents.items():
            conlist.append([con.get_name(), con.repr_owner(), con.get_units()])
        return conlist
    
    def get_phase(self):
        """
        Returns phase number
        :return: int
        """
        if self.turn == 0:
            if self.phase <= len(self.territories):
                return 'initial'
            else:
                return 'initial-reinforce'
        else:
            if self.phase == 0:
                return 'deployment'
            elif self.phase == 1:
                return 'attack'
            elif self.phase == 2:
                return 'fortify'
            else:
                return 'wrong phase!'

    def get_round(self):
        """
        Returns full number of the round
        :return: int
        """
        return (self.turn + 2) // 3

    def active_player(self):
        """
        Returns active player
        :return: Player
        """
        if self.turn == 0:
            id = self.phase % len(self.players)
        else:
            id = self.turn % len(self.players)
        if id == 0:
            id = len(self.players)
        return self.players['player' + str(id)]

    def new_turn(self):
        """
        New turn
        Resets phase number
        Reinforces active player
        :return: void
        """
        self.phase = 0
        self.turn += 1
        self.active_player().increase_units(self.count_reinforcements())

    def new_phase(self):
        """
        New phase
        Calls new_turn() if needed
        :return: void
        """
        self.phase += 1
        if self.turn == 0:
            if self.units_left() <= 0:
                self.new_turn()
        else:
            if self.phase > 2:
                self.new_turn()

    def player_territories(self, player):
        """
        Returns territories of a given player
        :param player: Player
        :return: list
        """
        terlist = [ter for key, ter in self.territories.items() if ter.get_owner() == player]
        return terlist

    def set_owner(self, territory, new_owner, armies):
        """
        Sets new owner of a territory
        :param territory: string
        :param new_owner: Player
        :param armies: int
        :return: void
        """
        territory = self.territories[territory]
        old_owner = territory.get_owner()
        if old_owner:
            old_owner.abandon_territory(territory)
        new_owner.possess_territory(territory)
        territory.set_owner(new_owner, armies)

    def units_left(self):
        """
        Returns numbers of unit left to all players
        :return: int
        """
        units = 0
        for key, player in self.players.items():
            units += player.get_units()
        return units

    def count_reinforcements(self):
        """
        Counts reinforcements of active player
        :return: int
        """
        player = self.active_player()
        reinforcments = len(self.player_territories(player)) // 3
        if reinforcments < 3:
            reinforcments = 3
        for key, con in self.continents.items():
            if con.get_owner() == player:
                reinforcments += con.get_units()
        return reinforcments


def set_connections(*connections):
    """
    Estabilishes connections between territories
    :param connections: tuple
    :return: void
    """
    for pair in connections:
        pair[0].make_connection(pair[1])
        pair[1].make_connection(pair[0])


