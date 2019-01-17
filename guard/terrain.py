class Terrain(object):
    def __init__(self, name, polity_forming):
        self.name = name
        assert isinstance(polity_forming, bool)
        self.polity_forming = polity_forming

    def __str__(self):
        return self.name

agriculture = Terrain('agriculture', True)
steppe = Terrain('steppe', True)
sea = Terrain('sea', False)
desert = Terrain('desert', False)
