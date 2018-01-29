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



class Human(Player):
    """Class Human Player"""
    pass


class Computer(Player):
    """Class Computer Player"""
    pass
