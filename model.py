from itertools import product

import numpy as np
import gurobipy as gp

from gurobipy import GRB

dim = 9
fixCell = [(1, 4, 6),
           (2, 9, 1),
           (3, 1, 8),
           (3, 4, 3),
           (4, 1, 2),
           (4, 2, 4),
           (4, 7, 7),
           (6, 3, 2),
           (6, 8, 9),
           (6, 9, 8),
           (7, 6, 2),
           (7, 9, 5),
           (8, 1, 9),
           (9, 6, 6)]
visibleBuildingLeft = [4, 2, 2, 5, 5, 3, 3, 1, 3]
visibleBuildingRight = [4, 4, 2, 1, 3, 2, 3, 3, 3]
visibleBuildingTop= [4, 2, 2, 3, 1, 4, 2, 4, 3]
visibleBuildingBottom= [2, 4, 2, 1, 5, 3, 6, 2, 4]
constraintArea = [[(1, 1), (2, 1), (2, 2),
                   (3, 1), (4, 1), (4, 2),
                   (4, 3), (5, 1), (5, 3)],
                  [(1, 2), (1, 3), (1, 4),
                   (1, 5), (1, 6), (2, 3),
                   (2, 4), (3, 2), (3, 3)],
                  [(1, 7), (2, 5), (2, 6),
                   (2, 7), (2, 8), (3, 4),
                   (3, 5), (3, 6), (3, 7)],
                  [(1, 8), (1, 9), (2, 9),
                   (3, 8), (3, 9), (4, 7),
                   (4, 8), (4, 9), (5, 8)],
                  [(4, 4), (4, 5), (4, 6),
                   (5, 4), (5, 5), (5, 6),
                   (6, 4), (6, 5), (6, 6)],
                  [(5, 2), (6, 1), (6, 2),
                   (6, 3), (7, 1), (7, 2),
                   (8, 1), (9, 1), (9, 2)],
                  [(7, 3), (7, 4), (7, 5),
                   (7, 6), (8, 2), (8, 3),
                   (8, 4), (8, 5), (9, 3)],
                  [(7, 7), (7, 8), (8, 6),
                   (8, 7), (9, 4), (9, 5),
                   (9, 6), (9, 7), (9, 8)],
                  [(5, 7), (5, 9), (6, 7),
                   (6, 8), (6, 9), (7, 9),
                   (8, 8), (8, 9), (9, 9)],]

model = gp.Model('MIP skyscraper')
model.setParam('LogToConsole', 0)

x = model.addMVar(shape=(dim, dim, dim), vtype=GRB.BINARY)

# Each cell has enough number
for i, j in product(range(dim), range(dim)):
    model.addConstr(gp.quicksum(x[i, j, k] for k in range(dim)) == 1)
    model.addConstr(gp.quicksum(x[k, i, j] for k in range(dim)) == 1)
    model.addConstr(gp.quicksum(x[i, k, j] for k in range(dim)) == 1)

# Each area has enough number
if dim == 9 and constraintArea == []:
    # Sky sudoky
    for i, j in product([0, 3, 6], [0, 3, 6]):
        for k in range(dim):
            model.addConstr(gp.quicksum(x[a, b, k]
                                        for a, b in product([i, i + 1, i + 2],
                                                            [j, j + 1, j + 2])) == 1)
else:
    # Krazytown
    for area in constraintArea:
        for k in range(dim):
            model.addConstr(gp.quicksum(x[i - 1, j - 1, k] for i, j in area) == 1)

for i, j, k in fixCell:
    model.addConstr(x[i - 1, j - 1, k - 1] == 1)

