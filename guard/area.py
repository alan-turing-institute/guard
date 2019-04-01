"""
Define regions of the map
"""


class Area(object):
    """
    Abstract base class for areas.

    Attributes:
        all_tiles (list[tuple]): A list of all tiles within the area. Each
            element is a tuple of the form (x,y).
    """
    def __init__(self):
        self.all_tiles = []

    def in_area(self, x, y):
        """
        Determine whether a tile is within an area.

        Args:
            x (int): The x coordinate of the tile.
            y (int): The y coordinate of the tile.

        Returns:
            (bool): True if the tile at (x,y) is within the area, False
                otherwise.

        Raises:
            NotImplementedError: If this method has not been implemented by the
                class
        """
        raise NotImplementedError


class Rectangle(Area):
    """
    Rectangluar area.

    Args:
        xmin (int): The lower x bound.
        xmax (int): The upper x bound.
        ymin (int): The lower y bound.
        ymay (int): The upper y bound.
    """
    def __init__(self, xmin, xmax, ymin, ymax):
        super().__init__()

        assert xmax > xmin
        assert ymax > ymin

        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.all_tiles = [
            (x, y) for x in range(xmin, xmax) for y in range(ymin, ymax)
            ]

    def in_area(self, x, y):
        if x < self.xmax and x >= self.xmin:
            if y < self.ymax and y >= self.ymin:
                return True
        return False

    def bounds(self):
        """
        The bounds of the rectangular area.

        Returns:
            (tuple): A tuple of the area bounds in the form (xmin, xmax, ymin,
                ymax)
        """
        return self.xmin, self.xmax, self.ymin, self.ymax

    @classmethod
    def entire_map(cls, world):
        """
        Build a rectangular area covering the entire map.

        Args:
            world (World): The world object containing the map.
        """
        return cls(0, world.xdim, 0, world.ydim)
