def doy(date):
  """
  d = [2021, 7, 5]
  doy(d) = 186
  doy(numpy.array(d)) = 186

  d = [[2000, 9, 30], [1900, 9, 30], [1980, 5, 5]]
  doy(d) =[274, 273, 126]
  doy(numpy.array(d)) = numpy.array([274, 273, 126])
  """
  import numpy

  from utilrsw.time.is_leap_year import is_leap_year

  date_type = type(date)
  date = numpy.array(date)
  if len(date.shape) == 1:
    year, month, day = date[0], date[1], date[2]
    if is_leap_year(year):
      K = 1
    else:
      K = 2
  else:
    year, month, day = date[:, 0], date[:, 1], date[:, 2]
    K = numpy.where(is_leap_year(year), 1, 2)

  # https://astronomy.stackexchange.com/a/2409
  N = numpy.fix((275.0*month)/9.0) - K*numpy.fix((month + 9.0)/12.0) + day - 30.0

  N = N.astype(int)

  if N.shape == ():
    return N.item()
  else:
    if date_type in (list, tuple):
      return date_type(N.tolist())
    else:
      return N


def doy_test():
  import os
  import numpy
  from utilrsw.time.is_leap_year import is_leap_year

  def read_calendar(file_name):
    file = os.path.join(os.path.dirname(__file__), file_name)
    calendar = {}
    with open(file, "r") as f:
      month = 1
      for line in f:
        line = line.strip().split()[1:]
        calendar[month] = [int(x) for x in line]
        month += 1
    return calendar

  ymd = [2021, 7, 5]
  doy_test = 186

  doy_calc = doy(ymd)
  assert(doy_test == doy_calc)
  assert(type(doy_calc) is int)

  doy_calc = doy(numpy.array(ymd))
  assert(doy_calc == doy_test)
  assert(type(doy_calc) is int)


  ymds = [[2000, 9, 30], [1900, 9, 30], [1980, 5, 5]]
  doys_test = [274, 273, 126]

  doys_calc = doy(ymds)
  assert(doys_calc == doys_test)
  assert(type(doys_calc) is list)
  assert(type(doys_calc[0]) is int)

  doys_calc = doy(numpy.array(ymds))
  assert(numpy.all(doys_calc == numpy.array(doys_test)))
  assert(type(doys_calc) is numpy.ndarray)
  assert(doys_calc.dtype == numpy.int64)


  calendar_nonleap = read_calendar("doy.nonleap.txt")
  calendar_leap = read_calendar("doy.leap.txt")

  for year in range(1804, 2401):
    if is_leap_year(year):
      calendar = calendar_leap
    else:
      calendar = calendar_nonleap
    for month in range(1,13):
      for day in range(1, len(calendar[month])+1):
        assert(doy([year, month, day]) == calendar[month][day-1])


if __name__ == '__main__':
  doy_test()