# Visible building constraints
for i in range(dim):
    # From left
    xLeft = []
    for j in range(1, dim - 1):
        for k in range(j, dim - 1):
            z = model.addVar(vtype=GRB.BINARY)
            xLeft.append(z)
            y = gp.quicksum(x[i, a, b]
                            for a in range(j)
                            for b in range(k + 1, dim))
            model.addConstr(y + j*z - j <= 0)
            model.addConstr(x[i, j, k] - z >= 0)
            model.addConstr(x[i, j, k] - y - z <= 0)
    model.addConstr(gp.quicksum(xL
                                for xL in xLeft)
                    + gp.quicksum(x[i, j, dim - 1]
                                for j in range(dim))
                    >= visibleBuildingLeft[i] - 1)

    # From right
    xRight = []
    for j in range(1, dim - 1):
        for val in range(j):
            k = dim - 1 - val - 1
            z = model.addVar(vtype=GRB.BINARY)
            xRight.append(z)
            y = gp.quicksum(x[i, a, b]
                            for a in range(j + 1, dim)
                            for b in range(k + 1, dim))
            model.addConstr(y + j*z - j <= 0)
            model.addConstr(x[i, j, k] - z >= 0)
            model.addConstr(x[i, j, k] - y - z <= 0)
    model.addConstr(gp.quicksum(xR
                                for xR in xRight)
                    + gp.quicksum(x[i, j, dim - 1]
                                for j in range(dim))
                    >= visibleBuildingRight[i] - 1)

    # From top
    xTop = []
    for j in range(1, dim - 1):
        for k in range(j, dim - 1):
            z = model.addVar(vtype=GRB.BINARY)
            xTop.append(z)
            y = gp.quicksum(x[a, i, b]
                            for a in range(j)
                            for b in range(k + 1, dim))
            model.addConstr(y + j*z - j <= 0)
            model.addConstr(x[j, i, k] - z >= 0)
            model.addConstr(x[j, i, k] - y - z <= 0)
    model.addConstr(gp.quicksum(xT
                                for xT in xTop)
                    + gp.quicksum(x[j, i, dim - 1]
                                for j in range(dim))
                    >= visibleBuildingTop[i] - 1)

    # From bottom
    xBottom = []
    for j in range(1, dim - 1):
        for val in range(j):
            k = dim - 1 - val - 1
            z = model.addVar(vtype=GRB.BINARY)
            xBottom.append(z)
            y = gp.quicksum(x[a, i, b]
                            for a in range(j + 1, dim)
                            for b in range(k + 1, dim))
            model.addConstr(y + j*z - j <= 0)
            model.addConstr(x[j, i, k] - z >= 0)
            model.addConstr(x[j, i, k] - y - z <= 0)
    model.addConstr(gp.quicksum(xB
                                for xB in xBottom)
                    + gp.quicksum(x[j, i, dim - 1]
                                for j in range(dim))
                    >= visibleBuildingBottom[i] - 1)

model.setObjective(0, GRB.MAXIMIZE)
model.optimize()

x = np.where(x.x == 1)

solution = np.zeros(shape=(dim, dim), dtype=int)

for i in range(len(x[0])):
    solution[x[0][i], x[1][i]] = x[2][i] + 1

renderTop = '  '
renderBot = '  '
for i in range(dim):
    renderTop += f'  {visibleBuildingTop[i]} '
    renderBot += f'  {visibleBuildingBottom[i]} '

# Display problem
print(renderTop)
for row in range(dim):
    renderUpRow = '  +'
    renderRow = f'{visibleBuildingLeft[row]} |'
    for i in range(dim):
        if (row + 1, i + 1, solution[row, i]) in fixCell:
            renderRow += f' {solution[row, i]} |'
        else:
            renderRow += f'   |'
        renderUpRow += '---+'
    renderRow += f' {visibleBuildingRight[row]}'
    print(renderUpRow)
    print(renderRow)
print(renderUpRow)
print(renderBot)

print('\n')
# Display solution
print(renderTop)
for row in range(dim):
    renderUpRow = '  +'
    renderRow = f'{visibleBuildingLeft[row]} |'
    for i in solution[row]:
        renderRow += f' {i} |'
        renderUpRow += '---+'
    renderRow += f' {visibleBuildingRight[row]}'
    print(renderUpRow)
    print(renderRow)
print(renderUpRow)
print(renderBot)
