from enum import Enum


class Color(Enum):
    NONE = 0
    GREEN = 1
    RED = 2
    BLUE = 3


class ZoneType(Enum):
    NORMAL = 0
    BLOCKED = 1
    RESTRICTED = 2
    PRIORITY = 3


class Map():
    class Zone():
        class Connection():
            def __init__(self, orig: "Map.Zone", dest: "Map.Zone",
                         max_capacity: int = -1):
                self.orig = orig
                self.dest = dest
                self.capacity = max_capacity

            def show(self):
                return f"{self.orig.name} <=> {self.dest.name}"

        def __init__(self, name: str, coords: tuple[str, str] | list[str],
                     color: str = "NONE"):
            self.name: str = name
            self.coords: tuple[int, int] | list[int] = [int(x) for x in coords]
            self.type = ZoneType.NORMAL
            self.color = [
                c for c in Color if str(c) == "Color." + color.upper()][0]
            self._connections: list[Map.Zone.Connection] = []

        def set_connection(self, dest: "Map.Zone"):
            self._connections.append(Map.Zone.Connection(self, dest))

        def get_connections(self):
            return (self._connections)

        def show(self, mode: int = 1):
            if mode == 0:
                return f"""{self.name}:
    Coordinates: {self.coords}
    Type: {self.type}
    Color: {self.color}
    Connections: {[c.show() for c in self._connections]}"""
            else:
                pass

    def __init__(self, pconfig: str):
        self._zones: list[Map.Zone] = []
        self.dimensions: list[int] = [0, 0]
        for c in pconfig:
            if ('hub' in c[0]):
                self._zones.append(Map.Zone(c[1].split(" ")[0],
                                            c[1].split(" ")[1:3],
                                            color=[co for co in
                                                   Color.__members__
                                                   if co in c[1].upper()][0]))
            if (c[0].lower() == "connection"):
                origen: str = c[1].split("-")[0]
                destination: str = c[1].split("-")[1]
                for z in self._zones:
                    if z.name.lower() == origen.lower():
                        for zz in self._zones:
                            if zz.name.lower() == destination.lower():
                                z.set_connection(zz)
                                zz.set_connection(z)

    def get_zones(self):
        return self._zones


def parse_config(file: str):
    result: list[list[str] | list[list[list[str]]]] = []
    splat: list[str] = file.split("\n")
    splat = [s for s in splat if not s.startswith("#")]
    result.extend(
        [[s[0], s[1]] for s in
         [ss.split(": ") for ss in splat if len(ss.split(": ")) == 2]])

    return (result)


if __name__ == "__main__":
    with open("maps/easy/01_linear_path.txt") as file:
        pconfig = parse_config(file.read())

    m: Map = Map(pconfig)
    [print(z.show(0)) for z in m.get_zones()]
