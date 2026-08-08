import fly_in as fi


def render_base(width: int, height: int) -> list[list[str]]:
    empty_cell: str = '\x1b[90m\x1b[100m▄▄▄▄\x1b[0m'
    amap: list[list[str]] = []
    for r in range(width):
        row: list[str] = []
        for c in range(height):
            row.append(empty_cell)
        amap.append(row)
    return (amap)


def render_zones(amap: list[list[str]], zones: list[fi.Map.Zone]) -> None:
    zone: str = '\x1b[40m\x1b[100m█\x1b[47m3\x1b[90m██\x1b[0m'
    connectors: list[str] = ["─", "│", "┌", "┐", "└",  "┘"]
    for row in [i for i in range(len(amap)) if i % 2 == 1]:
        for cell in [c for c in range(len(amap[0])) if c % 2 == 1]:
            if [cell // 2, row // 2] in [z.coords for z in zones]:
                amap[row][cell] = zone
    return (amap)


def render(m: fi.Map) -> None:
    CLEAR_SCREEN: str = '\x1b[2J\x1b[H'
    empty_cell: str = '\x1b[90m\x1b[90m▄▄▄▄\x1b[0m'
    drone: str = '(●)'
    render_width: int = (w := m.dimensions[1] + 1) + (w - 1) + 2
    render_height: int = (h := m.dimensions[0] + 1) + (h - 1) + 2
    amap: list[list[str]] = render_base(render_width, render_height)
    amap = render_zones(amap, m.get_zones())
    # print(CLEAR_SCREEN)
    for row in amap:
        for cell in row:
            print(cell, end='')
        print("")


# if __name__ == "__main__":
