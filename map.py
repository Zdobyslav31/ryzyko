from players import Player, Human, Computer

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

    def repr_owner(self):
        if self.player:
            return 'player' + str(self.player.get_id())
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

    def get_connected(self, connected=None):
        if connected is None:
            connected=set()
        connected.add(self)
        for ter in self.connections:
            if ter.get_owner() == self.player and ter not in connected:
                connected = connected | ter.get_connected(connected)
        return connected

    def is_border(self):
        for ter in self.connections:
            if ter.get_owner() != self.player:
                return True
        return False





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

    def repr_owner(self):
        owner = self.territories[0].repr_owner()
        for ter in self.territories:
            if ter.repr_owner() != owner:
                owner = 'noplayer'
        return owner

    def get_units(self):
        return self.units


class Board:
    def __init__(self, territorylist, continentlist, playerslist, map_name, unitchart):
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
        return self.map_name

    def get_territories(self):
        terlist = []
        for key, ter in self.territories.items():
            terlist.append([ter.get_name(), ter.repr_owner(), ter.get_strength()])
        return terlist

    def get_continents(self):
        conlist = []
        for key, con in self.continents.items():
            conlist.append([con.get_name(), con.repr_owner(), con.get_units()])
        return conlist
    
    def get_phase(self):
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
        return (self.turn + 2) // 3

    def active_player(self):
        if self.turn == 0:
            id = self.phase % len(self.players)
        else:
            id = self.turn % len(self.players)
        if id == 0:
            id = len(self.players)
        return self.players['player' + str(id)]

    def new_turn(self):
        self.phase = 0
        self.turn += 1
        self.active_player().increase_units(self.count_reinforcements())

    def new_phase(self):
        self.phase += 1
        if self.turn == 0:
            if self.units_left() <= 0:
                self.new_turn()
        else:
            if self.phase > 2:
                self.new_turn()

    def player_territories(self, player):
        terlist = [ter for key, ter in self.territories.items() if ter.get_owner() == player]
        return terlist

    def set_owner(self, territory, new_owner, armies):
        territory = self.territories[territory]
        old_owner = territory.get_owner()
        if old_owner != 'noplayer':
            old_owner.abandon_territory(territory)
        new_owner.possess_territory(territory)
        territory.set_owner(new_owner, armies)

    def units_left(self):
        units = 0
        for key, player in self.players.items():
            units += player.get_units()
        return units

    def count_reinforcements(self):
        player = self.active_player()
        reinforcments = len(self.player_territories(player)) // 3
        if reinforcments < 3:
            reinforcments = 3
        for key, con in self.continents.items():
            if con.get_owner() == player:
                reinforcments += con.get_units()
        return reinforcments


def set_connections(*connections):
    for pair in connections:
        pair[0].make_connection(pair[1])
        pair[1].make_connection(pair[0])


