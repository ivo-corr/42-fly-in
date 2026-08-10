from enum import Enum, auto
import graphics
import os


class Metadata(str, Enum):
    ZONE = "zone"
    COLOR = "color"
    MAX_LINK_CAPACITY = "max_link_capacity"
    MAX_DRONES = "max_drones"


class Color(Enum):
    NONE = auto()
    GREEN = auto()
    RED = auto()
    BLUE = auto()
    ORANGE = auto()
    YELLOW = auto()
    CYAN = auto()
    PURPLE = auto()
    BROWN = auto()
    LIME = auto()
    MAGENTA = auto()
    GOLD = auto()


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
                     color: str = "NONE", drones: int = 0):
            self.name: str = name
            self.coords: tuple[int, int] | list[int] = [int(x) for x in coords]
            self.type = ZoneType.NORMAL
            self.color = [
                c for c in Color if str(c) == "Color." + color.upper()][0]
            self._connections: list[Map.Zone.Connection] = []
            self.drones: list[str] = []
            # breakpoint()
            for dn in range(drones):
                self.drones.append("D"+str(dn))

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
        self.drones = 0
        delta: int = 0
        '''
        delta denotes the y-axis offset caused by the weird negative index
        notation that was chosen for the map config files
        '''
        for c in pconfig:
            meta: list[list[str]] = [
                [md.lower()] for md in Metadata.__members__ if
                md.lower() in c[1]]
            if ("nb_drones" in c[0]):
                self.drones = int(c[1])
            if ('hub' in c[0]):
                if int(c[1].split(" ")[1:3][1]) < 0:
                    absolute: int = abs(int(c[1].split(" ")[1:3][1]))
                    if (absolute > delta):
                        for z in self._zones:
                            z.coords = [z.coords[0], z.coords[1] + absolute]
                    self._zones.append(Map.Zone(name := c[1].split(" ")[0],
                                                tmp := [
                                                    c[1].split(" ")[1], '0' if
                                                    absolute > delta else
                                                    str(delta-absolute)],
                                                color=[co for co in
                                                Color.__members__
                                                if co in c[1].upper()][0],
                                                drones=self.drones if name ==
                                                "start" else 0))
                    delta = absolute if absolute > delta else delta
                else:
                    if (delta > 0):
                        # breakpoint()
                        pass
                    tmp = c[1].split(" ")[1:3]
                    tmp[1] = str(int(tmp[1]) + delta)
                    self._zones.append(Map.Zone(name := c[1].split(" ")[0],
                                                tmp,
                                                color=[co for co in
                                                Color.__members__
                                                if co in c[1].upper()][0],
                                                drones=self.drones if name ==
                                                "start" else 0))
                if (int(tmp[0]) > self.dimensions[0]):
                    self.dimensions[0] = int(tmp[0])
                if (int(tmp[1]) > self.dimensions[1]):
                    self.dimensions[1] = int(tmp[1])
            if (c[0].lower() == "connection"):
                origen: str = c[1].split("-")[0]
                destination: str = c[1].split("-")[1]
                for z in self._zones:
                    if z.name.lower() == origen.lower():
                        for zz in self._zones:
                            if zz.name.lower() == destination.lower():
                                z.set_connection(zz)
                                zz.set_connection(z)
        for z in self._zones:
            if (int(z.coords[0]) > self.dimensions[0]):
                self.dimensions[0] = int(z.coords[0])
            if (int(z.coords[1]) > self.dimensions[1]):
                self.dimensions[1] = int(z.coords[1])

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


def select_map() -> str:
    select: str = ""
    print("\x1b[42m")
    print("Pick a map\x1b[0m")
    directory = 'maps/'
    directories = [d for d in os.listdir(directory) if
                   os.path.isdir(os.path.join(directory, d))]
    files = [f for f in os.listdir(directory) if
             os.path.isfile(os.path.join(directory, f))]
    for d in directories:
        dfiles = [f for f in os.listdir(directory+"/"+d) if
                  os.path.isfile(os.path.join(directory+"/"+d, f))]
        print("\t\x1b[34m" + d + "/\x1b[0m")
        for df in dfiles:
            print("\t\t\x1b[32m"+df+"\x1b[0m" if df.endswith(".txt") else
                  "\t\x1b[31m"+df+" (not a text file)\x1b[0m")
    for f in files:
        print("\t\x1b[32m"+f+"\x1b[0m" if f.endswith(".txt") else
              "\t\x1b[31m"+f+" (not a text file)\x1b[0m")
    # print(directories)
    # print(files)
    input("## ")
    with open('maps/test_map.txt') as file:
        pconfig: str = parse_config(file.read())
    return pconfig


if __name__ == "__main__":
    CLEAR_SCREEN: str = '\x1b[2J\x1b[H'
    TITLE: str = '''
███████╗██╗  ██╗   ██╗       ██╗███╗   ██╗
██╔════╝██║  ╚██╗ ██╔╝       ██║████╗  ██║
█████╗  ██║   ╚████╔╝        ██║██╔██╗ ██║
██╔══╝  ██║    ╚██╔╝         ██║██║╚██╗██║
██║     ███████╗██║          ██║██║ ╚████║
╚═╝     ╚══════╝╚═╝          ╚═╝╚═╝  ╚═══╝'''
    print(TITLE)
    # select_map()
    # print("## ", end='')
    # cmd = input("")
    # while (cmd != "0"):
    #     print(CLEAR_SCREEN)
    #     print("## ", end='')
    #     cmd = input()
    with open('maps/easy/02_simple_fork.txt') as file:
        pconfig: str = parse_config(file.read())
    m: Map = Map(pconfig)
    # [print(z.show(0)) for z in m.get_zones()]
    print(f"Map size: {m.dimensions}")
    graphics.render(m)
