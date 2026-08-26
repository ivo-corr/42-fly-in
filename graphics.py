import fly_in as fi


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
        self.connections = list(
            filter(lambda x: x.dest.coords[0] > x.orig.coords[0],
                   self.connections))
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

    def base_grid(self, height: int, width: int,
                  vpad: int = 1, hpad: int = 1) -> list[list[str]]:
        def connect(map: list[list[str]], conn: list[list[int]]) -> bool:
            delta_x: int = conn[1][0] - conn[0][0]
            delta_y: int = conn[1][1] - conn[0][1]
            # end of recursion
            if (delta_x == 1 and (delta_y == 0 or abs(delta_y) == 1)):
                return True
            if delta_y != 0:
                # first case: origin is closer to median than destination
                # render y-axis first and then x-axis
                if (abs(conn[0][1] - self.hmedian) <
                        abs(conn[1][1] - self.hmedian)):
                    # origin is closer to median than destination
                    map[conn[0][1] + (1 if delta_y > 0 else -1)][conn[0][0]] =\
                        (f'{self.colors["BG_BG"]} ' * (self.csize//2)) +\
                        ((connectors['vertical'] + f'{self.colors["BG_BG"]} ')
                         if abs(delta_y) > 1 else
                         ((connectors['bl_edge'] if delta_y > 0 else
                           connectors['tl_edge'])
                          + f'{self.colors["BG_BG"] + connectors["horizontal"]}') * (self.csize//2))
                    return connect(
                        map,
                        [[conn[0][0], conn[0][1] + (1 if delta_y > 0 else -1)],
                         conn[1]])
                # destination is closer to median that origin
                # render x-axis first and then y-axis
                else:
                    # breakpoint()
                    # if (delta_x == 0):
                    #     map[conn[0][1] + (-1 if delta_y < 0 else 1), conn[0][0]] =
                    # if ([conn[0][0], conn[0][1]] == conn[1]):
                    return True
                    map[conn[0][1] + ((-1 if delta_y < 0 else 1) if delta_x == 0 else 0)][conn[0][0] + (1 if delta_x > 0 else 0)] =\
                        ((connectors['horizontal'] * self.csize)
                         if abs(delta_x) > 1
                         else
                         ((f'{self.colors["BG_BG"]}{connectors["horizontal"]}'
                           * (self.csize//2)) + (
                               connectors['br_edge']
                               if delta_x == 1
                               else
                               connectors['tr_edge']) +
                            (f'{self.colors["BG_BG"]} ' * (self.csize//2)))) if delta_x != 0 else (f'{self.colors["BG_BG"]} ' * (self.csize//2)) + (connectors['vertical'] + f'{self.colors["BG_BG"]} ')
                    return connect(
                        map,
                        [[conn[0][0] + (1 if delta_x > 0 else 0), conn[0][1] + (-1 if delta_y < 0 and delta_x == 0 else 0)],
                         conn[1]])
                    # x coord aligned
                    # if (conn[0][0] == conn[1][0] and delta_y != 0):
                    #     map[conn[0][1] + (1 if delta_y < 0 else (-1))][conn[0][0]] =\
                    #         (f'{self.colors["BG_BG"]} ' * (self.csize//2)) +\
                    #         ((connectors['vertical'] + f'{self.colors["BG_BG"]} ' * (self.csize//2)))
                    #     return connect(
                    #         map,
                    #         [[conn[0][0], conn[0][1] + (1 if delta_y > 0 else -1)], conn[1]]
                    #     )
                    # # x coord not aligned
                    # else:
                    #     map[conn[0][1]][conn[0][0] + 1] =\
                    #         connectors["horizontal"] * self.csize if\
                    #         delta_x > 1 else\
                    #         (connectors['horizontal'] * (self.csize//2)) + (
                    #             connectors["br_edge"] if delta_y < 0 else
                    #             connectors["tr_edge"]) + (f'{self.colors["BG_BG"]} ' * (self.csize//2))
                    #     return connect(
                    #         map,
                    #         [[conn[0][0] + 1, conn[0][1] + (-2 if (delta_x == 1 and delta_y < 0) else (2 if (delta_x == 1 and delta_y > 0) else 0))], conn[1]]
                    #     )
            elif (delta_y == 0 and delta_x != 0):
                map[conn[0][1]][conn[0][0] + 1] = connectors[
                    'horizontal'] * self.csize
                return connect(map, [[conn[0][0] + 1, conn[0][1]], conn[1]])

        amap: list[list[str]] = []
        connectors: dict[str] = {'horizontal': f"{self.colors['BG_BG']}─"
                                 f"{self.colors['END']}",
                                 'vertical':  f"{self.colors['BG_BG']}│"
                                 f"{self.colors['END']}",
                                 'tl_edge': f"{self.colors['BG_BG']}┌"
                                 f"{self.colors['END']}",
                                 'tr_edge': f"{self.colors['BG_BG']}┐"
                                 f"{self.colors['END']}",
                                 'bl_edge': f"{self.colors['BG_BG']}└"
                                 f"{self.colors['END']}",
                                 'br_edge': f"{self.colors['BG_BG']}┘"
                                 f"{self.colors['END']}"}
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
        for c in self.raw_connections:
            connect(amap, c)
            # print(f"Connecting {c[0]} and {c[1]}")
            # delta_x: int = abs(c[0][0] - c[1][0])
            # delta_y: int = abs(c[0][1] - c[1][1])
            # # this connection is horizontal so it will be rendered first
            # if (delta_y == 0):
            #     print("The connection is horizontal")
            #     print(delta_x)
            #     for cell in range(delta_x - 1):
            #         amap[c[0][1]][c[0][0] + cell + 1] = connectors[
            #             'horizontal'] * self.csize
            # else:
            #     pass
        return (amap)

    @staticmethod
    def get_conn_coords(grid: "Grid", c: fi.Map.Zone.Connection) -> list[list[int]]:
        src_coord: list[int] = c.orig.coords
        dest_coord: list[int] = c.dest.coords
        return [src_coord, dest_coord]

    def tr(self, coords: list[int],
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

    def print_grid(self) -> None:
        CLEAR_SCREEN: str = '\x1b[2J\x1b[H'
        print(CLEAR_SCREEN)
        self.ascii_grid = self.base_grid(
            self.map.dimensions[1], self.map.dimensions[0],
            self.vpad, hpad=self.hpad)
        for row in self.ascii_grid:
            for cell in row:
                print(cell, end='')
            print()



# def render_base(height: int, width: int,
#                 horizontal_padding: int = 6,
#                 vertical_padding: int = 2) -> list[list[str]]:
#     empty_cell: str = '\x1b[90m' + '█'*horizontal_padding + '\x1b[0m'
#     amap: list[list[str]] = []
#     for r in range(height*(vertical_padding)-(vertical_padding+1)):
#         row: list[str] = []
#         for c in range(width):
#             row.append(empty_cell)
#         amap.append(row)
#     return (amap)


# def render_zones(amap: list[list[str]],
#                  zones: list[fi.Map.Zone],
#                  horizontal_padding: int = 6,
#                  vertical_padding: int = 1) -> None:
#     # the mapping from logical map to rendered is 2*x+1
#     def is_occupied(x: int, y: int):
#         if amap[2*x+1][2*y+1] == '\x1b[90m' +\
#                 '█'*horizontal_padding + '\x1b[0m':
#             return False
#         return True

#     zone: str = '\x1b[40m\x1b[100m█\x1b[47m{}\x1b[90m██\x1b[0m'
#     connectors: dict[str] = {'horizontal': "─", 'vertical': "│", 'tl_edge': "┌", 'tr_edge': "┐", 'bl_edge': "└",  'br_edge': "┘"}
#     colors = {
#         'NONE': '',
#         'GREEN': '\x1b[42m',
#         'RED': '\x1b[41m',
#         'BLUE': '\x1b[44m',
#         'ORANGE': '\x1b[48;5;208m',
#         'YELLOW': '\x1b[43m',
#         'CYAN': '\x1b[46m',
#         'PURPLE': '\x1b[45m',
#         'BROWN': '\x1b[48;5;130m',
#         'LIME': '\x1b[48;5;10m',
#         'MAGENTA': '\x1b[45m',
#         'GOLD': '\x1b[48;5;220m',
#         'BACKGROUND': '\x1b[90m'
#     }
#     for row in [i for i in range(len(amap)) if i % (2*vertical_padding) == 1]:
#         for cell in [c for c in range(len(amap[0])) if c % 2 == 1]:
#             # (x,y) where x and y are odd always fall in the logical map
#             # (cell // 2, row // 2) is the mapping from the rendered map to
#             # the logical map
#             if [cell // 2, row // (2*vertical_padding)] in [z.coords for z in
#                                                             zones]:
#                 zdrones = [len(z.drones) for z in zones if z.coords ==
#                            [cell // 2, row // (2*vertical_padding)]][0]
#                 c = [
#                     colors[color.name] for color in
#                     [z.color for z in zones if
#                      z.coords == [cell // 2, row // (2*vertical_padding)]]][0]
#                 amap[row][cell] = f'{c}{zdrones}\x1b[0m' +\
#                     (f'{c}  ' if zdrones < 10 else f'{c} ') +\
#                     '\x1b[90m'+'█' *\
#                     (horizontal_padding//2+4)+'\x1b[0m'
#     breakpoint()
#     for src_coord, coord in [(z.coords, [c.dest.coords for c in z.get_connections()]) for z in zones]:
#         # print(f"Connecting {src_coord} and {coord}")
#         delta_x: int = coord[-1][0] - src_coord[0]
#         delta_y: int = coord[-1][1] - src_coord[1]
#         breakpoint()
#         if abs(delta_y) > 0:
#             pass
#         else:
#             # breakpoint()
#             amap[(2*src_coord[1])+2][2*src_coord[0]+2] = amap[(2*src_coord[1])+2][2*src_coord[0]+2].split("[90m")[0] + '\x1b[0m\x1b[100m' + (connectors['horizontal']*(horizontal_padding+1))
#             amap[(2*src_coord[1])+1][2*src_coord[0]+1+1] = connectors['horizontal'] * 2 * (horizontal_padding - 1)
#             for row in amap:
#                 for cell in row:
#                     print(cell, end='')
#                 print("")
#             pass

#     # breakpoint()
#     return (amap)


# def render(m: fi.Map,
#            horizontal_padding: int = 6,
#            vertical_padding: int = 2) -> None:
#     CLEAR_SCREEN: str = '\x1b[2J\x1b[H'
#     empty_cell: str = '\x1b[90m\x1b[90m▄▄▄▄\x1b[0m'
#     drone: str = '(●)'
#     render_width: int = (w := m.dimensions[1] + 1) + (w - 1) + 2
#     render_height: int = (h := m.dimensions[0] + 1) + (h - 1) + 2
#     amap: list[list[str]] = render_base(render_width, render_height,
#                                         horizontal_padding=horizontal_padding,
#                                         vertical_padding=vertical_padding)
#     amap = render_zones(amap, m.get_zones(), vertical_padding=vertical_padding)
#     # print(CLEAR_SCREEN)
#     for row in amap:
#         for cell in row:
#             print(cell, end='')
#         print("")


# if __name__ == "__main__":
#     g: Grid = Grid(10, 10, 5)
#     # print(g.ascii_grid)
#     g.print_grid()
