def parse_config(file: str):
    result: list[list[str]] = []
    splat: list[str] = file.split("\n")
    splat = [s for s in splat if not s.startswith("#")]
    result.extend(
        [[s[0], s[1]] for s in
         [ss.split(": ") for ss in splat if len(ss.split(": ")) == 2]])
    return (result)


if __name__ == "__main__":
    with open("maps/easy/01_linear_path.txt") as file:
        print(parse_config(file.read()))
