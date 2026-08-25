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
    BLACK = auto()
    MAROON = auto()
    DARKRED = auto()
    CRIMSON = auto()
    RAINBOW = auto()

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
                self.name = f"{self.orig.name}-{self.dest.name}"
                self.drones: list["str"] = []
                self.capacity = max_capacity

            def available(self) -> bool:
                if self.capacity == -1 or len(self.drones) < self.capacity:
                    return True
                return False

            def is_converse(self, c: "Map.Zone.Connection") -> bool:
                if type(c) is not list:
                    return True if self.orig == c.dest and\
                        self.dest == c.orig and\
                        self.capacity == c.capacity else False

            def show(self):
                return f"{self.orig.name} <=> {self.dest.name}"

        def __init__(self, name: str, coords: tuple[str, str] | list[str],
                     type: ZoneType = ZoneType.NORMAL,
                     color: str = "NONE",
                     capacity: int = -1,
                     drones: int = 0):
            self.name: str = name
            self.coords: tuple[int, int] | list[int] = [int(x) for x in coords]
            self.type = type
            self.color = color
            # self.color = [
            #     c for c in Color if str(c) == "Color." + color.upper()][0]
            self._connections: list[Map.Zone.Connection] = []
            self.drones: list[str] = []
            self.capacity: int = capacity
            for dn in range(drones):
                self.drones.append("D"+str(dn))

        def set_connection(self, dest: "Map.Zone", capacity: int = -1):
            self._connections.append(Map.Zone.Connection(
                self, dest, max_capacity=capacity))

        def get_connections(self) -> list["Map.Zone.Connection"]:
            return (self._connections)

        def node(self, m: "Map") -> int:
            '''
            returns the numeric id of the node
            that represents this zone in the graph
            that represents map m
            '''
            return m.get_zones().index(self)

        def available(self) -> bool:
            if (self.type == "BLOCKED"):
                return False
            if (self.capacity == -1 or
                    len(self.drones) < self.capacity):
                return True
            return False

        def possible_moves(self) -> list["Map.Zone"]:
            available: list["Map.Zone"] = []
            [available.append(c.dest) for c in self.get_connections() if
             c.dest.available() and c.available()]
            return available

        def show(self, mode: int = 0):
            if mode == 0:
                return f"""\x1b[46m\n\n\t{self.name}:
    \t\tCoordinates: {self.coords}
    \t\tType: {self.type}
    \t\tDrones: \n\t\t\t{(chr(10) + (chr(9) * 3)).join([d for d in self.drones])}
    \t\tConnections: \n\t\t\t{(chr(10) + (chr(9) * 3)).join([c.show()
                                            for c in self._connections])}
    \t\tColor: {self.color}\n\x1b[0m
    """
            else:
                pass

    def __init__(self, pconfig: str):
        self._zones: list[Map.Zone] = []
        self.dimensions: list[int] = [0, 0]
        self.drones: int = 0
        self.locked: tuple[str, Map.Zone] = []
        delta: int = 0
        '''
        delta denotes the y-axis offset caused by the weird negative index
        notation that was chosen for the map config files
        '''
        self.colors: list[str] = ["NONE", "GREEN", "RED", "BLUE", "ORANGE",
                             "YELLOW", "CYAN", "PURPLE", "BROWN",
                             "LIME", "MAGENTA", "GOLD", "BLACK",
                             "MAROON", "DARKRED", "CRIMSON", "RAINBOW"]
        for c in pconfig:
            meta: list[list[str]] = [
                [md.lower()] for md in Metadata.__members__ if
                md.lower() in c[1]]
            if ("nb_drones" in c[0]):
                self.drones = int(c[1])
            if ('hub' in c[0]):
                # this branch of the if-else manages cases where we have
                # coordinates in the y-axis
                # breakpoint()
                color: str = "NONE"
                if "color" in c[1]:
                    color = c[1].split("color=")[1].upper()
                    if len(color.split(" ")) == 1:
                        color = color.split("]")[0]
                    else:
                        color = color.split(' ')[0]
                    if color not in self.colors:
                        self.colors.append(color)
                if int(c[1].split(" ")[1:3][1]) < 0:
                    absolute: int = abs(int(c[1].split(" ")[1:3][1]))
                    if (absolute > delta):
                        for z in self._zones:
                            z.coords = [z.coords[0], z.coords[1] + absolute]
                    if ["max_drones"] in meta:
                        md: int = c[1].split("max_drones=")[1]
                        md = md.split("]")[0] if ']' in\
                            md else md.split(' ')[0]
                    if ['zone'] in meta:
                        zsplit: list[str] = c[1].split("zone=")[1]
                        zone_md = zsplit.split(" ")[0]\
                            if len(zsplit.split(" ")) > 1\
                            else zsplit.split("]")[0]
                    self._zones.append(
                        Map.Zone(
                            name := c[1].split(" ")[0],
                            tmp := [
                                c[1].split(" ")[1], '0' if
                                absolute > delta else
                                str(delta-absolute)],
                            color=color,
                            capacity=int(md) if ["max_drones"] in meta
                            else -1,
                            type=ZoneType.__members__.get(
                                zone_md.upper(), ZoneType.NORMAL).name,
                            drones=self.drones if name ==
                            "start" else 0))
                    delta = absolute if absolute > delta else delta
                else:
                    if (delta > 0):
                        pass
                    tmp = c[1].split(" ")[1:3]
                    tmp[1] = str(int(tmp[1]) + delta)
                    if ["max_drones"] in meta:
                        drones_md: int = c[1].split("max_drones=")[1]
                        drones_md = drones_md.split("]")[0] if ']' in\
                            drones_md else md.split(' ')[0]
                    zone_md: str = "NORMAL"
                    if ['zone'] in meta:
                        zsplit: list[str] = c[1].split("zone=")[1]
                        zone_md = zsplit.split(" ")[0]\
                            if len(zsplit.split(" ")) > 1\
                            else zsplit.split("]")[0]
                    self._zones.append(
                        Map.Zone(name := c[1].split(" ")[0],
                                 tmp,
                                 color=color,
                                 capacity=int(drones_md)
                                 if ["max_drones"] in meta
                                 else -1,
                                 type=ZoneType.__members__.get(
                                     zone_md.upper(), ZoneType.NORMAL).name,
                                 drones=self.drones if name ==
                                 "start" else 0))
                if (int(tmp[0]) > self.dimensions[0]):
                    self.dimensions[0] = int(tmp[0])
                if (int(tmp[1]) > self.dimensions[1]):
                    self.dimensions[1] = int(tmp[1])
            if (c[0].lower() == "connection"):
                origen: str = c[1].split("-")[0]
                destination: str = dst\
                    if len((dst := c[1].split("-")[1]).split("[")) == 1\
                    else dst.split(" [")[0]
                mlc: int = -1
                if ['max_link_capacity'] in meta:
                    mlcs: str = c[1].split("max_link_capacity=")[1]
                    if len(mlcs.split(" ")) == 1:
                        mlc = int(mlcs.split("]")[0])
                    else:
                        mlc = int(mlcs.split(" ")[0])
                for z in self._zones:
                    if z.name.lower() == origen.lower():
                        for zz in self._zones:
                            if zz.name.lower() == destination.lower():
                                z.set_connection(zz, capacity=mlc)
                                zz.set_connection(z, capacity=mlc)
        for z in self._zones:
            if (int(z.coords[0]) + 1 > self.dimensions[0]):
                self.dimensions[0] = int(z.coords[0]) + 1
            if (int(z.coords[1]) + 1 > self.dimensions[1]):
                self.dimensions[1] = int(z.coords[1]) + 1

    def move(self, z1: "Map.Zone",
             z2: "Map.Zone", d: str,):
        if (z1 in self.get_zones() and
            z2 in self.get_zones() and
            d in z1.drones and
                z2.name in [c.dest.name for c in z1.get_connections()]):
            z1.drones.remove(d)
            z2.drones.append(d)
            # else:
            #     m.locked.append(d, z2)
            print(f"{d}-{z2.name}")
        else:
            raise Exception(
                f'''\x1b[43m\n\n\tMap.move ERROR:\n\n\tOne of the following is\
 not true:
            \t\tBoth zones are in the map
            \t\t'{d}' is in {z1.name}
            \t\tThere is a connection from '{z1.name}'\
to '{z2.name}'\x1b\n[0m''')

    def get_zones(self, only_occupied: bool = False) -> list["Map.Zone"]:
        if not only_occupied:
            return self._zones
        return [z for z in self.get_zones() if len(z.drones) > 0]

    # def get_connection(self, o)

    def get_zone(self, name: str) -> "Map.Zone":
        found_zone = [z for z in self.get_zones() if z.name == name.lower()]
        if len(found_zone) == 1:
            return found_zone[0]
        return None

    def get_graph(self):
        vertices: list[tuple[int, int]] = []
        for zi in range(len(self._zones)):
            for c in [z
                      for z in
                      self._zones[zi].get_connections()
                      if z.dest.type != 'BLOCKED']:
                if (self._zones.index(c.orig) < self._zones.index(c.dest)):
                    vertices.append(
                        (self._zones.index(c.orig), self._zones.index(c.dest)))
        return (vertices)

    def show(self):
        return f'''
Zones: {[z.name for z in self.get_zones()]}
        '''


