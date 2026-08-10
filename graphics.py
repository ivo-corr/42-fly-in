import fly_in as fi


def render_base(width: int, height: int,
                zone_padding: int = 6) -> list[list[str]]:
    empty_cell: str = '\x1b[90m' + '█'*zone_padding + '\x1b[0m'
    amap: list[list[str]] = []
    for r in range(width):
        row: list[str] = []
        for c in range(height):
            row.append(empty_cell)
        amap.append(row)
    return (amap)


def render_zones(amap: list[list[str]], zones: list[fi.Map.Zone],
                 zone_padding: int = 6) -> None:
    zone: str = '\x1b[40m\x1b[100m█\x1b[47m{}\x1b[90m██\x1b[0m'
    connectors: list[str] = ["─", "│", "┌", "┐", "└",  "┘"]
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
    for row in [i for i in range(len(amap)) if i % 2 == 1]:
        for cell in [c for c in range(len(amap[0])) if c % 2 == 1]:
            if [cell // 2, row // 2] in [z.coords for z in zones]:
                zdrones = [len(z.drones) for z in zones if z.coords ==
                           [cell // 2, row // 2]][0]
                # cell_content = f'\x1b[40m\x1b[100m█\x1b[47m'\
                #                   f'{zdrones}\x1b[90m' +\
                #     '██' if (len(str(zdrones)) == 1) else '█' + '\x1b[0m'
                c = [
                    colors[color.name] for color in
                    [z.color for z in zones if
                     z.coords == [cell // 2, row // 2]]][0]
                amap[row][cell] = f'{c}{zdrones}\x1b[0m' + (f'{c}  ' if zdrones < 10 else '\x1b[90m█') + '\x1b[90m'+'█'*(zone_padding//2)+'\x1b[0m'
    # for z in zones:
    #     amap[z.coords[0]][z.coords[1]]
    return (amap)


def render(m: fi.Map) -> None:
    CLEAR_SCREEN: str = '\x1b[2J\x1b[H'
    empty_cell: str = '\x1b[90m\x1b[90m▄▄▄▄\x1b[0m'
    drone: str = '(●)'
    render_width: int = (w := m.dimensions[1] + 1) + (w - 1) + 2
    render_height: int = (h := m.dimensions[0] + 1) + (h - 1) + 2
    amap: list[list[str]] = render_base(render_width, render_height, 8)
    amap = render_zones(amap, m.get_zones(), 10)
    # print(CLEAR_SCREEN)
    for row in amap:
        for cell in row:
            print(cell, end='')
        print("")


# if __name__ == "__main__":
