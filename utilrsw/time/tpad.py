def tpad(time, length=7):
  """Pad list or array with 3 or more elements with zeros.

  Example:
  --------
  >>> from hxform import hxform as hx
  >>> print(hx.tpad([2000,1,1]))                 # [2000, 1, 1, 0, 0, 0, 0]
  >>> print(hx.tpad([2000,1,1], length=4))       # [2000, 1, 1, 0]
  >>> print(hx.tpad([2000,1,1,2,3,4], length=3)) # [2000, 1, 1]
  """
  import numpy as np
  in_type = type(time)

  # TODO: Check that time is valid
  time = np.array(time)

  assert len(time) > 2, "time must have at least 3 elements"

  if len(time.shape) == 1:
    if len(time) > length:
      time = time[0:length]
    else:
      pad = length - len(time)
      time = np.pad(time, (0, pad), 'constant', constant_values=0)
  else:
    if len(time[0]) > length:
      time = time[:,0:length]
    else:
      pad = length - len(time)
      time = np.pad(time, ((0, 0), (0, pad)), 'constant', constant_values=0)

  if in_type == np.ndarray:
    return time
  elif in_type == tuple:
    return tuple(map(tuple, time))
  else:
    return list(time)

