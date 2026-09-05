import fly_in as fi
from time import sleep


def pr_grid(grid: list[list[str]]):
    for row in grid:
        for column in row:
            print(column, end='')
        print()


class Grid():
    colors = {
        'NONE': '',
        'GREEN': '\x1b[42m',
        'RED': '\x1b[41m',
        'BLUE': '\x1b[44m',
        'ORANGE': '\x1b[48;5;208m',
        'YELLOW': '\x1b[43m',
        'CYAN': '\x1b[46m',
        'PURPLE': '\x1b[45m',
        'BROWN': '\x1b[48;5;130m',
        'LIME': '\x1b[48;5;10m',
        'MAGENTA': '\x1b[45m',
        'GOLD': '\x1b[48;5;220m',
        "NOT_FOUND": '',
        'BACKGROUND': (bg := '\x1b[90m'),
        'BG_BG': '\x1b[' + str(int(bg.split("[")[1][:-1]) + 10) + 'm',
        'END': '\x1b[0m'
    }

    def __init__(self, m: fi.Map, csize: int = 6,
                 vpad: int = 1, hpad: int = 1) -> None:
        self.map: fi.Map = m
        self.zones: list[fi.Map.Zone] = self.map.get_zones()
        # we unpack all connections in a flat list
        self.connections: list[fi.Map.Zone.Connection] = [
            element for sublist in [ee for ee in [
                c for c in [z.get_connections() for z in self.zones]
                ]] for element in sublist]
        # we select only the connections that need to be rendered
        # self.connections = list(
        #     filter(lambda x: x.dest.coords[0] > x.orig.coords[0],
        #            self.connections))
        self.raw_zones: list[list[int]] = []
        self.raw_connections: list[list[list[int]]] = []
        # we translate each connection to a set of coordinates
        self.conn_coordinates: list[list[list[int]]] = list(
            map(lambda x: Grid.get_conn_coords(x),
                self.raw_connections))
        # cell size
        self.csize: int = csize
        # vertical padding: amount of scaffolding between cells vertically
        self.vpad: int = vpad
        # horizontal padding: amount of scaffolding between cells horizontally
        self.hpad: int = hpad
        # horizontal median for symmetric connection rendering
        self.hmedian: int = (self.map.dimensions[1]//2) + 1 + self.vpad
        self.bg_color: str = self.colors['BACKGROUND']
        self.scaffolding: str = f'{self.bg_color}█' * self.csize +\
            self.colors['END']
        self.ascii_grid: list[list[str]] = self.base_grid(
            self.map.dimensions[1], self.map.dimensions[0],
            self.vpad, hpad=self.hpad)

    def rconnect(self, conn: list[list[int]], delay: int = 0,
                 a_char: str = ''):
        delta_x: int = conn[1][0] - conn[0][0]
        delta_y: int = conn[1][1] - conn[0][1]
        if delta_x == 0 and delta_y == 0:
            return True
        if abs(delta_x) * abs(delta_y) > 0:
            # draw diagonal
            if delta_y > 0:
                breakpoint()
                self.ascii_grid[conn[0][1]][conn[0][0]] = (
                    self.colors['BACKGROUND'] + self.colors['BG_BG'] +
                    '█' * (self.csize // 2)) + '▫️' +\
                    ('█' * (self.csize // 2)) + self.colors['END']
            self.rconnect([[conn[0][0] + 1, conn[0][1] - 1], conn[1]])
        else:
            if delta_x > 0:
                if ' ' not in self.ascii_grid[conn[0][1]][conn[0][0]]:
                    if (a_char == ''):
                        self.ascii_grid[conn[0][1]][conn[0][0]] = (
                            self.colors['BACKGROUND'] + self.colors['BG_BG'] +
                            '█' * (self.csize // 2)) + '▫️' +\
                                ('█' * (self.csize // 2)) + self.colors['END']
                        sleep(delay)
                    else:
                        self.ascii_grid[conn[0][1]][conn[0][0]] = (
                            self.colors['BACKGROUND'] + self.colors['BG_BG'] +
                            '█' * (self.csize // 2)) + '◯' +\
                                ('█' * (self.csize // 2)) + self.colors['END']
                self.rconnect([[conn[0][0] + 1, conn[0][1]], conn[1]])
            if delta_x == 0 and delta_y != 0:
                if ' ' not in self.ascii_grid[conn[0][1]][conn[0][0]]:
                    if (a_char == ''):
                        self.ascii_grid[conn[0][1]][conn[0][0]] = (
                            self.colors['BACKGROUND'] + self.colors['BG_BG'] +
                            '█' * (self.csize // 2)) + '▫️' +\
                                ('█' * (self.csize // 2)) + self.colors['END']
                    else:
                        pass
                sleep(delay)
                if delta_y > 0:
                    self.rconnect([[conn[0][0], conn[0][1] + 1], conn[1]])
                elif delta_y < 0:
                    self.rconnect([[conn[0][0], conn[0][1] - 1], conn[1]])

    def connect_grid(self):
        for c in self.raw_connections:
            self.rconnect(c)

    def base_grid(self, height: int, width: int,
                  vpad: int = 1, hpad: int = 1) -> list[list[str]]:
        amap: list[list[str]] = []
        for r in range(2 + (height + ((height - 1) * vpad))):
            row: list[str] = []
            for c in range(2 + (width + ((width - 1) * hpad))):
                # breakpoint()
                if not ((r % (vpad + 1) == 1) and (c % (hpad + 1) == 1)):
                    row.append(self.scaffolding)
                elif (self.tr([c, r]) in
                      [z.coords for z in self.map.get_zones()]):
                    color = [z for z in self.map.get_zones() if z.coords == self.tr([c, r])][0].color
                    zdrones = [len(z.drones) for z in self.map.get_zones() if z.coords == self.tr([c, r])][0]
                    zdrones_digits = len(str(zdrones))
                    if (color in self.colors.keys()):
                        row.append(self.colors[color] + str(zdrones) + " " * (self.csize - zdrones_digits))
                    else:
                        row.append(self.colors["NOT_FOUND"] + str(zdrones) + " " * (self.csize - zdrones_digits))
                    self.raw_zones.append([c, r])
                    # print(f"{[self.tr([c,r])]} correlates to {[c,r]} ")
                else:
                    # check if this is part of a connection line
                    if (True):
                        row.append(self.scaffolding)
            amap.append(row)
        for c in self.connections:
            origin = list(
                filter(lambda x: self.tr(x) == c.orig.coords, self.raw_zones))[
                    0]
            destination = list(
                filter(lambda x: self.tr(x) == c.dest.coords, self.raw_zones))[
                    0]
            self.raw_connections.append([origin, destination])
        return (amap)

    @staticmethod
    def get_conn_coords(grid: "Grid", c: fi.Map.Zone.Connection) -> list[list[int]]:
        src_coord: list[int] = c.orig.coords
        dest_coord: list[int] = c.dest.coords
        return [src_coord, dest_coord]

    def tr(self, coords: list[int] | list[list[int]],
           direction: int = 0) -> list[int]:
        '''
        Transform function takes grid coordinates and translates
        them to logical coordinates when direction is 0, and the converse
        if direction is 1
        note: since the function is many-to-one in one direction there is no
        unique inverse
        '''
        if direction == 0:
            return [coords[0] // (self.hpad + 1), coords[1] // (self.vpad + 1)]
        if direction == 1:
            return []

    def print_grid(self, msg: str, delay: int = 1) -> None:
        CLEAR_SCREEN: str = '\x1b[2J\x1b[H'
        print(CLEAR_SCREEN)
        self.ascii_grid = self.base_grid(
            self.map.dimensions[1], self.map.dimensions[0],
            self.vpad, hpad=self.hpad)
        self.connect_grid()
        for row in self.ascii_grid:
            for cell in row:
                print(cell, end='')
            print()
        print(msg)
        sleep(delay)
        # print("0/R: run\n1/N: next turn\n2/S: map select")