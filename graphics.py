import fly_in as fi
from time import sleep
from typing import Any


def pr_grid(grid: list[list[str]]) -> None:
    """Print a character grid to the terminal, row by row.

    Parameters
    ----------
    grid : list[list[str]]
        A 2D grid of strings (e.g. ANSI-colored cell contents) to print,
        where each inner list is a row.

    Returns
    -------
    None
    """
    for row in grid:
        for column in row:
            print(column, end='')
        print()


class Grid():
    """Renders a :class:`fly_in.Map` as an ANSI-colored terminal grid.

    Builds and refreshes an ASCII/ANSI representation of the map's
    zones, their drone counts, and the connections between them,
    including simple orthogonal/diagonal line-drawing between cells.

    Attributes
    ----------
    bg : str
        ANSI escape code for the grid's background color.
    colors : dict[str, str]
        Mapping from zone color names (and a few special keys like
        ``'BACKGROUND'``, ``'BG_BG'``, and ``'END'``) to their ANSI
        escape codes.
    """

    bg = '\x1b[90m'
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
        'BACKGROUND': bg,
        'BG_BG': '\x1b[' + str(int(bg.split("[")[1][:-1]) + 10) + 'm',
        'END': '\x1b[0m'
    }

    def __init__(self, m: fi.Map, csize: int = 6,
                 vpad: int = 1, hpad: int = 1) -> None:
        """Initialize a Grid renderer bound to a given map.

        Flattens the map's zones and connections, computes layout
        parameters (cell size, padding, horizontal median), and builds
        the initial ASCII grid.

        Parameters
        ----------
        m : fi.Map
            The map to render.
        csize : int, optional
            The width (in characters) of each rendered cell. Defaults
            to 6.
        vpad : int, optional
            The number of scaffolding rows inserted between grid rows
            vertically. Defaults to 1.
        hpad : int, optional
            The number of scaffolding columns inserted between grid
            columns horizontally. Defaults to 1.

        Returns
        -------
        None
        """
        self.map: fi.Map = m
        self.zones: list[fi.Zone] = self.map.get_zones()
        # we unpack all connections in a flat list
        self.connections: list[fi.Connection] = [
            element for sublist in [ee for ee in [
                c for c in [z.get_connections() for z in self.zones]
                ]] for element in sublist]
        # we select only the connections that need to be rendered
        # self.connections = list(
        #     filter(lambda x: x.dest.coords[0] > x.orig.coords[0],
        #            self.connections))
        self.raw_zones: list[list[int]] = []
        self.raw_connections: list[list[list[Any]]] = []
        # we translate each connection to a set of coordinates
        # self.conn_coordinates: list[list[list[int]]] = list(
        #     map(lambda x: Grid.get_conn_coords(x),
        #         self.raw_connections))
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
                 a_char: str = '') -> bool:
        """Recursively draw a connection line between two grid cells.

        Walks from ``conn[0]`` toward ``conn[1]`` one step at a time
        (diagonally when both axes differ, otherwise straight), marking
        each intermediate empty cell with a connector glyph, and
        optionally pausing ``delay`` seconds between steps for an
        animated effect.

        Parameters
        ----------
        conn : list[list[int]]
            A two-element list ``[start, end]`` of ``[x, y]`` grid
            coordinates describing the segment to draw.
        delay : int, optional
            Seconds to sleep after drawing each straight-line step.
            Defaults to 0.
        a_char : str, optional
            If non-empty, use the alternate connector glyph (``'◯'``)
            instead of the default (``'▫️'``) when marking straight-line
            cells. Defaults to ``''``.

        Returns
        -------
        bool
            ``True`` once the start and end coordinates coincide
            (recursion base case), ``False`` otherwise (returned by the
            recursive branches after having drawn their segment).
        """
        delta_x: int = conn[1][0] - conn[0][0]
        delta_y: int = conn[1][1] - conn[0][1]
        if delta_x == 0 and delta_y == 0:
            return True
        if abs(delta_x) * abs(delta_y) > 0:
            # draw diagonal
            if delta_y > 0:
                self.ascii_grid[conn[0][1]][conn[0][0]] = (
                    self.colors['BACKGROUND'] + self.colors['BG_BG'] +
                    '█' * (self.csize // 2)) + '▫️' +\
                    ('█' * (self.csize // 2)) + self.colors['END']
            self.rconnect([[conn[0][0] + 1, conn[0][1] - 1], conn[1]])
        else:
            if delta_x > 0:
                if ' ' not in self.ascii_grid[conn[0][1]][conn[0][0]]\
                        and 'D' not in self.ascii_grid[conn[0][1]][conn[0][0]]:
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
                if ' ' not in self.ascii_grid[conn[0][1]][conn[0][0]]\
                        and 'D' not in self.ascii_grid[conn[0][1]][conn[0][0]]:
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
        return False

    def bresenham(self, x0: int, y0: int, x1: int, y1: int)\
            -> list[tuple[int, int]]:
        """Compute grid points on a line between two points (Bresenham's
        algorithm).

        Parameters
        ----------
        x0 : int
            X coordinate of the starting point.
        y0 : int
            Y coordinate of the starting point.
        x1 : int
            X coordinate of the ending point.
        y1 : int
            Y coordinate of the ending point.

        Returns
        -------
        list[tuple[int, int]]
            The sequence of ``(x, y)`` integer points forming a
            straight line from ``(x0, y0)`` to ``(x1, y1)`` inclusive.
        """
        points: list[tuple[int, int]] = []
        dx: int = abs(x1 - x0)
        dy: int = -abs(y1 - y0)
        sx: int = 1 if x0 < x1 else -1
        sy: int = 1 if y0 < y1 else -1
        err: int = dx + dy

        while True:
            points.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy
        return points

    def connect_grid(self) -> None:
        """Draw all connection lines between zones onto the ASCII grid.

        For each raw connection, computes its line points via
        :meth:`bresenham` and marks the corresponding grid cells with a
        connector glyph, embedding any in-transit drone markers
        (``c[2]``) roughly at the midpoint of the line.

        Returns
        -------
        None
        """
        for c in self.raw_connections:
            points: list[tuple[int, int]] =\
                self.bresenham(c[0][0], c[0][1], c[1][0], c[1][1])
            for p in points:
                if ' ' not in self.ascii_grid[p[1]][p[0]]\
                        and 'D' not in self.ascii_grid[p[1]][p[0]]:
                    if len(c[2]) > 0:
                        if (points.index(p) - 1) in range(
                            (len(points)//2) - (len(c[2])//2) - 1,
                                (len(points)//2) + len(c[2]) -
                                (len(c[2])//2) + 1):
                            self.ascii_grid[p[1] - 1][p[0]] = (
                                self.colors['BACKGROUND'] +
                                '█' * (((self.csize) // 2) - 1)) + c[2][0] +\
                                ('█' * (self.csize // 2)) + self.colors['END']
                            c[2].remove(c[2][0])
                    self.ascii_grid[p[1]][p[0]] = (
                        self.colors['BACKGROUND'] + self.colors['BG_BG'] +
                        '█' * (self.csize // 2)) + '▫️' +\
                        ('█' * (self.csize // 2)) + self.colors['END']

    def base_grid(self, height: int, width: int,
                  vpad: int = 1, hpad: int = 1) -> list[list[str]]:
        """Build the base ASCII grid, placing zone cells and scaffolding.

        Constructs a padded 2D grid sized from ``height``/``width`` and
        the given padding, filling non-zone positions with scaffolding
        blocks and zone positions with a colored cell showing the
        zone's current drone count. Also records each zone's raw grid
        coordinates (``self.raw_zones``) and each connection's raw
        origin/destination grid coordinates plus its current drones
        (``self.raw_connections``) for later use by :meth:`connect_grid`.

        Parameters
        ----------
        height : int
            The map's logical height (number of rows of zones).
        width : int
            The map's logical width (number of columns of zones).
        vpad : int, optional
            Vertical scaffolding padding between zone rows. Defaults
            to 1.
        hpad : int, optional
            Horizontal scaffolding padding between zone columns.
            Defaults to 1.

        Returns
        -------
        list[list[str]]
            The constructed ASCII grid, as a list of rows of cell
            strings.
        """
        amap: list[list[str]] = []
        for r in range(2 + (height + ((height - 1) * vpad))):
            row: list[str] = []
            for c in range(2 + (width + ((width - 1) * hpad))):
                if not ((r % (vpad + 1) == 1) and (c % (hpad + 1) == 1)):
                    row.append(self.scaffolding)
                elif (self.tr([c, r]) in
                      [z.coords for z in self.map.get_zones()]):
                    color = [z for z in self.map.get_zones() if z.coords ==
                             self.tr([c, r])][0].color
                    zdrones = [len(z.drones) for z in self.map.get_zones()
                               if z.coords == self.tr([c, r])][0]
                    zdrones_digits = len(str(zdrones))
                    if (color in self.colors.keys()):
                        row.append(self.colors[color] + str(zdrones) + " " *
                                   (self.csize - zdrones_digits))
                    else:
                        row.append(self.colors["NOT_FOUND"] + str(zdrones) +
                                   " " * (self.csize - zdrones_digits))
                    self.raw_zones.append([c, r])
                    # print(f"{[self.tr([c,r])]} correlates to {[c,r]} ")
                else:
                    # check if this is part of a connection line
                    if (True):
                        row.append(self.scaffolding)
            amap.append(row)
        for cn in self.connections:
            origin = list(
                filter(
                    lambda x: self.tr(x) == cn.orig.coords, self.raw_zones))[
                    0]
            destination = list(
                filter(
                    lambda x: self.tr(x) == cn.dest.coords, self.raw_zones))[
                    0]
            self.raw_connections.append(
                [origin, destination, cn.drones.copy()])
        return (amap)

    @staticmethod
    def get_conn_coords(c: fi.Connection) -> list[tuple[int, int] | list[int]]:
        """Return a connection's origin and destination coordinates.

        Parameters
        ----------
        c : fi.Connection
            The connection to extract coordinates from.

        Returns
        -------
        list[tuple[int, int] | list[int]]
            A two-element list ``[origin_coords, dest_coords]``.
        """
        src_coord: tuple[int, int] | list[int] = c.orig.coords
        dest_coord: tuple[int, int] | list[int] = c.dest.coords
        return [src_coord, dest_coord]

    def tr(self, coords: list[int],
           direction: int = 0) -> list[int]:
        '''
        Transform function takes grid coordinates and translates
        them to logical coordinates when direction is 0, and the converse
        if direction is 1
        note: since the function is many-to-one in one direction there is no
        unique inverse

        Parameters
        ----------
        coords : list[int]
            An ``[x, y]`` coordinate pair to transform.
        direction : int, optional
            ``0`` to convert grid coordinates to logical (zone)
            coordinates; ``1`` for the (unimplemented) converse.
            Defaults to 0.

        Returns
        -------
        list[int]
            The transformed ``[x, y]`` coordinate pair when
            ``direction`` is 0. An empty list when ``direction`` is 1
            or any other value, since the inverse transform is not
            implemented (the mapping is many-to-one).
        '''
        if direction == 0:
            return [coords[0] // (self.hpad + 1), coords[1] // (self.vpad + 1)]
        if direction == 1:
            return []
        return []

    def print_grid(self, msg: str, delay: float = 1) -> None:
        """Clear the screen and render the current state of the map.

        Rebuilds the base grid, draws all connections, prints the
        resulting ANSI grid followed by ``msg``, and pauses for
        ``delay`` seconds.

        Parameters
        ----------
        msg : str
            A message (e.g. controls/help text or turn log) to print
            below the rendered grid.
        delay : float, optional
            Seconds to pause after printing. Defaults to 1.

        Returns
        -------
        None
        """
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
