"""
Terrain class and terrain types defintion
"""


class Terrain(object):
    """
    Terrain class.

    Args:
        name (str): A label describing the terrain type.
        polity_formaing (bool): True if communities with this terrain may form
            multi-community polities, False otherwise.

    Attributes:
        name (str): A label describing the terrain type.
        polity_formaing (bool): True if communities with this terrain may form
            multi-community polities, False otherwise.
    """
    def __init__(self, name, polity_forming):
        self.name = name
        assert isinstance(polity_forming, bool)
        self.polity_forming = polity_forming

    def __str__(self):
        return self.name


"""
Agricultural terrain
"""
agriculture = Terrain('agriculture', True)
"""
Steppe terrain, which begin the simulation with all military technologies
"""
steppe = Terrain('steppe', True)
"""
Sea terrain
"""
sea = Terrain('sea', False)
"""
Desert terrain
"""
desert = Terrain('desert', False)
