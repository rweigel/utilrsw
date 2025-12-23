def components2matrix(*args):
  """Convert input to a 2D numpy array with three columns.

  For three arguments, components2matrix(x, y, z), each argument contains a value
  (or values) for one component (x, y, z). The output matrix has columns
  of x, y, and z. List and tuple inputs must have same length. Returned matrix
  is numpy.column_stack([x, y, z]).
    1. components2matrix(number, number, number)
    2. components2matrix(list, list, list)
    3. components2matrix(tuple, tuple, tuple)
    4. components2matrix(ndarray, ndarray, ndarray)
  where number is one of int, float, or numpy.number.

  For one argument, components2matrix(v), the argument contains all three components.
    Output matrix has columns of x, y, and z and 1 row. Numbers must be of same type.
      5. components2matrix([number, number, number])
      6. components2matrix((number, number, number))
    Output matrix has columns of x, y, and z and N rows. Numbers are coerced to same type.
      7. components2matrix([[number, number, number], ...]) (N lists of 3 numbers)
      8. components2matrix(((number, number, number), ...)) (N tuples of 3 numbers)

      9. components2matrix([ndarray, ...]) (N ndarrays of 3 numbers)
      10. components2matrix((ndarray, ...)) (N ndarrays of 3 numbers)

    Output matrix has columns of x, y, and z and 1 row
      9. components2matrix(size = (3, ) ndarray)
      10. components2matrix(size = (1, 3) ndarray)
    Output is same as input
      11. components2matrix((N, 3) ndarray)

  """
  import numpy

  if len(args) != 1 and len(args) != 3:
    raise ValueError(f'Number of arguments must be 1 or 3, got {len(args)}.')

  number_types = (int, float, numpy.number)

  if len(args) == 3:
    # components2matrix(x, y, z)
    coda = 'when passing three arguments.'
    for arg in args:
      if not (isinstance(arg, number_types) or
              isinstance(arg, (list, tuple)) or
              isinstance(arg, numpy.ndarray)):
        ve = f'All inputs must be number, list, tuple, or numpy.ndarray {coda}'
        raise ValueError(ve)

    for arg in args[1:]:
      if isinstance(args[0], number_types):
        if not isinstance(arg, number_types):
          ve = f'If the first input is a number, all inputs must numbers {coda}'
          raise ValueError(ve)
      else:
        if not isinstance(arg, type(args[0])):
          ve = f'If the first input is not numeric, all inputs have same type {coda}'
          raise ValueError(ve)

    if isinstance(args[0], number_types):
      # components2matrix(number, number, number)
      # Return 2D array with one row
      return numpy.column_stack([args[0], args[1], args[2]])

    if isinstance(args[0], (list, tuple)):
      # components2matrix(list, list, list)
      # or
      # components2matrix(tuple, tuple, tuple)
      for arg in args:
        if not isinstance(arg, number_types):
          if len(arg) != len(args[0]):
            ve = f'All arguments must have same length {coda}'
            raise ValueError(ve)
      # Return 2D array with columns of component
      return numpy.column_stack([args[0], args[1], args[2]])

    if isinstance(args[0], numpy.ndarray):
      # components2matrix(ndarray, ndarray, ndarray)
      if args[0].ndim == 0:
        return numpy.array([[args[0], args[1], args[2]]])

      for arg in args:
        if len(arg.shape) != 1:
          ve = f'All numpy.ndarrays must be 1D {coda}'
          raise ValueError(ve)
        if arg.shape[0] != args[0].shape[0]:
          ve = f'All numpy.ndarrays must have same shape[0] {coda}'
          raise ValueError(ve)

      # Return 2D array with columns of component
      return numpy.column_stack([args[0], args[1], args[2]])


  if len(args) == 1:
    coda = 'when passing one argument.'

    if not isinstance(args[0], (list, tuple, numpy.ndarray)):
      ve = f'Input must be list, tuple, or numpy.ndarray {coda}'
      raise ValueError(ve)

    if isinstance(args, (list, tuple)):
      # components2matrix(list) or components2matrix(tuple)
      if isinstance(args[0], (list, tuple)):
        # components2matrix([list of 3 values, ...])
        # or
        # components2matrix((tuple of 3 values, ...))
        for arg in args[0][1:]:
          if isinstance(args[0][0], number_types):
            if not isinstance(arg, number_types):
              ve = f'If the first input is a number, all inputs must numbers {coda}'
              raise ValueError(ve)
          else:
            if not isinstance(arg, type(args[0][0])):
              ve = f'If the first input is not numeric, all inputs must have same type {coda}'
              raise ValueError(ve)

          if isinstance(arg, (list, tuple)):
            if len(arg) != 3:
              ve = f'All list/tuples must have three elements {coda}'
              raise ValueError(ve)

        if isinstance(args[0][0], number_types):
          if len(args[0]) != 3:
            ve = f'Input list/tuple must have three elements {coda}'
            raise ValueError(ve)
          # components2matrix([number, number, number])
          # or
          # components2matrix((number, number, number))
          return numpy.array(args[0]).reshape((1, 3))
        if isinstance(args[0][0], (list, tuple)):
          # components2matrix([[number, number, number], ...])
          # or
          # components2matrix(((number, number, number), ...))
          # Does not test that each number is of same type
          return numpy.array(args[0])

        if isinstance(args[0][0], numpy.ndarray):
          # components2matrix([ndarray, ...])
          # or
          # components2matrix((ndarray, ...))
          nrows = len(args[0])
          for i in range(nrows):
            if args[0][i].shape != (3, ) and args[0][i].shape != (1, 3):
              ve = f'All input ndarrays must have shape (3,) or (1, 3). Got {args[0][i].shape} in element {i} {coda}'
              raise ValueError(ve)
          return numpy.array(args[0]).reshape((nrows, 3))

      if isinstance(args[0], numpy.ndarray):
        # components2matrix(ndarray)

        if len(args[0].shape) != 1 and len(args[0].shape) != 2:
          ve = f'Input numpy.ndarray must be 1D or 2D {coda}'
          raise ValueError(ve)

        if len(args[0].shape) == 1:
          # components2matrix(1D ndarray)
          if args[0].shape[0] != 3:
            ve = f'Input 1-D numpy.ndarray must have three elements {coda}'
            raise ValueError(ve)
          return numpy.array([args[0]])

        if len(args[0].shape) == 2:
          # components2matrix((n, 3) ndarray)
          if args[0].shape[1] != 3:
            ve = f'Input numpy.ndarray must have three columns {coda}'
            raise ValueError(ve)
          return args[0]
