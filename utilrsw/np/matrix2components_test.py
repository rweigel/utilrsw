import numpy as np

# Installed using pip install -e . so absolute import works
# Execute test using python -m utilrsw.np.components2matrix_test from
# the utilrsw package root directory.
from utilrsw.np.components2matrix import components2matrix
from utilrsw.test.assert_raises import assert_raises

match = "Input must be list, tuple, or numpy.ndarray"
# components2matrix(None)
assert_raises(ValueError, components2matrix, [None], match=match)
# components2matrix({})
assert_raises(ValueError, components2matrix, [{}], match=match)


comps1 = np.array([[1.0, 0.0, 0.0]])
comps2 = np.array([[1.0, 0.0, 0.0], [2.0, 0.0, 0.0]])

# Three inputs

# Case 1. in docstring
mat = components2matrix(1.0, 0.0, 0.0)
assert(mat.shape == (1, 3))
assert(np.all(mat == comps1))

match = "Number of arguments must be 1 or 3"
# components2matrix(1, 2)
assert_raises(ValueError, components2matrix, [1, 2], match=match)
# components2matrix(1, 2, 3, 4)
assert_raises(ValueError, components2matrix, [1, 2, 3, 4], match=match)
# components2matrix([1, 2, 3], 1)
assert_raises(ValueError, components2matrix, [[1, 2, 3], 1], match=match)

match = 'If the first input is a number, all inputs must numbers'
# components2matrix(1, [2], 3)
assert_raises(ValueError, components2matrix, [1, [2], 3], match=match)
# components2matrix(1, (2,), 3)
assert_raises(ValueError, components2matrix, [1, (2,), 3], match=match)
match = 'If the first input is not numeric, all inputs have same type'
# components2matrix([1], 2, 3)
assert_raises(ValueError, components2matrix, [[1], 2, 3], match=match)

match = 'All inputs must be number, list, tuple, or numpy.ndarray'
# components2matrix({}, {}, {})
assert_raises(ValueError, components2matrix, [{}, {}, {}], match=match)

# Case 2. in docstring
match = 'All arguments must have same length'
# components2matrix([1, 2], [0], [0])
assert_raises(ValueError, components2matrix, [[1, 2], [0], [0]], match=match)
# components2matrix((1, 2), (0, ), (0, ))
assert_raises(ValueError, components2matrix, [(1, 2), (0, ), (0, )], match=match)

mat = components2matrix([1.0], [0.0], [0.0])
assert(mat.shape == (1, 3))
assert(np.all(mat == comps1))

mat = components2matrix([1.0, 2.0], [0.0, 0.0], [0.0, 0.0])
assert(mat.shape == (2, 3))
assert(np.all(mat[0, :] == comps2[0, :]))
assert(np.all(mat[1, :] == comps2[1, :]))

# Case 3. in docstring
mat = components2matrix((1.0), (0.0), (0.0))
assert(mat.shape == (1, 3))
assert(np.all(mat == comps1))

mat = components2matrix((1.0, 2.0), (0.0, 0.0), (0.0, 0.0))
assert(mat.shape == (2, 3))
assert(np.all(mat[0, :] == comps2[0, :]))
assert(np.all(mat[1, :] == comps2[1, :]))

# Case 4. in docstring
mat = components2matrix(np.array(1), np.array(0), np.array(0))
assert(mat.shape == (1, 3))
assert(np.all(mat == comps1))

mat = components2matrix(np.array([1, 2]), np.array([0, 0]), np.array([0, 0]))
assert(mat.shape == (2, 3))
assert(np.all(mat == comps2))

match = 'All numpy.ndarrays must be 1D'
arg = [np.array([[1, 2], [3, 4]]), np.array([0, 0]), np.array([0, 0])]
# components2matrix(arg[0])
assert_raises(ValueError, components2matrix, arg, match=match)

