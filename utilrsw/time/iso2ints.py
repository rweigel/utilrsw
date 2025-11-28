def iso2ints(isostr, length=None):
  """Convert time string in for YYYY-MM-DD[THH:mm:SS.FZ] to list of integers."""
  import re

  if not isinstance(isostr, str):
    if not isinstance(isostr, list):
      raise ValueError('Input must be a string or list of strings.')
    for i in range(len(isostr)):
      isostr[i] = iso2ints(isostr[i], length=7)
    return isostr

  tmp = re.split("-|:|T|Z", isostr)
  int_list = []
  for str_int in tmp:
    if str_int != "Z" and str_int != '':
      int_list.append(int(str_int))

  return int_list

