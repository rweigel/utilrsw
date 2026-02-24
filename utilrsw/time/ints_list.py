def ints_list(dto, dtf, dt_delta, n=7, end=False):
  """Generate list of integer time lists given datetime start, end, and delta.

  Each list has 7 elements: [year, month, day, hour, minute, second, microsecond]

  Example:
  --------
  >>> import datetime
  >>> dto = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)
  >>> dtf = datetime.datetime(2000, 1, 1, 2, 0, 0, 0)
  >>> ints_list(dto, dtf, {'hours': 1})
  [
    [2000, 1, 1, 0, 0, 0, 0],
    [2000, 1, 1, 1, 0, 0, 0]
  ]
  >>> import datetime
  >>> dto = datetime.datetime(2000, 1, 1)
  >>> dtf = datetime.datetime(2000, 1, 1, 2)
  >>> ints_list(dto, dtf, {'hours': 1}, end=True)
  [
    [2000, 1, 1, 0, 0, 0, 0],
    [2000, 1, 1, 1, 0, 0, 0],
    [2000, 1, 1, 2, 0, 0, 0]
  ]
  """
  import datetime

  if not isinstance(dto, datetime.datetime):
    n = min(n, len(dto))
    dto = datetime.datetime(*dto)

  if not isinstance(dtf, datetime.datetime):
    n = min(n, len(dtf))
    dtf = datetime.datetime(*dtf)

  t = []
  delta = datetime.timedelta(**dt_delta)
  i = 0
  while True:
    dt = dto + i*delta

    if not end and dt >= dtf:
      break

    i = i + 1
    ta = [dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond]
    t.append(ta[:n])

    if dt >= dtf:
      break

  return t


def ints_list_test():

  import datetime
  dto = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)
  dtf = datetime.datetime(2000, 1, 1, 2, 0, 0, 0)
  ref = [
    [2000, 1, 1, 0, 0, 0, 0],
    [2000, 1, 1, 1, 0, 0, 0]
  ]
  assert ints_list(dto, dtf, {'hours': 1}) == ref

  dto = datetime.datetime(2000, 1, 1)
  dtf = datetime.datetime(2000, 1, 1, 2)
  assert ints_list(dto, dtf, {'hours': 1}) == ref

  dto = datetime.datetime(2000, 1, 1)
  dtf = datetime.datetime(2000, 1, 2)
  assert len(ints_list(dto, dtf, {'hours': 1})) == 24

  dto = datetime.datetime(2000, 1, 1)
  dtf = datetime.datetime(2000, 1, 2)
  assert len(ints_list(dto, dtf, {'hours': 1}, end=True)) == 25

  dto = datetime.datetime(2000, 1, 1)
  dtf = datetime.datetime(2000, 1, 1)
  assert len(ints_list(dto, dtf, {'hours': 1})) == 0

  dto = datetime.datetime(2000, 1, 1)
  dtf = datetime.datetime(2000, 1, 1)
  assert len(ints_list(dto, dtf, {'hours': 1}, end=True)) == 1


if __name__ == "__main__":
  ints_list_test()