match = 'All numpy.ndarrays must have same shape[0]'
arg = [np.array([1, 2]), np.array([1, 2]), np.array([1, 2, 3])]
# components2matrix(arg[0])
assert_raises(ValueError, components2matrix, arg, match=match)


# One input

match = 'Input list/tuple must have three elements'
# components2matrix([1.0, 0.0])
assert_raises(ValueError, components2matrix, [[1.0, 0.0]], match=match)

# Case 5. in docstring
mat = components2matrix([1.0, 0.0, 0.0])
assert(mat.shape == (1, 3))
assert(np.all(mat == comps1))

# Case 6. in docstring
mat = components2matrix((1.0, 0.0, 0.0))
assert(mat.shape == (1, 3))
assert(np.all(mat == comps1))

# Case 7. in docstring
mat = components2matrix([[1, 0, 0], [2, 0, 0]])
assert(mat.shape == (2, 3))
assert(np.all(mat == comps2))

# Case 8. in docstring
mat = components2matrix([np.array([1, 0, 0]), np.array([2, 0, 0])])
assert(mat.shape == (2, 3))
assert(np.all(mat == comps2))

mat = components2matrix([
  np.array([1, 0, 0]).reshape(1, 3),
  np.array([2, 0, 0]).reshape(1, 3)])
assert(mat.shape == (2, 3))
assert(np.all(mat == comps2))

# Mis-match of number types allowed. Coerced to common type by numpy.array()
mat = components2matrix([[1.0, 0, 0], [2, 0, 0]])
assert(mat.shape == (2, 3))
assert(np.all(mat == comps2))

# Case 8. in docstring
mat = components2matrix(((1, 0, 0), (2, 0, 0)))
assert(mat.shape == (2, 3))
assert(np.all(mat == comps2))

# Case 9. in docstring
mat = components2matrix((np.array([1, 0, 0]), np.array([2, 0, 0])))
assert(mat.shape == (2, 3))
assert(np.all(mat == comps2))


# Case 7 and 8 error cases
match = 'If the first input is not numeric, all inputs must have same type'
assert_raises(ValueError, components2matrix, [[[1, 0, 0], (2, 0, 0)]], match=match)

# Case 11. in docstring
mat = components2matrix(np.array([1.0, 0.0, 0.0]))
assert(np.all(mat == comps1))


match = 'Input 1-D numpy.ndarray must have three elements'
# components2matrix(np.array([1.0, 0.0]))
assert_raises(ValueError, components2matrix, [np.array([1.0, 0.0])], match=match)

# Case 12. in docstring
comps1c = comps1.copy()
comps1c.shape = (1, 3)
mat = components2matrix(comps1c)
assert(mat.shape == (1, 3))
assert(np.all(mat == comps1))

#x
match = 'Input 1-D numpy.ndarray must have three elements'
# components2matrix(np.array([1.0, 0.0]))
assert_raises(ValueError, components2matrix, [np.array([1.0, 0.0])], match=match)

match = 'Input numpy.ndarray must be 1D or 2D'
# components2matrix(np.array([[[1.0, 0.0, 0.0]]]))
assert_raises(ValueError, components2matrix, [np.array([[[1.0, 0.0, 0.0]]])], match=match)

# Case 13. in docstring
mat = components2matrix(comps2)
assert(mat.shape == (2, 3))
assert(np.all(mat == comps2))

match = 'Input must be list, tuple, or numpy.ndarray'
assert_raises(ValueError, components2matrix, [None], match=match)

match = 'Input must be list, tuple, or numpy.ndarray'
assert_raises(ValueError, components2matrix, [{}], match=match)

match = 'Input numpy.ndarray must have three columns'
arg = [np.array([[1.0, 0.0, 0.0, 0.0]])]
# components2matrix(arg)
assert_raises(ValueError, components2matrix, arg, match=match)

arg = [np.array([[1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]])]
# components2matrix(arg)
assert_raises(ValueError, components2matrix, arg, match=match)

