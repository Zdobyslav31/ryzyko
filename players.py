class Player:
    def __init__(self, id, name, units):
        self.id = id
        self.name = name
        self.units = units
        self.territory_list = []

    def get_units(self):
        return self.units

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id

    def possess_territory(self, territory):
        self.territory_list.append(territory)

    def abandon_territory(self, territory):
        self.territory_list.remove(territory)

    def increase_units(self, number):
        self.units += number

    def decrease_units(self, number):
        self.units -= number



class Human(Player):
    pass


class Computer(Player):
    pass
