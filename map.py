class Territory:
    def __init__(self, name, title, player=None, armies=0):
        self.name = name
        self.player = player
        self.armies = armies
        self.connections = []
        self.title = title

    def make_connection(self, territory):
        self.connections.append(territory)

    def get_name(self):
        return self.name

    def get_title(self):
        return self.title

    def get_owner(self):
        if self.player:
            return self.player
        else:
            return 'noplayer'

    def get_neighbours(self):
        return self.connections

    def set_owner(self, newowner, armies):
        self.player = newowner
        self.armies = armies

    def get_strength(self):
        return self.armies

    def reinforce(self, diff):
        self.armies += diff

    def weaken(self, diff):
        self.armies -= diff

class Continent:
    def __init__(self, name, territorylist, units):
        self.name = name
        self.territories = territorylist
        self.units = units

    def get_name(self):
        return self.name

    def get_owner(self):
        owner = self.territories[0].get_owner()
        for ter in self.territories:
            if ter.get_owner() != owner:
                owner = 'noplayer'
        return owner

    def get_units(self):
        return self.units

class Board:
    def __init__(self, territorylist, continentlist, playerslist, map_name):
        self.map_name = map_name
        self.territories = territorylist
        self.continents = continentlist
        self.players = playerslist
        self.status = 1

    def get_map_name(self):
        return self.map_name

    def get_territories(self):
        terlist = []
        for key, ter in self.territories.items():
            terlist.append([ter.get_name(), ter.get_owner(), ter.get_strength()])
        return terlist

    def get_continents(self):
        conlist = []
        for key, con in self.continents.items():
            conlist.append([con.get_name(), con.get_owner(), con.get_units()])
        return conlist

    def turn(self):
        if self.status <= len(self.territories):
            result = ['initial', self.status % len(self.players), self.status]
        else:
            turn = self.status - len(self.territories)
            if turn % 3 == 0:
                result = ['deployment', (turn // 3) + 1]
            elif turn % 3 == 1:
                result = ['attack', (turn // 3) + 1]
            else:
                result = ['fortify', (turn // 3) + 1]
        return result

    def active_player(self):
        if self.status <= len(self.territories):
            result = self.status % len(self.players)
        else:
            turn = self.status - len(self.territories)
            result = ((turn // 3) + 1) % len(self.players)
        if result == 0:
            result = len(self.players)
        return result

    def new_turn(self):
        self.status += 1

    def player_territories(self, player):
        terlist = []
        for key, ter in self.territories.items():
            if ter.get_owner() == player:
                terlist.append(ter.get_name())
        return terlist


def set_connections(*connections):
    for pair in connections:
        pair[0].make_connection(pair[1])
        pair[1].make_connection(pair[0])