import fly_in as fi


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
        'BACKGROUND': '\x1b[90m'
    }

    def __init__(self, m: fi.Map, csize: int = 6,
                 vpad: int = 1, hpad: int = 1) -> None:
        self.map: fi.Map = m
        self.zones: list[fi.Map.Zone] = self.map.get_zones()
        # cell size
        self.csize: int = csize
        # vertical padding: amount of scaffolding between cells vertically
        self.vpad: int = vpad
        # horizontal padding: amount of scaffolding between cells horizontally
        self.hpad: int = hpad
        self.scaffolding: str = '█' * self.csize
        self.ascii_grid: list[list[str]] = self.base_grid(
            self.map.dimensions[1], self.map.dimensions[0],
            self.vpad, hpad=self.hpad)

    def base_grid(self, height: int, width: int,
                  vpad: int = 1, hpad: int = 1) -> list[list[str]]:
        amap: list[list[str]] = []
        for r in range(2 + (height + ((height - 1) * vpad))):
            row: list[str] = []
            for c in range(2 + (width + ((width - 1) * hpad))):
                # breakpoint()
                if not ((r % (vpad + 1) == 1) and (c % (hpad + 1) == 1)):
                    row.append(self.scaffolding)
                elif (self.tr([c, r]) in [z.coords for z in self.map.get_zones()]):
                    row.append(" " * self.csize)
                else:
                    row.append(self.scaffolding)
            amap.append(row)
        return (amap)

    def tr(self, coords: list[int],
           direction: int = 0) -> list[int]:
        '''
        Transform function takes grid coordinates and translates
        them to logical coordinates
        '''
        if direction == 0:
            return [coords[0] // (self.hpad + 1), coords[1] // (self.vpad + 1)]

    def print_grid(self) -> None:
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
