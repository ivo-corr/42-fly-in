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

        def __init__(self, name: str, coords: tuple[str, str] | list[str],
                     color: str = "NONE"):
            self.name: str = name
            self.coords: tuple[int, int] | list[int] = [int(x) for x in coords]
            self.type = ZoneType.NORMAL
            self.color = [
                c for c in Color if str(c) == "Color." + color.upper()][0]
            self._connections: list[Map.Zone.Connection] = []

        def set_connection(self, dest: "Map.Zone"):
            self._connections.append(Map.Zone.Connection(self, []))

        def get_connections(self):
            pass

    def __init__(self, pconfig: str):
        self._zones: list[Map.Zone] = []
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

    def get_zones(self):
        return self._zones


def parse_config(file: str):
    result: list[list[str] | list[list[list[str]]]] = []
    splat: list[str] = file.split("\n")
    splat = [s for s in splat if not s.startswith("#")]
    result.extend(
        [[s[0], s[1]] for s in
         [ss.split(": ") for ss in splat if len(ss.split(": ")) == 2]])
    # for r in result:
    #     r[1] = r[1].split(" ", 1)
    #     if len(r) >= 2 and "=" in r[1]:
    #         result[result.index(r)] = [
    #             r[1].split("[")[0],
    #             [x[:-1] if x[-1] == ']' else x for x in
    #              r[1].split("[")[1].split("=")]]
    return (result)


if __name__ == "__main__":
    with open("maps/easy/01_linear_path.txt") as file:
        pconfig = parse_config(file.read())

    m: Map = Map(pconfig)
    [print(z.name, z.coords, z.color, z.get_connections()) for z in m.get_zones()]
