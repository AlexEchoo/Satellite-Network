from Position import *


class Gateway:
    uid = 0

    def __init__(self, lon, lat, height=USER_HEIGHT):
        assert (lon >= -1 * pi)
        assert (lon <= pi)
        assert (lat >= -0.5 * pi)
        assert (lat <= pi / 2)
        assert (height >= 0)
        self.__class__.uid += 1
        self.id = self.uid
        self.height = height
        self.w0_pos = Sphere_Position()
        self.w0_pos.lon = lon
        self.w0_pos.lat = lat
        self.w0_pos.radius = EARTH_RADIUS + height
        self.we_pos = Sphere_Position()
        self.we_pos = self.w0_pos
        self.sat_covered = set()
