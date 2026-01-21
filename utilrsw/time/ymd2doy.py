def ymd2doy(date):
  """
  d = [2021, 7, 5]
  ymd2doy(d) = 186
  ymd2doy(numpy.array(d)) = 186

  d = [[2000, 9, 30], [1900, 9, 30], [1980, 5, 5]]
  ymd2doy(d) =[274, 273, 126]
  ymd2doy(numpy.array(d)) = numpy.array([274, 273, 126])
  """

  # TODO: Simple to avoid calculation and use calendar() function?
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


def ymd2doy_test():
  import numpy

  ymd = [2021, 7, 5]
  doy_test = 186

  doy_calc = ymd2doy(ymd)
  assert(doy_test == doy_calc)
  assert(type(doy_calc) is int)

  doy_calc = ymd2doy(numpy.array(ymd))
  assert(doy_calc == doy_test)
  assert(type(doy_calc) is int)


  ymds = [[2000, 9, 30], [1900, 9, 30], [1980, 5, 5]]
  doys_test = [274, 273, 126]

  doys_calc = ymd2doy(ymds)
  assert(doys_calc == doys_test)
  assert(type(doys_calc) is list)
  assert(type(doys_calc[0]) is int)

  doys_calc = ymd2doy(numpy.array(ymds))
  assert(numpy.all(doys_calc == numpy.array(doys_test)))
  assert(type(doys_calc) is numpy.ndarray)
  assert(doys_calc.dtype == numpy.int64)


  from utilrsw.time.calendar import calendar

  for year in range(1804, 2401):
    calendar_dict = calendar(year)
    for month in range(1,13):
      for day in range(1, len(calendar_dict[month])+1):
        assert(ymd2doy([year, month, day]) == calendar_dict[month][day-1])


if __name__ == '__main__':
  ymd2doy_test()