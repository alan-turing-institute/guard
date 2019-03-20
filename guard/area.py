# Define regions of the map


class Area(object):
    def __init__(self):
        self.all_tiles = []

    def in_area(self, x, y):
        raise NotImplementedError


class Rectangle(Area):
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
        return self.xmin, self.xmax, self.ymin, self.ymax

    @classmethod
    def entire_map(cls, world):
        return cls(0, world.xdim, 0, world.ydim)