def parse_config(file: str):
    result: list[list[str] | list[list[list[str]]]] = []
    splat: list[str] = file.split("\n")
    splat = [s for s in splat if not s.startswith("#")]
    result.extend(
        [[s[0], s[1]] for s in
         [ss.split(": ") for ss in splat if len(ss.split(": ")) == 2]])
    return (result)


def select_map() -> str:
    print(CLEAR_SCREEN)
    print('\x1b[36m'+TITLE+'\x1b[0m')
    print("\x1b[42m\n")
    print("Hello please pick a map\n\x1b[0m")
    file_index: list[str] = []
    directory: str = 'maps/'
    directories = [d for d in os.listdir(directory) if
                   os.path.isdir(os.path.join(directory, d))]
    files = [f for f in os.listdir(directory) if
             os.path.isfile(os.path.join(directory, f))]
    for d in directories:
        dfiles = [f for f in os.listdir(directory+"/"+d) if
                  os.path.isfile(os.path.join(directory+"/"+d, f))]
        print("\t\x1b[34m" + d + "/\x1b[0m")
        for df in dfiles:
            if df.endswith(".txt"):
                file_index.append([str(directories.index(d)) + '.' +
                                   str(dfiles.index(df)), d+'/'+df])
            print("\t\t\x1b[32m"+f'({directories.index(d)}.{dfiles.index(df)})\
                  \t'+df+"\x1b[0m" if df.endswith(".txt") else
                  "\t\x1b[31m"+df+" (not a text file)\x1b[0m")
    for f in files:
        print("\t\x1b[32m"+f'({files.index(f)})\t'+f+"\x1b[0m" if
              f.endswith(".txt") else
              "\t\x1b[31m"+f+" (not a text file)\x1b[0m")
    choice = input("\n\x1b[46m## ")
    if (choice not in [i[0] for i in file_index]):
        print('\x1b[0m')
        select_map()
    with open('maps/'+[m[1] for m in file_index if m[0] == choice][0]) as file:
        print('\x1b[0m')
        pconfig: str = parse_config(file.read())
    return pconfig


