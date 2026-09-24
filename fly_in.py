from enum import Enum
import os
import argparse


class InputFileError(Exception):
    """Exception raised when the input configuration file is malformed.

    Parameters
    ----------
    line : str | list[str] | None, optional
        The offending line (or lines) from the input file.
    line_nr : int | list[int] | None, optional
        The line number (or numbers) at which the error occurred.
    Message : str | None, optional
        A custom error message. If not provided, a message is generated
        from ``line`` and ``line_nr``.
    """

    def __init__(self, line: str | list[str] | None = None,
                 line_nr: int | list[int] | None = None,
                 Message: str | None = None) -> None:
        self.line_nr = line_nr
        self.line = line
        if Message is None:
            Message = f'Error in line {line_nr}: \'{line}\''
        super().__init__(Message)


class SemanticError(Exception):
    """Exception raised when the parsed map violates a semantic rule.

    Examples of semantic errors include an unreachable goal zone or a
    start/end zone whose capacity is lower than the number of drones.

    Parameters
    ----------
    Message : str | None, optional
        Description of the semantic error.
    """

    def __init__(self, Message: str | None = None) -> None:
        super().__init__(Message)


class Metadata(str, Enum):
    """Enumeration of the metadata keys allowed in the map config file.

    Attributes
    ----------
    ZONE : str
        Metadata key specifying a zone's type (see :class:`ZoneType`).
    COLOR : str
        Metadata key specifying a hub's display color.
    MAX_LINK_CAPACITY : str
        Metadata key specifying a connection's maximum drone capacity.
    MAX_DRONES : str
        Metadata key specifying a hub's maximum drone capacity.
    """

    ZONE = "zone"
    COLOR = "color"
    MAX_LINK_CAPACITY = "max_link_capacity"
    MAX_DRONES = "max_drones"


class ZoneType(Enum):
    """Enumeration of the possible types a :class:`Zone` can have.

    Attributes
    ----------
    NORMAL : int
        A regular zone with no special behavior.
    BLOCKED : int
        A zone that drones cannot enter or move through.
    RESTRICTED : int
        A zone that adds extra "distance" cost and locks drones while
        they occupy it.
    PRIORITY : int
        A zone that drones prefer to move through when routing toward
        the goal.
    """

    NORMAL = 0
    BLOCKED = 1
    RESTRICTED = 2
    PRIORITY = 3


