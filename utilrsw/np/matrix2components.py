def matrix2components(*args):
  """Given args passed to components2matrix, return values matching input type.
  """
  import numpy as np
  out = []
  if len(args) != 4 and len(args) != 2:
    raise ValueError(f'Number of arguments must be 1 or 4, got {len(args)}.')

  if len(args) == 4:
    # Input was components2matrix(x, y, z, mat)
    mat = args[3]
    for i in range(3):
      comp = mat[:, i]
      if isinstance(args[i], np.ndarray):
        out.append(np.array(comp).reshape(args[i].shape))
      elif isinstance(args[i], (list, tuple)):
        out.append(type(args[i])(comp.tolist()))
      else:
        out.append(comp[0])
    return tuple(out)

  if len(args) == 2:
    number_types = (int, float, np.number)
    # Input was components2matrix(v, mat)
    mat = args[1]
    if isinstance(args[0], (list, tuple)):
      if isinstance(args[0][0], list):
        return [list(row) for row in mat.tolist()]
      elif isinstance(args[0][0], tuple):
        ret = [tuple(row) for row in mat.tolist()]
        if isinstance(args[0], list):
          return ret
        if isinstance(args[0], tuple):
          return tuple(ret)
      elif isinstance(args[0][0], np.ndarray):
        ret = [np.array(row) for row in mat.tolist()]
        if isinstance(args[0], list):
          return ret
        if isinstance(args[0], tuple):
          return tuple(ret)
      elif isinstance(args[0][0], number_types):
        if isinstance(args[0], list):
          return mat[0, :].tolist()
        if isinstance(args[0], tuple):
          return tuple(mat[0, :].tolist())
      else:
        raise ValueError('Unsupported input type.')

    if isinstance(args[0], np.ndarray):
      return mat.reshape(args[0].shape)