def next_turn(m: Map) -> tuple[int, int]:
    '''
    next_turn runs the next simulation turn
    returns True when all drones reached goal
    False otherwise
    '''
    def hasPath(xs: list[tuple[int]], conn: tuple[int, int], counter: int = 0):
        '''
        hasPath returns the number of intermediate vertices
        between two points if a path between nodes
        tuple[0] and tuple[1]
        exists, otherwise -1
        '''
        if (conn[0] == conn[1]):
            return counter
        xsf = [(n, m) for (n, m) in xs if n != conn[0]]
        return next((x for x in [
            hasPath(xsf, (m, conn[1]), counter + 1)
            for (n, m) in xs if n == conn[0]] if x > 0), -1)

    move_count: int = 0
    moved_drones: list[str] = []
    move_flag: bool = True
    if (m.get_zone("impossible_goal")):
        goal_zone: Map.Zone = m.get_zone("impossible_goal")
        if len(m.get_zone("impossible_goal").drones) == m.drones:
            return [move_count, 1]
    else:
        goal_zone: Map.Zone = m.get_zone("goal")
        if len(goal_zone.drones) == m.drones:
            return [move_count, 1]
    # flushing locked drones entering into restricted zones
    if (len(m.locked) > 0):
        for d in m.locked:
            if (d[1].available()):
                m.move([z for z in m.get_zones() if d[0] in z.drones][0],
                       d[1], d[0])
                moved_drones.append(d[0])
                move_count += 1
    m.locked = []
    # as long as there have been moved drones keep checking if zones have been
    # unlocked making more moves are possible, same structure as bubble sort
    while (move_flag):
        move_flag = False
        for z in m.get_zones(only_occupied=True):
            # here i use a copy of the list of drones because the list
            # itself can change during iteration, causing elements to be
            # skipped
            for d in z.drones.copy():
                next_forward_priority: Map.Zone = [
                    nxtzone for nxtzone in z.possible_moves()
                    if (step_count := hasPath(
                        m.get_graph(),
                        (nxtzone.node(m), goal_zone.node(m))))
                    < hasPath(m.get_graph(),
                              (z.node(m), goal_zone.node(m)))
                    and
                    step_count != -1
                    and
                    nxtzone.type == "PRIORITY"]
                next_forward: Map.Zone = [
                    nxtzone for nxtzone in z.possible_moves()
                    if (scount := hasPath(
                        m.get_graph(),
                        (nxtzone.node(m), goal_zone.node(m))))
                    < hasPath(m.get_graph(),
                              (z.node(m), goal_zone.node(m)))
                    and scount != -1
                    and nxtzone.type != "RESTRICTED"]
                next_forward_restricted: Map.Zone = [
                    nxtzone for nxtzone in z.possible_moves()
                    if (step_count := hasPath(
                        m.get_graph(),
                        (nxtzone.node(m), goal_zone.node(m))))
                    < hasPath(m.get_graph(),
                              (z.node(m), goal_zone.node(m)))
                    and
                    step_count != -1
                    and
                    nxtzone.type == "RESTRICTED"]
                if len(next_forward_priority) > 0 and d not in moved_drones:
                    m.move(z, next_forward_priority[0], d)
                    move_flag = True
                    moved_drones.append(d)
                    move_count += 1
                if len(next_forward) > 0 and d not in moved_drones:
                    m.move(z, next_forward[0], d)
                    move_flag = True
                    moved_drones.append(d)
                    move_count += 1
                if len(next_forward_restricted) > 0 and d not in moved_drones:
                    # m.move(z, next_forward_restricted[0], d)
                    rdest: Map.Zone = next_forward_restricted[0]
                    m.locked.append((d, rdest))
                    print(f"{d}-{z.name}-{rdest.name}")
                    move_flag = True
                    moved_drones.append(d)
                    move_count += 1

    # print("Zones with drones in turn: " +
    #       f"{[z.name for z in m.get_zones(only_occupied=True)]}")
    print(f"Number of moves in this turn: {move_count}")
    if len(goal_zone.drones) == m.drones:
        return [move_count, 1]
    if (move_count == 0):
        return [move_count, 1]
    return [move_count, 0]