class Map():
    """Represents the drone circuit map: its zones, connections and state.

    A ``Map`` is built from a parsed config (as produced by
    :func:`parse_config`) and exposes the simulation step
    (:meth:`new_turn`) used to advance drones toward the goal zone.

    Attributes
    ----------
    colors : list[str]
        Valid color names that can be assigned to a hub.
    move_count : int
        Class-level counter (currently unused at the class level; per-turn
        move counts are returned by :meth:`new_turn`).
    """

    colors: list[str] = ["NONE", "GREEN", "RED", "BLUE", "ORANGE",
                         "YELLOW", "CYAN", "PURPLE", "BROWN",
                         "LIME", "MAGENTA", "GOLD", "BLACK",
                         "MAROON", "DARKRED", "CRIMSON", "RAINBOW"]
    move_count: int = 0

    @staticmethod
    def hasPath(xs: list[tuple[int, int]], conn: tuple[int, int],
                counter: int = 0)\
            -> int:
        '''
        hasPath returns the number of intermediate vertices
        between two points if a path between nodes
        tuple[0] and tuple[1]
        exists, otherwise -1

        Parameters
        ----------
        xs : list[tuple[int, int]]
            The graph, expressed as a list of edges (node id pairs), to
            search through.
        conn : tuple[int, int]
            A pair ``(start_node, end_node)`` identifying the path to
            look for.
        counter : int, optional
            The accumulated number of hops taken so far (used internally
            for the recursion). Defaults to 0.

        Returns
        -------
        int
            The number of intermediate vertices on a path from
            ``conn[0]`` to ``conn[1]`` if one exists, otherwise -1.
        '''
        if (conn[0] == conn[1]):
            return counter
        xsf = [(n, m) for (n, m) in xs if n != conn[0]]
        return next((x for x in [
            Map.hasPath(xsf, (m, conn[1]), counter + 1)
            for (n, m) in xs if n == conn[0]] if x > 0), -1)

    def __init__(self,
                 pconfig: list[list[str] | list[list[list[str]]]] | None):
        """Build a Map from a parsed config, creating zones and connections.

        Parses the ``pconfig`` structure produced by :func:`parse_config`,
        populating ``self._zones`` with :class:`Zone` instances and wiring
        up :class:`Connection` objects between them. Also validates that
        the start/end zone capacities can hold the declared number of
        drones and that at least one path exists from the start zone to
        the goal zone.

        Parameters
        ----------
        pconfig : list[list[str] | list[list[list[str]]]] | None
            The parsed map configuration, as returned by
            :func:`parse_config`. If ``None``, an empty map is created
            (no zones, no connections).

        Raises
        ------
        SemanticError
            If the start or end zone's capacity is lower than the number
            of drones, or if there is no path from the start zone to the
            goal zone.
        """
        self._zones: list[Zone] = []
        self._dimensions: list[int] = [0, 0]
        self._drones: int = 0
        self._locked: list[tuple[str, Connection | Zone]] = []
        self._moved_drones: list[str] = []
        delta: int = 0
        '''
        delta denotes the y-axis offset caused by the weird negative index
        notation that was chosen for the map config files
        '''
        if pconfig is None:
            return
        for c in pconfig:
            meta: list[list[str]] = [
                [md.lower()] for md in Metadata.__members__ if
                md.lower() in c[1]]
            if ("nb_drones" in c[0]):
                if (type(c[1]) is str):
                    self.drones = int(c[1])
            if ('hub' in c[0].lower() if type(c[0]) is str else c[0]):
                # this branch of the if-else manages cases where we have
                # coordinates in the y-axis
                color: str = "NONE"
                if "color" in c[1]:
                    if type(c[1]) is str:
                        color = c[1].split("color=")[1].upper()
                    if len(color.split(" ")) == 1:
                        color = color.split("]")[0]
                    else:
                        color = color.split(' ')[0]
                    if color not in Map.colors:
                        color = Map.colors[0]
                if type(c[1]) is not str:
                    return
                if int(c[1].split(" ")[1:3][1]) < 0:
                    absolute: int = abs(int(c[1].split(" ")[1:3][1]))
                    if (absolute > delta):
                        for z in self._zones:
                            z.coords = [z.coords[0], z.coords[1] + absolute]
                    if ["max_drones"] in meta:
                        md: str = c[1].split("max_drones=")[1]
                        md = md.split("]")[0] if ']' in\
                            md else md.split(' ')[0]
                    if ['zone'] in meta:
                        zsplit: str = c[1].split("zone=")[1]
                        zone_md = zsplit.split(" ")[0]\
                            if len(zsplit.split(" ")) > 1\
                            else zsplit.split("]")[0]
                    if type(c[0]) is not str:
                        return
                    self._zones.append(
                        Zone(
                            name := c[1].split(" ")[0],
                            c[0], self,
                            tmp := [
                                c[1].split(" ")[1], '0' if
                                absolute > delta else
                                str(delta-absolute)],
                            color=color,
                            capacity=int(md) if ["max_drones"] in meta
                            else 1 if name != 'start' and name != 'goal'
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
                        drones_md: str = c[1].split("max_drones=")[1]
                        drones_md = drones_md.split("]")[0] if ']' in\
                            drones_md else md.split(' ')[0]
                    zone_md = "NORMAL"
                    if ['zone'] in meta:
                        zsplit = c[1].split("zone=")[1]
                        zone_md = zsplit.split(" ")[0]\
                            if len(zsplit.split(" ")) > 1\
                            else zsplit.split("]")[0]
                    if (type(c[0]) is not str):
                        return
                    self._zones.append(
                        Zone(name := c[1].split(" ")[0],
                             c[0], self,
                             tmp,
                             color=color,
                             capacity=int(drones_md)
                             if ["max_drones"] in meta
                             else 1 if name != 'start' and name != 'goal'
                             else -1,
                             type=ZoneType.__members__.get(
                                zone_md.upper(), ZoneType.NORMAL).name,
                             drones=self.drones if name == "start" else 0))
                if (int(tmp[0]) > self._dimensions[0]):
                    self._dimensions[0] = int(tmp[0])
                if (int(tmp[1]) > self._dimensions[1]):
                    self._dimensions[1] = int(tmp[1])
            if type(c[0]) is not str or type(c[1]) is not str:
                return
            if (c[0].lower() == "connection"):
                origen: str = c[1].split("-")[0]
                destination: str = dst\
                    if len((dst := c[1].split("-")[1]).split("[")) == 1\
                    else dst.split(" [")[0]
                mlc: int = 1
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
            if (int(z.coords[0]) + 1 > self._dimensions[0]):
                self._dimensions[0] = int(z.coords[0]) + 1
            if (int(z.coords[1]) + 1 > self._dimensions[1]):
                self._dimensions[1] = int(z.coords[1]) + 1
        if (self.drones > (cap := [z for z in self._zones
                           if z.if_name == 'start_hub'][0].capacity)
                and cap > -1):
            raise SemanticError("The capacity of the start zone"
                                " can't be lower than the number of drones in "
                                "the circuit")
        if (self.drones > (cap := [z for z in self._zones
                           if z.if_name == 'end_hub'][0].capacity)
                and cap > -1):
            raise SemanticError("The capacity of the end zone"
                                " can't be lower than the number of drones in "
                                "the circuit")
        start: Zone | None = self.get_zone('start')
        goal: Zone | None = self.get_zone('goal')
        assert start is not None
        assert goal is not None
        if Map.hasPath(
                    self.get_graph(),
                    (start.node(self),
                     goal.node(self))) == -1:
            raise SemanticError(Message='There must be at least one path'
                                'from start zone to goal zone')

    def move(self, z1: "Zone | Connection",
             z2: "Zone | Connection", d: str) -> str:
        """Move a single drone from one map element to another.

        Validates that ``z1`` and ``z2`` belong to the map, that drone
        ``d`` is currently located at ``z1``, and that a connection from
        ``z1`` to ``z2`` exists, before moving the drone.

        Parameters
        ----------
        z1 : Zone | Connection
            The zone or connection the drone is currently occupying.
        z2 : Zone | Connection
            The zone or connection the drone is being moved into.
        d : str
            The identifier of the drone to move.

        Returns
        -------
        str
            A string of the form ``"<drone>-<destination_name>"``
            describing the move that was made.

        Raises
        ------
        Exception
            If ``z1``/``z2`` are not part of the map, drone ``d`` is not
            at ``z1``, or there is no connection from ``z1`` to ``z2``.
        """
        # check that z1, z2, and d exist.
        elements = {
            *self.get_zones(),
            *self.get_connections(),
            *z1.drones,
        }
        if ({z1, z2, d} & elements == {z1, z2, d}
                and (z2 in
                     [(c.dest if type(c) is Connection else c)
                      for c in z1.get_connections()]
                     or (isinstance(z2, Connection))
                     and z2 in z1.get_connections())):
            # check that the amount of drones moved through
            # the connection so far is lower than the connection's capacity.
            if type(z2) is Connection:
                if len(z2.drones) < z2.dest.capacity:
                    z1.drones.remove(d)
                    z2.drones.append(d)
            else:
                z1.drones.remove(d)
                z2.drones.append(d)
            return (f"{d}-{z2.name}")
        else:
            raise Exception(
                f'''\x1b[43mMap.move ERROR:\nOne of the following is\
 not true:
            Both zones are in the map
            '{d}' is in {z1.name}
            There is a connection from '{z1.name}'\
to '{z2.name}'\x1b[0m''')

    def get_zones(self, only_occupied: bool = False) -> list["Zone"]:
        """Return the list of zones in the map.

        Parameters
        ----------
        only_occupied : bool, optional
            If ``True``, only return zones that currently contain at
            least one drone. Defaults to ``False``.

        Returns
        -------
        list[Zone]
            The requested list of zones.
        """
        if not only_occupied:
            return self._zones
        return [z for z in self.get_zones() if len(z.drones) > 0]

    def get_connections(
            self,
            only_occupied: bool = False) -> list["Connection"]:
        """Return the list of connections between all zones in the map.

        Parameters
        ----------
        only_occupied : bool, optional
            Currently unused; present for API symmetry with
            :meth:`get_zones`. Defaults to ``False``.

        Returns
        -------
        list[Connection]
            All connections belonging to every zone in the map.
        """
        return [c for z in self._zones for c in z.get_connections()]

    def get_zone(self, name: str) -> "Zone | None":
        """Look up a zone by name (case-insensitive).

        Parameters
        ----------
        name : str
            The name of the zone to find.

        Returns
        -------
        Zone | None
            The matching zone, or ``None`` if no zone with that name
            exists.
        """
        found_zone = [z for z in self.get_zones() if z.name == name.lower()]
        if len(found_zone) == 1:
            return found_zone[0]
        return None

    # def get_graph(self) -> list[tuple[int, int]]:
    #     vertices: list[tuple[int, int]] = []
    #     for zi in range(len(self._zones)):
    #         for c in [z
    #                   for z in
    #                   self._zones[zi].get_connections()
    #                   if z.dest.type != 'BLOCKED']:
    #             if (self._zones.index(c.orig) < self._zones.index(c.dest)):
    #                 vertices.append(
    #                   (self._zones.index(c.orig), self._zones.index(c.dest)))
    #     return (vertices)
    def get_graph(self) -> list[tuple[int, int]]:
        '''
        get_graph returns a graph that the function hasPath understands,
        to calculate paths for each drone each turn. It omits BLOCKED zones
        and it expands RESTRICTED zones to account for their cost, translated
        as distance.

        Returns
        -------
        list[tuple[int, int]]
            A list of edges (as zone-index pairs) representing the map's
            connections. Connections into a RESTRICTED zone are split into
            two edges via a synthetic intermediary node so that entering a
            RESTRICTED zone costs an extra hop in :meth:`Map.hasPath`.
        '''
        vertices: list[tuple[int, int]] = []
        next_node = len(self._zones)

        for zi in range(len(self._zones)):
            for c in [
                z for z in self._zones[zi].get_connections()
                if z.dest.type != 'BLOCKED'
            ]:
                orig = self._zones.index(c.orig)
                dest = self._zones.index(c.dest)

                if orig < dest:
                    if c.dest.type == 'RESTRICTED':
                        intermediary = next_node
                        next_node += 1

                        vertices.append((orig, intermediary))
                        vertices.append((intermediary, dest))
                    else:
                        vertices.append((orig, dest))

        return vertices

    def comes_before(self, z1: "Zone", z2: "Zone") -> bool:
        goal_zone: Zone | None = self.get_zone("goal")
        if (type(z1) is not Zone or type(z2) is not Zone)\
                or goal_zone is None:
            return False
        steps_z1: int = Map.hasPath(
            self.get_graph(),
            (z1.node(self), goal_zone.node(self))
        )
        steps_z2: int = Map.hasPath(
            self.get_graph(),
            (z2.node(self), goal_zone.node(self))
        )
        return True if steps_z1 > steps_z2 else False

    def new_turn(self) -> tuple[int, int, list[str]]:
        '''
        next_turn runs the next simulation turn
        returns True when all drones reached goal
        False otherwise

        Advances the simulation by one turn: first flushes any drones
        that were locked in a RESTRICTED zone and have since become free
        to continue, then repeatedly moves every occupied zone's drones
        one step closer to the goal (preferring PRIORITY zones, then
        normal zones, then RESTRICTED zones which get locked) until no
        further moves are possible in this turn.

        Returns
        -------
        tuple[int, int, list[str]]
            A 3-tuple of:

            - ``move_count`` (int): the number of drone moves made this
              turn.
            - ``finished`` (int): ``1`` if the simulation is finished
              (either all drones reached the goal, or no more moves are
              possible), ``0`` otherwise.
            - ``tdata`` (list[str]): a log of the individual moves made
              this turn, formatted as ``"<drone>-<destination>"`` strings.
        '''
        def compare_path_lengths(
                graph: list[tuple[int, int]],
                orig: int,
                next_forward: list[Zone]) -> Zone:
            """Pick the candidate zone with the shortest path to the goal.

            Parameters
            ----------
            graph : list[tuple[int, int]]
                The graph (as returned by :meth:`Map.get_graph`) to
                compute path lengths on.
            orig : int
                The node id of the zone the drone is currently in
                (currently unused directly, kept for context).
            next_forward : list[Zone]
                Candidate zones to move into.

            Returns
            -------
            Zone
                The candidate zone in ``next_forward`` with the shortest
                path to the goal zone.
            """
            steps: list[tuple[Zone, int]] = []
            for z in next_forward:
                if goal_zone is not None:
                    steps.append((z, Map.hasPath(
                        graph,
                        (z.node(self), goal_zone.node(self)))))
            closest_zone: Zone = min(steps, key=lambda x: x[1])[0]
            return closest_zone

        move_count: int = 0
        moved_drones: list[tuple[str, Connection]] = []
        move_flag: bool = True
        tdata: list[str] = []
        if (self.get_zone("impossible_goal")):
            goal_zone: Zone | None = self.get_zone("impossible_goal")
            if goal_zone is not None:
                if len(goal_zone.drones) == self.drones:
                    return (move_count, 1, tdata)
        else:
            goal_zone = self.get_zone("goal")
            if goal_zone is not None:
                if len(goal_zone.drones) == self.drones:
                    return (move_count, 1, tdata)
        # flushing locked drones entering into restricted zones
        for d in self._locked.copy():
            conn: Connection = [
                z for z in (self.get_connections())
                if d[0] in z.drones][0]
            result: str | None = self.move(conn, d[1], d[0])
            if result is not None:
                tdata.append(result)
                moved_drones.append((d[0], conn))
                conn.transits += 1
                self._locked.remove((d[0], d[1]))
                move_count += 1

        # as long as there are moved drones keep checking if zones have been
        # unlocked making more moves are possible, same structureas bubble sort
        while (move_flag):
            move_flag = False
            for z in self.get_zones(only_occupied=True):
                # here i use a copy of the list of drones because the list
                # itself can change during iteration, causing elements to be
                # skipped
                for dr in z.drones.copy():
                    if goal_zone is None:
                        continue
                    next_forward_priority: list[Zone] = [
                        nxtzone for nxtzone in z.possible_moves()
                        if (step_count := Map.hasPath(
                            self.get_graph(),
                            (nxtzone.node(self), goal_zone.node(self))))
                        < Map.hasPath(self.get_graph(),
                                      (z.node(self), goal_zone.node(self)))
                        and step_count != -1
                        and nxtzone.type == "PRIORITY"]
                    next_forward: list[Zone] = [
                        nxtzone for nxtzone in z.possible_moves()
                        if (step_count := Map.hasPath(
                            self.get_graph(),
                            (nxtzone.node(self), goal_zone.node(self))))
                        < Map.hasPath(self.get_graph(),
                                      (z.node(self), goal_zone.node(self)))
                        and step_count != -1
                        and nxtzone.type != "RESTRICTED"]
                    next_forward_restricted: list[Zone] = [
                        nxtzone for nxtzone in z.possible_moves()
                        if (step_count := Map.hasPath(
                            self.get_graph(),
                            (nxtzone.node(self), goal_zone.node(self))))
                        < Map.hasPath(self.get_graph(),
                                      (z.node(self), goal_zone.node(self)))
                        and step_count != -1
                        and nxtzone.type == "RESTRICTED"]

                    if len(next_forward_priority) > 0 and dr\
                            not in [md[0] for md in moved_drones]:
                        result = self.move(z, compare_path_lengths(
                            self.get_graph(), z.node(self),
                            next_forward_priority), dr)
                        conn = [
                            c for c in z.get_connections()
                            if c.dest == next_forward_priority[0]][0]
                        if result is not None:
                            tdata.append(result)
                            conn.transits += 1
                        move_flag = True
                        moved_drones.append((dr, conn))
                        move_count += 1

                    elif len(next_forward) > 0 and dr\
                            not in [md[0] for md in moved_drones]:
                        result = self.move(z, compare_path_lengths(
                            self.get_graph(),
                            z.node(self), next_forward), dr)
                        # result = m.move(z, next_forward[0], dr)
                        conn = [
                            c for c in z.get_connections()
                            if c.dest == next_forward[0]][0]
                        if result is not None:
                            tdata.append(result)
                            conn.transits += 1
                        move_flag = True
                        moved_drones.append((dr, conn))
                        move_count += 1

                    elif len(next_forward_restricted) > 0 and dr\
                            not in [md[0] for md in moved_drones]:
                        rdest = next_forward_restricted[0]
                        conn = [
                            c for c in z.get_connections()
                            if c.dest == next_forward_restricted[0]][0]
                        result = self.move(z, conn, dr)
                        if result is not None:
                            self._locked.append((dr, rdest))
                            moved_drones.append((dr, conn))
                            tdata.append(f"{dr}-{z.name}-{rdest.name}")
                            conn.transits += 1
                            move_flag = True
                            move_count += 1
        if goal_zone is not None:
            if len(goal_zone.drones) == self.drones:
                return (move_count, 1, tdata)
            if (move_count == 0):
                return (move_count, 1, tdata)
            for c in [c for c in self.get_connections() if c.transits > 0]:
                c.transits = 0
        return (move_count, 0, tdata)


class Zone():
    """Represents a single zone (hub) on the map.

    A zone has a name, coordinates, a type (see :class:`ZoneType`), an
    optional drone capacity, and a set of outgoing :class:`Connection`
    objects to neighboring zones.
    """

    def __init__(self, name: str, if_name: str, map: Map,
                 coords: tuple[str, str] | list[str],
                 type: str = 'NORMAL',
                 color: str = "NONE",
                 capacity: int = -1,
                 drones: int = 0):
        """Initialize a Zone.

        Parameters
        ----------
        name : str
            The zone's display/config name (e.g. ``"start"``, ``"goal"``).
        if_name : str
            The interface/role name of the zone as declared in the config
            file (e.g. ``"start_hub"``, ``"end_hub"``).
        coords : tuple[str, str] | list[str]
            The zone's ``(x, y)`` coordinates, as strings, converted to
            ``int`` internally.
        type : str, optional
            The zone's type name, matching a member of :class:`ZoneType`.
            Defaults to ``'NORMAL'``.
        color : str, optional
            The zone's display color. Defaults to ``"NONE"``.
        capacity : int, optional
            The maximum number of drones the zone can hold at once, or
            ``-1`` for unlimited. Defaults to ``-1``.
        drones : int, optional
            The number of drones to pre-populate the zone with (used for
            the start zone). Defaults to 0.
        """
        self.if_name: str = if_name
        self.name: str = name
        self.coords: tuple[int, int] | list[int] = [int(x) for x in coords]
        self.type = type
        self.color = color
        self._connections: list[Connection] = []
        self.drones: list[str] = []
        self.capacity: int = capacity
        self.map = map
        for dn in range(drones):
            self.drones.append("D"+str(dn))

    def set_connection(self, dest: "Zone", capacity: int = -1) -> None:
        """Create and register a connection from this zone to another.

        Parameters
        ----------
        dest : Zone
            The destination zone to connect to.
        capacity : int, optional
            The maximum number of drones that may transit the connection
            at once. Defaults to -1.

        Returns
        -------
        None
        """
        self._connections.append(Connection(
            self, dest, max_capacity=capacity))

    def get_connections(self) -> list["Connection"]:
        """Return this zone's outgoing connections.

        Returns
        -------
        list[Connection]
            The list of connections originating from this zone.
        """
        return (self._connections)

    def node(self, m: "Map") -> int:
        '''
        returns the numeric id of the node
        that represents this zone in the graph
        that represents map m

        Parameters
        ----------
        m : Map
            The map this zone belongs to.

        Returns
        -------
        int
            The index of this zone within ``m``'s zone list.
        '''
        return m.get_zones().index(self)

    def available(self) -> bool:
        """Check whether this zone can currently accept another drone.

        Returns
        -------
        bool
            ``False`` if the zone is BLOCKED or already at capacity,
            ``True`` otherwise.
        """
        if (self.type == "BLOCKED"):
            return False
        if (self.type == 'RESTRICTED'):
            inc_conns: list[Connection] = [
                c for c in self.get_connections() if
                self.map.comes_before(c.dest, self)]
            for i in range(len(inc_conns)):
                inc_conns[i] = [c for c in inc_conns[i].dest.get_connections()
                                if c.orig == inc_conns[i].dest and
                                c.dest == inc_conns[i].orig][0]
            total_expected: int = sum(map(lambda x: len(x.drones), inc_conns))
            if not total_expected < (self.capacity - len(self.drones)):
                return False
        if (self.capacity == -1 or
                len(self.drones) < self.capacity):
            return True
        # here we manage the case where a restricted zone
        # has more than one incoming connection and must
        # not leave drones waiting in any of them.
        # Availability will reflect not only current occupancy
        # but also expected occupancy by counting the number of
        # drones in incoming connections!
        return False

    def possible_moves(self) -> list["Zone"]:
        """Return the neighboring zones a drone here could move into.

        A neighbor is a valid move target if both the connection to it
        and the neighbor zone itself are available (not blocked/full).

        Returns
        -------
        list[Zone]
            The list of zones reachable in one hop from this zone.
        """
        available: list[Zone] = []
        # for c in self.get_connections():
        #     conn_av = c.available()
        for c in self.get_connections():
            if c.dest.available() and c.available():
                available.append(c.dest)
        # [available.append(c.dest) for c in self.get_connections() if
        #  c.dest.available() and c.available()]
        return available

    def show(self, mode: int = 0) -> str:
        """Build a human-readable, ANSI-colored summary of this zone.

        Parameters
        ----------
        mode : int, optional
            Display mode. ``0`` (the default) returns a detailed
            multi-line summary; any other value returns an empty string.

        Returns
        -------
        str
            The formatted summary string.
        """
        if mode == 0:
            return f"""\x1b[46m\n\n\t{self.name}:
\t\tCoordinates: {self.coords}
\t\tType: {self.type}
\t\tDrones: \n\t\t\t{(chr(10) + (chr(9) * 3)).join([d for d in self.drones])}
\t\tConnections: \n\t\t\t{(chr(10) + (chr(9) * 3)).join([c.show()
                                                         for c in
                                                         self._connections])}
\t\tColor: {self.color}\n\x1b[0m
"""
        else:
            return ''


class Connection():
    """Represents a directed connection (edge) between two zones."""

    def __init__(self, orig: Zone, dest: Zone,
                 max_capacity: int = 1):
        """Initialize a Connection.

        Parameters
        ----------
        orig : Zone
            The zone the connection originates from.
        dest : Zone
            The zone the connection leads to.
        max_capacity : int, optional
            The maximum number of drones that may transit this
            connection at once. Defaults to 1.
        """
        self.orig: Zone = orig
        self.dest: Zone = dest
        self.name = f"{self.orig.name}-{self.dest.name}"
        self.drones: list["str"] = []
        self.transits: int = 0
        self.capacity: int = max_capacity
        self.used: bool = False

    def get_connections(self) -> list[Zone]:
        """Return the destination zone as a single-element list.

        Provided so a :class:`Connection` can be treated similarly to a
        :class:`Zone` when checking possible next hops.

        Returns
        -------
        list[Zone]
            A single-element list containing ``self.dest``.
        """
        return [self.dest]

    def available(self) -> bool:
        """Check whether this connection has spare capacity.

        Returns
        -------
        bool
            ``True`` if the number of drones currently transiting plus
            those already queued is below ``self.capacity``, ``False``
            otherwise.
        """
        if self.transits + len(self.drones) < self.capacity:
            return True
        return False

    def show(self) -> str:
        """Build a human-readable summary of this connection.

        Returns
        -------
        str
            A string of the form ``"<origin> <=> <destination>"``.
        """
        return f"{self.orig.name} <=> {self.dest.name}"


def parse_config(file: str) -> list[list[str] | list[list[list[str]]]]:
    """Parse and validate the contents of a map configuration file.

    Splits the raw file content into ``key: value`` pairs, validates
    hub, connection, and metadata syntax, and enforces map-level rules
    (exactly one ``start_hub`` and one ``end_hub``, unique zone names and
    coordinates, etc.).

    Parameters
    ----------
    file : str
        The raw text content of the map configuration file.

    Returns
    -------
    list[list[str] | list[list[list[str]]]]
        The parsed configuration, as a list of ``[key, value]`` pairs,
        ready to be passed to :class:`Map`.

    Raises
    ------
    InputFileError
        If the file is malformed or violates any validation rule (e.g.
        missing ``nb_drones`` line, invalid metadata, duplicate zone
        names, missing/duplicate start or end hub, etc.).
    """
    def validate_md(meta: str, type: str) -> None:
        """Validate one or more space-separated ``key=value`` metadata items.

        Parameters
        ----------
        meta : str
            The metadata substring to validate (may contain multiple
            space-separated ``key=value`` entries).
        type : str
            The kind of element the metadata belongs to, either
            ``'hub'`` or ``'connection'``, which determines which
            metadata keys are permitted.

        Returns
        -------
        None

        Raises
        ------
        InputFileError
            If the metadata is malformed, references an unknown
            property, or uses a property not valid for ``type``.
        """
        if (ml := len(meta.split(' '))) == 1:
            metas = meta.split('=')
            if (len(metas) != 2):
                raise InputFileError(
                    cline,
                    cline_nr,
                    Message='Metadata must be specified '
                    'as \'<property>=<value>\'')
            try:
                Metadata[metas[0].upper()]
            except KeyError:
                raise InputFileError(
                    cline,
                    cline_nr,
                    Message=f'\'{metas[0].upper()}\''
                    'is not a valid property.\n'
                    f'Valid properties: {list(Metadata.__members__.keys())}')
            if type.lower() == 'hub':
                if meta[0].lower() == 'max_link_capacity':
                    raise InputFileError(
                        cline,
                        cline_nr,
                        Message='MAX_LINK_CAPACITY is not a property of hubs')
                if metas[0].lower() == 'zone' and\
                        metas[1].upper()\
                        not in list(ZoneType.__members__.keys()):
                    raise InputFileError(
                        cline,
                        cline_nr,
                        Message=f'\'{metas[1]}\' is not a valid Zone type.\n'
                        f'Zone types: {list(ZoneType.__members__.keys())}')
                if metas[0].lower() == 'max_drones':
                    try:
                        value: int = int(metas[1])
                        if value < 1:
                            raise InputFileError(
                                cline,
                                cline_nr,
                                Message='max_drones should be positive')
                    except Exception:
                        raise InputFileError(
                            cline,
                            cline_nr,
                            Message='max_drones should be a positive integer')
            if type.lower() == 'connection':
                if metas[0].lower() != 'max_link_capacity':
                    raise InputFileError(
                        cline,
                        cline_nr,
                        Message='Connections can only have MAX_LINK_CAPACITY'
                        ' as a property.')
                if metas[0].lower() == 'max_link_capacity':
                    try:
                        value = int(metas[1])
                        if value < 1:
                            raise InputFileError(
                                cline,
                                cline_nr,
                                Message='max_link_capacity should be positive')
                    except Exception:
                        raise InputFileError(
                            cline,
                            cline_nr,
                            Message='max_link_capacity should be an integer')
        elif ml > 1:
            for p in meta.split(' '):
                validate_md(p, type)

    def validate_hub(line: str, line_nr: int) -> None:
        """Validate the syntax of a single hub declaration line.

        Parameters
        ----------
        line : str
            The full ``key: value`` line declaring the hub.
        line_nr : int
            The 1-based line number of ``line`` in the source file, used
            for error reporting.

        Returns
        -------
        None

        Raises
        ------
        InputFileError
            If the line is missing its value, the zone name contains
            dashes or spaces, the coordinates are not integers, or any
            embedded metadata is invalid.
        """
        splat: list[str] = line.split(": ")
        if (len((m := splat[1].split('['))) > 1):
            meta: str = m[1][:-1]
            validate_md(meta, 'hub')
        if len(splat) < 2:
            raise InputFileError(line, line_nr, "Missing semicolon")
        spl = spl[:-1] if (spl := splat[1].split('[')[0])[-1] == ' ' else spl
        if (len((splspl := spl.split(' '))) != 3):
            if all(list(map(lambda x: x.isdigit(), splspl[-2:]))):
                raise InputFileError(line, line_nr, "Zone names must"
                                     " not contain dashes or spaces")
            raise InputFileError(line, line_nr,
                                 "Malformed line! Correct form:\n"
                                 "hub: <str> <int> <int>")
        if ('-' in spl.split(' ')[0]):
            raise InputFileError(line, line_nr, "Zone names must not contain"
                                 " dashes or spaces")
        try:
            int(splat[1].split(' ')[1])
            int(splat[1].split(' ')[2])
        except ValueError:
            raise InputFileError(line, line_nr, "Zone coordinates must "
                                 "be integers")

    def validate_connection(line: str, line_nr: int, zones: list[str],
                            conns: list[str]) -> None:
        """Validate the syntax and uniqueness of a connection declaration.

        Parameters
        ----------
        line : str
            The full ``key: value`` line declaring the connection.
        line_nr : int
            The 1-based line number of ``line`` in the source file, used
            for error reporting.
        zones : list[str]
            The names of all zones declared elsewhere in the file, used
            to verify the connection references existing zones.
        conns : list[str]
            The raw values of all connection declarations seen so far,
            used to detect duplicate (including reversed) connections.

        Returns
        -------
        None

        Raises
        ------
        InputFileError
            If either endpoint zone does not exist, the reverse
            connection already exists, or any embedded metadata is
            invalid.
        """
        conn: str = line.split(": ")[1].split(" [")[0]
        src: str
        dst: str
        src, dst = conn.split('-')
        converse_conn: str = dst + '-' + src
        # first check that connected zones exist
        if (src not in zones or dst not in zones):
            raise InputFileError(
                line, line_nr,
                Message="Connections must connect existing zones"
            )
        # second, check if there are equivalent connections
        if (converse_conn in conns):
            raise InputFileError(
                line, line_nr, Message="There must not be any "
                "duplicate connections"
            )
        if (len((md := line.split('['))) == 2):
            validate_md(md[1][:-1], 'connection')
    result: list[list[str] | list[list[list[str]]]] = []
    splat: list[str] = file.split("\n")
    splat = [s for s in splat if not s.startswith("#")]
    result.extend(
        [[s[0], s[1]] for s in
         [ss.split(": ") for ss in splat if len(ss.split(": ")) == 2]])
    if result[0][0] != 'nb_drones':
        raise InputFileError(
            '',
            1,
            Message="The first line of the input file must specify the "
            "number of drones in the circuit: 'nb_drones: <int>'"
        )
    sh_count: int = 0
    eh_count: int = 0
    for i in range(len(result)):
        r: str | list[list[str]] = result[i][0]
        rr: str | list[list[str]] = result[i][1]
        if type(r) is str and type(rr) is str:
            cline: str = r + ': ' + rr
        cline_nr: int = file.split("\n").index(cline) + 1
        if (i == 0):
            if (result[i][0] == 'nb_drones'):
                try:
                    if type(rr) is str:
                        int(rr)
                except ValueError:
                    raise InputFileError(
                        cline,
                        cline_nr,
                        Message='nb_drones must be assigned a positive ' +
                        'integer')

                if (type(res := result[i][1]) is str and int(res) < 1):
                    raise InputFileError(
                        cline,
                        cline_nr,
                        Message='nb_drones must be assigned a positive ' +
                        'integer')
        if 'hub' in result[i][0]:
            validate_hub(cline, cline_nr)
        if 'connection' in result[i][0]:
            validate_connection(
                cline,
                cline_nr,
                [z[1].split(' ')[0]
                 for z in result[1:]
                 if z[0] != 'connection' and isinstance(z[1], str)
                 and isinstance(z[1], str)],
                [cs[1] for cs in result if isinstance(cs[1], str)
                 and cs[0] == 'connection']
            )
            # validate_connection(cline,
            #                     cline_nr,
            #                     [z[1].split(' ')[0]
            #                      for z in result[1:]
            #                      if z[0] != 'connection'],
            #                   [cs for cs in result if cs[0] == 'connection'])
        if result[i][0] == 'start_hub':
            sh_count += 1
        if result[i][0] == 'end_hub':
            eh_count += 1
    if (sh_count != 1):
        raise InputFileError(
            cline,
            cline_nr,
            Message='There must be exactly one \'start_hub\':' +
            f'\n\'{cline}\'')
    if (eh_count != 1):
        raise InputFileError(
            str(file.split("\n").index(cline) + 1),
            Message='There must be exactly one \'end_hub\':' +
            f'\n\'{cline}\'')
    for i in range(1, len(result)):
        for resu in result[i+1:]:
            n1: str | None = rrr.split(' ')[0] if\
                type(rrr := result[i][1]) is str else None
            n2: str | None = rrrr.split(' ')[0] if type(rrrr := resu[1])\
                is str else None
            if n1 == n2:
                lst: list[str] = file.split('\n')
                if n1 is None:
                    continue
                lines: list[tuple[str, int]] = [
                    (li, lst.index(li) + 1)
                    for li in file.split('\n')
                    if (' ' + n1 + ' ') in li or (' ' + n1 + '') in li]
                raise InputFileError(
                    lines[0][0],
                    lines[0][1],
                    Message="Zone names and connections must be unique")
            value = result[i][1]
            other_value = r[1]
            if not isinstance(value, str):
                continue
            if not isinstance(other_value, str):
                continue
            c1: list[str] = value.split(' ')[1:3]
            c2: list[str] = other_value.split(' ')[1:3]
            if c1 and c1 == c2 and not c1[0].startswith("["):
                lst = file.split('\n')
                if n1 is None:
                    continue
                lines = [
                    (li, lst.index(li) + 1)
                    for li in file.split('\n')
                    if (' ' + n1 + ' ') in li or (' ' + n1 + '') in li]
                raise InputFileError(
                    lines[0][0],
                    lines[0][1],
                    Message="Zones must have different coordinates")
    return (result)


def main() -> None:
    """Run the drone simulation CLI: select a map, then step turns
    interactively.

    Parses the ``--map`` command-line argument (or prompts interactively
    via :func:`select_map` if not given), builds a :class:`Map`, and then
    loops calling :meth:`Map.new_turn`, rendering the grid after each
    turn and prompting the user for the next command (run, next turn,
    select a new map, or quit) until the simulation finishes. The move
    log for the whole run is written to ``output.txt``.

    Returns
    -------
    None
    """
    import graphics

    def select_map() -> list[list[str] | list[list[list[str]]]] | None:
        """Interactively prompt the user to pick a map file from ``maps/``.

        Prints a title banner and a listing of available map files (grouped
        by subdirectory), reads the user's numeric choice from stdin, then
        parses the chosen file via :func:`parse_config`.

        Returns
        -------
        list[list[str] | list[list[list[str]]]] | None
            The parsed map configuration for the chosen file, or ``None`` if
            the chosen file failed to parse (an :class:`InputFileError` was
            caught and reported).
        """
        CLEAR_SCREEN: str = '\x1b[2J\x1b[H'
        TITLE: str = '''
    ███████╗██╗  ██╗   ██╗       ██╗███╗   ██╗
    ██╔════╝██║  ╚██╗ ██╔╝       ██║████╗  ██║
    █████╗  ██║   ╚████╔╝        ██║██╔██╗ ██║
    ██╔══╝  ██║    ╚██╔╝         ██║██║╚██╗██║
    ██║     ███████╗██║          ██║██║ ╚████║
    ╚═╝     ╚══════╝╚═╝          ╚═╝╚═╝  ╚═══╝
    '''
        print(CLEAR_SCREEN)
        print('\x1b[36m'+TITLE+'\x1b[0m')
        print("\x1b[42m\n")
        print("Hello please pick a map\n\x1b[0m")
        file_index: list[list[str]] = []
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
        choice = input("\n## ")
        if choice.upper() == 'Q':
            exit()
        if (choice not in [i[0] for i in file_index]):
            print('\x1b[0m')
            return select_map()
        with open('maps/'+[m[1] for m in file_index if m[0] == choice][0])\
                as file:
            print('\x1b[0m')
            try:
                pconfig: list[list[str]
                              | list[list[list[str]]]] = parse_config(
                    file.read())
            except InputFileError as e:
                if e.line is not None:
                    print(f"\x1b[30m\x1b[43mInputFileError:\n{e}\n"
                          f"(Line {e.line_nr}): \'{e.line}\'\x1b[0m")
                else:
                    print(f"\x1b[30m\x1b[43mInputFileError:\n{e}")
                return None
        return pconfig

    def run_map(pconfig: list[list[str] | list[list[list[str]]]] | None)\
            -> int | None:
        try:
            mm: Map = Map(pconfig)
        except SemanticError as e:
            print(f"\x1b[43mSemanticError:\n{e}\n")
            exit()
        g: graphics.Grid = graphics.Grid(mm, 3, vpad=5, hpad=5)
        msg = "\nR: run simulation\nN: next turn\nS: select map\nQ: quit"
        g.print_grid(msg, delay=0.3)
        cmd: str = prompt()
        turn: int = 0
        finished: int
        tdata: list[str]
        output_f: str = ""
        while (True):
            if (cmd == 'S'):
                return None
            tmoves, finished, tdata = mm.new_turn()
            output_f += (" ".join(tdata) + '\n').replace('  ', ' ')
            g = graphics.Grid(mm, 3, vpad=5, hpad=5)
            g.print_grid(
                msg + f'\n\n─── Turn {turn} ───\n' + '\n'.join(tdata) +
                '\n──────────────')
            if (cmd not in 'R'):
                cmd = prompt()
            if (finished):
                break
            turn += 1
        with open("output.txt", 'w') as file:
            file.write(output_f)
        print("\n\x1b[42m\x1b[30mSimulation finished successfully!\x1b[0m\n")
        print(f"Total number of turns: {turn+1}")
        cmd = prompt()
        return turn+1 if cmd.upper() in ['R', 'N'] else None

    def prompt() -> str:
        """Read and normalize a single command from the user.

        Returns
        -------
        str
            ``"S"`` to select a new map, or the uppercased command
            string otherwise. Calls ``exit()`` directly if the user
            enters ``Q``.
        """
        cmd: str = input("\n## ")
        if (cmd.upper() == 'Q'):
            exit()
        if (cmd.upper() not in ['N', 'R', 'S']):
            return prompt()
        return cmd.upper()
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", type=str)
    args = parser.parse_args()
    if args.map is not None:
        try:
            with open('maps/'+args.map) as file:
                print('\x1b[0m')
                pconfig: \
                    list[list[str] | list[list[list[str]]]] | \
                    None = parse_config(
                        file.read())
        except Exception:
            print("Map does not exist!\nExample: python3 fly_in.py --map "
                  "easy/linear_path.txt'")
            exit()
    else:
        pconfig = select_map()
        if pconfig is None:
            exit(-1)
        while (run_map(pconfig) is None):
            pconfig = select_map()


if __name__ == "__main__":
    main()
