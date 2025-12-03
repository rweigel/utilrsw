def iso2ints(isostr, length=None):
  """Convert time string in YYYY-MM-DD[THH:mm:SS[.F[Z]]] to list of integers
  of form [year, month, day, hour, minute, second, microsecond]. If input is
  a list of strings, return a list of lists of integers.
  """
  import re

  if length is not None:
    if not isinstance(length, int):
      raise ValueError('Length must be an integer.')
    if length < 1 or length > 7:
      raise ValueError('Length must be between 1 and 7.')

  pattern = r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?Z?)?$'
  if isinstance(isostr, str) and not re.match(pattern, isostr):
    raise ValueError(f"{isostr} is not in the ISO 8601 format of 'YYYY-MM-DD[THH:mm:SS[.F[Z]]]")

  if not isinstance(isostr, str):
    if isinstance(isostr, list):
      for i in range(len(isostr)):
        isostr[i] = iso2ints(isostr[i], length=length)
      return isostr
    else:
      raise ValueError('Input must be a string or list of strings.')

  tmp = re.split(r"-|:|T|Z|\.", isostr)
  int_list = []
  for str_int in tmp:
    if str_int != "Z" and str_int != '':
      int_list.append(int(str_int))

  if length is not None:
    while len(int_list) < length:
      int_list.append(0)

  return int_list

def iso2int_test():

  test_str1 = "2010-12-30"
  test_ints1 = [2010, 12, 30]
  result1 = iso2ints(test_str1)
  assert(result1 == test_ints1)

  test_str1 = "2010-12-30"
  test_ints1 = [2010, 12, 30, 0]
  result1 = iso2ints(test_str1, length=4)
  assert(result1 == test_ints1)

  test_str1 = "2010-12-30"
  test_ints1 = [2010, 12, 30, 0, 0, 0, 0]
  result1 = iso2ints(test_str1, length=7)
  assert(result1 == test_ints1)

  test_str1 = "2010-12-30T01:02:03"
  test_ints1 = [2010, 12, 30, 1, 2, 3]
  result1 = iso2ints(test_str1)
  assert(result1 == test_ints1)

  test_str1 = "2010-12-30T01:02:03"
  test_ints1 = [2010, 12, 30, 1, 2, 3, 0]
  result1 = iso2ints(test_str1, length=7)
  print(f"Result1: {result1}")
  assert(result1 == test_ints1)

  test_str1 = "2010-12-30T01:02:03.000Z"
  test_ints1 = [2010, 12, 30, 1, 2, 3, 0]
  result1 = iso2ints(test_str1)
  assert(result1 == test_ints1)

  test_str1 = "2010-12-30T01:02:03.000"
  test_ints1 = [2010, 12, 30, 1, 2, 3, 0]
  result1 = iso2ints(test_str1)
  assert(result1 == test_ints1)

  test_str1 = "2010-12-30T01:02:03.000000Z"
  test_ints1 = [2010, 12, 30, 1, 2, 3, 0]
  result1 = iso2ints(test_str1)
  assert(result1 == test_ints1)

  test_str1 = "2010-12-30T01:02:03.000001Z"
  test_ints1 = [2010, 12, 30, 1, 2, 3, 1]
  result1 = iso2ints(test_str1)
  assert(result1 == test_ints1)

  test_str2 = ["2010-12-30T01:02:03.000Z", "2009-01-02T11:12:13.500Z"]
  test_ints2 = [[2010, 12, 30, 1, 2, 3, 0], [2009, 1, 2, 11, 12, 13, 500]]
  result2 = iso2ints(test_str2)
  assert(result2 == test_ints2)

  print("iso2ints tests passed.")

if __name__ == "__main__":
  iso2int_test()