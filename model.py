from itertools import product

import numpy as np
import gurobipy as gp

from gurobipy import GRB

dim = 5
fixCell = [(2, 1, 4), (3, 2, 4), (3, 4, 2), (4, 5, 1)]
visibleBuildingLeft = [3, 2, 3, 1, 3]
visibleBuildingRight = [3, 2, 1, 4, 2]
visibleBuildingTop= [3, 2, 1, 2, 3]
visibleBuildingBottom= [2, 4, 3, 1, 2]
constraintArea = []

model = gp.Model('MIP skyscraper')
model.setParam('LogToConsole', 0)

x = model.addMVar(shape=(dim, dim, dim), vtype=GRB.BINARY)

# Each cell have only one number
for i, j in product(range(dim), range(dim)):
    model.addConstr(gp.quicksum(x[i, j, k] for k in range(dim)) == 1)
    model.addConstr(gp.quicksum(x[k, i, j]for k in range(dim)) == 1)
    model.addConstr(gp.quicksum(x[i, k, j]for k in range(dim)) == 1)

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

# Display solution
x = np.where(x.x == 1)

solution = np.zeros(shape=(dim, dim), dtype=int)

for i in range(len(x[0])):
    solution[x[0][i], x[1][i]] = x[2][i] + 1

renderTop = '  '
renderBot = '  '
for i in range(dim):
    renderTop += f'  {visibleBuildingTop[i]} '
    renderBot += f'  {visibleBuildingBottom[i]} '

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
