import z3
from time import time
from random import random

s = z3.Solver()

cur_board = [
    ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '#', '.', '.', '.', '#', '.'],
    ['.', '.', '.', '#', '.', '#', '.', '.', '.'],
    ['.', '#', '#', '.', '#', '#', '#', '.', '.'],
    ['.', '.', '.', '#', '#', '.', '#', '.', '.'],
    ['.', '.', '#', '#', '.', '#', '#', '.', '.'],
    ['.', '.', '.', '#', '.', '#', '.', '.', '.'],
    ['.', '.', '#', '.', '.', '#', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.', '.']
]

SIZE = 25
BORDER = 2

cur_board = []
for _ in range(BORDER):
    cur_board.append(['.'] * SIZE)

for i in range(SIZE - BORDER * 2):
    row = ['.'] * BORDER
    for j in range(SIZE - BORDER * 2):
        if random() < 0.3:
            row.append('#')
        else:
            row.append('.')
    row += ['.'] * BORDER
    cur_board.append(row)

for _ in range(BORDER):
    cur_board.append(['.'] * SIZE)

for row in cur_board:
    print(''.join(row))


def get_neighbors(cells, i, j, maxI, maxJ):
    neighbors = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            if i + dx < 0 or i + dx >= maxI:
                continue
            if j + dy < 0 or j + dy >= maxJ:
                continue
            neighbors.append(cells[i + dx][j + dy])
    return neighbors


def dead(cell):
    return cell == 0


def alive(cell):
    return cell == 1


def get_dead_constraints(s, cells, i, j):
    neighbors = get_neighbors(cells, i, j, SIZE, SIZE)
    live_neighbors = z3.Sum(neighbors)

    # if this cell was dead then it must not have had 3 alive neighbors
    s.add(z3.Implies(dead(cells[i][j]), live_neighbors != 3))

    # if it was alive then it must not have had 2 or 3 alive neighbors
    s.add(z3.Implies(alive(cells[i][j]), z3.And(
        live_neighbors != 2, live_neighbors != 3)))


def get_alive_constraints(s, cells, i, j):
    neighbors = get_neighbors(cells, i, j, SIZE, SIZE)
    live_neighbors = z3.Sum(neighbors)

    # if this cell was dead it must have had 3 alive neighbors
    s.add(z3.Implies(dead(cells[i][j]), live_neighbors == 3))

    # if it was alive it must have had either 2 or 3 alive neighbors
    s.add(z3.Implies(alive(cells[i][j]), z3.Or(
        live_neighbors == 2, live_neighbors == 3)))


cells = []
for i in range(SIZE):
    row = []
    for j in range(SIZE):
        var = z3.Int(f'c{i}{j}')
        s.add(z3.Or(var == 0, var == 1))
        row.append(var)
    cells.append(row)

for i in range(SIZE):
    for j in range(SIZE):
        if cur_board[i][j] == '.':
            get_dead_constraints(s, cells, i, j)
        else:
            get_alive_constraints(s, cells, i, j)

t1 = time()
ans = s.check()
print(time() - t1)
if ans == z3.unsat:
    print('dead')
    raise SystemExit()

model = s.model()

preimage = []
for row in cells:
    pre_row = []
    for cell in row:
        if model[cell] == 1:
            pre_row.append('#')
        else:
            pre_row.append('.')
    preimage.append(pre_row)

for row in preimage:
    print(''.join(row))