if __name__ == "__main__":
    CLEAR_SCREEN: str = '\x1b[2J\x1b[H'
    TITLE: str = '''
███████╗██╗  ██╗   ██╗       ██╗███╗   ██╗
██╔════╝██║  ╚██╗ ██╔╝       ██║████╗  ██║
█████╗  ██║   ╚████╔╝        ██║██╔██╗ ██║
██╔══╝  ██║    ╚██╔╝         ██║██║╚██╗██║
██║     ███████╗██║          ██║██║ ╚████║
╚═╝     ╚══════╝╚═╝          ╚═╝╚═╝  ╚═══╝
'''

    # print('\x1b[94m'+TITLE+'\x1b[0m')
    pconfig: str = select_map()
    # try:
    m: Map = Map(pconfig)
    # [print(z.show(0)) for z in m.get_zones()]
    print(m.get_graph())
    # breakpoint()
    print(f"Map size: {m.dimensions}")
    g: graphics.Grid = graphics.Grid(m, 3, vpad=5, hpad=4)
    g.print_grid()
    print(m.show())
    hub = m.get_zone('start')
    print(hub.get_connections()[0])
    print(hub.show())
    turn: int = 0
    print(f"==== Turn {turn} ====")
    turn += 1
    tmoves: int
    finished: int
    tmoves, finished = next_turn(m)
    total_moves: int = tmoves
    while (not finished):
        # breakpoint()
        print(f"==== Turn {turn} ====")
        tmoves, finished = next_turn(m)
        total_moves += tmoves
        turn += 1
        if not tmoves and finished:
            print("\x1b[41mMAZE STUCK\x1b[0m")
    print(f"Total moves: {total_moves}")
    # except Exception as e:
    #     print(e)
