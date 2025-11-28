import numpy as np

# Installed using pip install -e . so absolute import works
# Execute test using python -m utilrsw.np.components2matrix_test from
# the utilrsw package root directory.
from utilrsw.np.matrix2components import matrix2components
from utilrsw.np.components2matrix import components2matrix

# Three inputs
comps0l = [1.0, 0.0, 0.0]
comps0t = (1.0, 0.0, 0.0)

# components2matrix(x, y, z) where x, y, z are numbers
mat = components2matrix(*comps0l)
comps = matrix2components(*comps0l, mat)
assert(list(comps) == comps0l)


comps0 = ([1.0], [0.0], [0.0])

# components2matrix(x, y, z) where x, y, z are lists
mat = components2matrix(*comps0)
comps = matrix2components(*[*comps0, mat])
assert(comps == comps0)


comps0 = ([1.0, 2.0], [0.0, 0.0], [0.0, 0.0])

# components2matrix(x, y, z) where x, y, z are lists
mat = components2matrix(*comps0)
comps = matrix2components(*comps0, mat)
assert(comps == comps0)


comps0 = (np.array(1), np.array(0), np.array(0))

# components2matrix(x, y, z) where x, y, z are scalar numpy.ndarrays
mat = components2matrix(*comps0)
comps = matrix2components(*comps0, mat)
assert(comps == comps0)


comps0 = (np.array([1.0, 2.0]), np.array([0.0, 0.0]), np.array([0.0, 0.0]))

# components2matrix(x, y, z) where x, y, z are shape = (2, ) numpy.ndarrays
mat = components2matrix(*comps0)
comps = matrix2components(*comps0, mat)
for i in range(3):
  assert(np.all(comps[i] == comps0[i]))


# One input
comps0l = [1.0, 0.0, 0.0]
comps0t = (1.0, 0.0, 0.0)

# components2matrix([x, y, z]) where x, y, z are numbers
mat = components2matrix(comps0l)
comps = matrix2components(*[*comps0l, mat])
assert(list(comps) == comps0l)

# components2matrix((x, y, z)) where x, y, z are numbers
mat = components2matrix(comps0t)
comps = matrix2components(*[*comps0t, mat])
assert(comps == comps0t)

comps0l = [ [1.0, 0.0, 0.0], [2.0, 0.0, 0.0] ]
comps0t = ( (1.0, 0.0, 0.0), (2.0, 0.0, 0.0) )

# components2matrix([[x, y, z], ...]) where x, y, z are numbers
mat = components2matrix(comps0l)
comps = matrix2components(comps0l, mat)
assert(comps == comps0l)

# components2matrix([(x, y, z), ...]) where x, y, z are numbers
mat = components2matrix(list(comps0t))
comps = matrix2components(list(comps0t), mat)
assert(comps == list(comps0t))

# components2matrix(((x, y, z), ...)) where x, y, z are numbers
mat = components2matrix(comps0t)
comps = matrix2components(comps0t, mat)
assert(comps == comps0t)

# components2matrix(([x, y, z], ...)) where x, y, z are numbers
mat = components2matrix(tuple(comps0t))
comps = matrix2components(tuple(comps0t), mat)
assert(comps == tuple(comps0t))

comps0n = [np.array([1.0, 0.0, 0.0]), np.array([2.0, 0.0, 0.0])]

# components2matrix([x, y, z]) where x, y, z are ndarrays
mat = components2matrix(comps0n)
comps = matrix2components(comps0n, mat)
for i in range(len(comps0n)):
  assert(np.all(comps[i] == comps0n[i]))

# components2matrix((x, y, z)) where x, y, z are ndarrays
mat = components2matrix(tuple(comps0n))
comps = matrix2components(tuple(comps0n), mat)
for i in range(len(comps0n)):
  assert(np.all(comps[i] == tuple(comps0n[i])))

# components2matrix((3, ) ndarray)
mat = components2matrix(comps0n[0])
comps = matrix2components(comps0n[0], mat)
assert(np.all(comps == comps0n[0]))

# components2matrix((1, 3) ndarray)
mat = components2matrix(comps0n[0].reshape((1, 3)))
comps = matrix2components(comps0n[0].reshape((1, 3)), mat)
assert(np.all(comps == comps0n[0].reshape((1, 3))))

# components2matrix((2, 3) ndarray)
mat = components2matrix(np.array(comps0n))
comps = matrix2components(np.array(comps0n), mat)
assert(np.all(comps == np.array(comps0n)))



