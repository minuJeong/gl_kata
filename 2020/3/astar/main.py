import math
import random

import numpy as np
import imageio as ii
from glm import *


width, height = 200, 200
inf = 1.0e999


class Node(object):
    x = -1
    y = -1
    is_obstacle = False
    fit_score = inf
    prev_node = None

    def __init__(self, x, y):
        super(Node, self).__init__()
        self.x, self.y = x, y

    def __repr__(self):
        return f"node[{self.x}, {self.y}]"

    def pos(self):
        return (self.x, self.y)


def heuristic(pos):
    pass


def astar(start, goal, nodes):
    openset = [start]
    closeset = []

    def _get_next_opened() -> Node:
        min_node = openset[0]
        min_f_score = min_node.fit_score
        for n in openset:
            if n.fit_score < min_f_score:
                min_f_score = n.fit_score
                min_node = n
        return min_node

    def _get_neighbors(node):
        neighbors = []
        x, y = node.pos()
        for _x, _y in [(-1, 0), (+1, 0), (0, -1), (0, +1)]:
            if _x == 0 and _y == 0:
                continue

            xx, yy = x + _x, y + _y
            if xx < 0 or yy < 0 or xx > width - 1 or yy > height - 1:
                continue

            neighbor = nodes[xx, yy]
            if neighbor.is_obstacle:
                continue

            if neighbor in closeset:
                continue

            if neighbor in openset:
                continue
            
            neighbors.append(neighbor)

        return neighbors

    def _build_path(node):
        path = [node]
        while True:
            node = node.prev_node
            path.append(node)
            if not node.prev_node:
                break

        return reversed(path)

    def _eval_cost(a, b):
        return distance(vec2(*a.pos()), vec2(*b.pos()))

    def _eval_cost_spent(node):
        n = 0
        while node.prev_node:
            n += 1
            node = node.prev_node
        return n

    cursor = start
    while openset:
        cursor = _get_next_opened()
        if cursor == goal:
            print("reached goal, building path..")
            start.prev_node = None
            return _build_path(cursor)

        openset.remove(cursor)
        closeset.append(cursor)

        for neighbor in _get_neighbors(cursor):
            neighbor.prev_node = cursor
            neighbor.fit_score = _eval_cost_spent(neighbor) + _eval_cost(neighbor, goal)

            if neighbor not in openset:
                openset.append(neighbor)

    return None


def main():
    nodes = {}
    for x in range(0, width):
        for y in range(0, height):
            nodes[x, y] = Node(x, y)

    for x in range(5, 88):
        nodes[x, 99].is_obstacle = True
    for x in range(44, 189):
        nodes[x, 166].is_obstacle = True
    for x in range(11, 122):
        nodes[x, 11].is_obstacle = True
    for y in range(2, 122):
        nodes[111, y].is_obstacle = True
    for y in range(33, 66):
        nodes[2, y].is_obstacle = True
    for y in range(99, 177):
        nodes[188, y].is_obstacle = True

    def get_rand_xy():
        return random.randint(0, width - 1), random.randint(0, height - 1)

    x, y = get_rand_xy()
    start = nodes[x, y]
    while start.is_obstacle:
        x, y = get_rand_xy()
        start = nodes[x, y]

    x, y = get_rand_xy()
    goal = nodes[x, y]
    while start.is_obstacle:
        x, y = get_rand_xy()
        goal = nodes[x, y]

    print(f"start: {start}, goal: {goal}")

    if start == goal:
        print(f"start == goal ({start}, {goal})")
        return

    path = astar(start, goal, nodes)
    if not path:
        print("blocked")
        return

    visual = np.zeros((height, width, 4), dtype=np.ubyte)
    for x in range(0, width):
        for y in range(0, height):
            node = nodes[x, y]
            if node.is_obstacle:
                visual[x, y] = (255, 12, 12, 255)
            else:
                d_start = distance(vec2(*start.pos()), vec2(x, y))
                d_goal = distance(vec2(*goal.pos()), vec2(x, y))
                d_max = clamp(1.0 - min(d_start, d_goal) / 12.0, 0.0, 1.0)
                d_max = int(d_max * 255.0)
                if d_start < 25:
                    d = d_start / 12.0
                    d *= 255.0
                    d = int(clamp(d, 0.0, 255.0))
                    visual[x, y] = (128, 0, d, d_max)
                elif d_goal < 25:
                    d = d_goal / 12.0
                    d *= 255.0
                    d = int(clamp(d, 0.0, 255.0))
                    visual[x, y] = (d, 0, 128, d_max)
                else:
                    visual[x, y] = (12, 0, 0, d_max)

    for i, step in enumerate(path):
        x, y = step.pos()
        visual[x, y] = ((i * 2) % 255, 255, 128, 255)

    visual[start.pos()] = (255, 0, 0, 255)
    visual[goal.pos()] = (0, 0, 255, 255)

    ii.imwrite("vislaized.png", visual)


if __name__ == "__main__":
    main()
