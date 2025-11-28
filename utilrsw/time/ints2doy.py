def ints2doy(t):
  """Convert from [y, m, d, ...] to [y, doy, ...].

  Examples
  --------
  >>> ints2doy([2000, 2, 1, 9, 9, 9]) # [2000, 32, 9, 9, 9]
  """
  from datetime import datetime
  import numpy as np

  in_type = type(t)

  t = np.array(t)

  if len(t.shape) == 1:
    pad = 6 - len(t)
    t = np.pad(t, (0, pad), 'constant', constant_values=0)
  else:
    pad = 6 - len(t[0])
    t = np.pad(t, ((0, 0), (0, pad)), 'constant', constant_values=0)

  if len(t.shape) == 1:
    day_of_year = datetime(*t).timetuple().tm_yday
  else:
    day_of_year = doy(t[:,:3])
    t = np.column_stack((t[:,0], day_of_year, t[:,3], t[:,4], t[:,5]))

  if in_type == np.ndarray:
    return t
  elif isinstance(in_type, tuple):
    return tuple(t.tolist())
  else:
    return t.tolist()

