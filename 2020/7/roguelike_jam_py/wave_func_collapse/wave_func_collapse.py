import json
import random

import numpy as np
import imageio as ii


class Tile(object):
    index = 0
    image = None

    def __init__(self, index, image):
        self.index = index
        self.image = image

    def __repr__(self):
        return f"tile[{self.index}]"


class Cell(object):
    def __init__(self, x, y, resource_tiles, cells):
        super().__init__()
        self.x, self.y = x, y
        self.resource_tiles = resource_tiles
        self.resource_tile = None
        self.cells = cells

    def __repr__(self):
        return f"cell[{self.x}, {self.y}] - {self.resource_tile.index}"

    def collapse(self):
        coords = self.cells.keys()

        directions = [(-1, 0), (+1, 0), (0, -1), (0, +1)]
        neighbors = list(map(lambda xy: (self.x + xy[0], self.y + xy[1]), directions))

        def adjacency_test(a, b, _direction):
            if _direction == (-1, 0):
                return (a[:, 0] == b[:, -1]).all()
            elif _direction == (+1, 0):
                return (a[:, -1] == b[:, 0]).all()
            elif _direction == (0, -1):
                return (a[0, :] == b[-1, :]).all()
            elif _direction == (0, +1):
                return (a[-1, :] == b[0, :]).all()

        contradiction = 20
        while contradiction > 0:
            self.resource_tile = None
            shuffled_tiles = self.resource_tiles[:]
            random.shuffle(shuffled_tiles)

            adjacent_neighbors = []
            for neighbor_coord, direction in zip(neighbors, directions):
                if neighbor_coord not in coords:
                    continue

                neighbor = self.cells[neighbor_coord]
                if neighbor.resource_tile is None:
                    continue

                adjacent_neighbors.append((neighbor, direction))

            for tile in shuffled_tiles:
                a = tile.image
                adjacency_result = True
                for neighbor, direction in adjacent_neighbors:
                    b = neighbor.resource_tile.image
                    if not adjacency_test(a, b, direction):
                        adjacency_result = False
                        continue

                if adjacency_result:
                    self.resource_tile = tile
                    contradiction = 0
                else:
                    contradiction -= 1

        if self.resource_tile is None:
            img = np.zeros_like((self.resource_tiles[0].image), dtype=np.ubyte)
            self.resource_tile = Tile(-1, img)


class Generator(object):
    def __init__(self, filepath):
        super().__init__()

        atlas = ii.imread(f"{filepath}.png")

        with open(f"{filepath}.json", "r") as fp:
            res = json.loads(fp.read())

        self.resource_tiles = []
        unit_width, unit_height = 1, 1
        for i, frame_data in enumerate(res["frames"].values()):
            x = frame_data["frame"]["x"]
            y = frame_data["frame"]["y"]
            w = frame_data["frame"]["w"]
            h = frame_data["frame"]["h"]
            unit_width, unit_height = max(w, unit_width), max(h, unit_height)
            img = atlas[y : y + h, x : x + w]
            self.resource_tiles.append(Tile(i, img))

        self.unit_width, self.unit_height = unit_width, unit_height

    def generate(self, width, height):
        self.cells = {}
        for x in range(width):
            for y in range(height):
                self.cells[x, y] = Cell(x, y, self.resource_tiles, self.cells)

        coords = tuple(self.cells.keys())
        start_coord = random.choice(coords)
        start_cell = self.cells[start_coord]
        start_cell.collapse()

        visited = [start_coord]

        def flood(_xy):
            _x, _y = _xy[0], _xy[1]
            a = _x + 1, _y + 0
            b = _x - 1, _y + 0
            c = _x, _y + 1
            d = _x, _y - 1

            def validate(__xy):
                return __xy not in visited and __xy in coords

            return tuple(filter(validate, [a, b, c, d]))

        cursor = start_coord
        plan = flood(cursor)

        while plan:
            next_plan = []
            for xy in plan:
                visited.append(xy)
                self.cells[xy].collapse()

                for next_xy in flood(xy):
                    if next_xy in next_plan:
                        continue
                    next_plan.append(next_xy)
            plan = next_plan

        world_resolution = self.unit_width * width, self.unit_height * height
        world_image = np.zeros(
            (world_resolution[1], world_resolution[0], 4), dtype=np.ubyte
        )

        num_cells = len(self.cells.values())
        for i, cell in enumerate(self.cells.values()):
            x = cell.x * self.unit_width
            y = cell.y * self.unit_height
            world_image[
                y : y + self.unit_height, x : x + self.unit_width
            ] = cell.resource_tile.image

        return world_image


def main():
    generator = Generator("./resource")

    for i in range(100):
        generated_img = generator.generate(width=8, height=8)
        ii.imwrite(f"generated_world_{i}.png", generated_img)


if __name__ == "__main__":
    main()
