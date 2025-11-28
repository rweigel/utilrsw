def is_leap_year(year):

  import numpy

  if isinstance(year, (list, tuple, numpy.ndarray)):
    if isinstance(year, (list, tuple)):
      return type(year)(is_leap_year(numpy.array(year)))
    if isinstance(year, numpy.ndarray):
      year = numpy.array(year)
      leap400 = numpy.where(year % 400 == 0, True, False)
      leap100 = numpy.where(year % 100 == 0, True, False)
      leap4 = numpy.where(year %4 == 0, True, False)
      cor1 = numpy.where(leap100, False, leap4)
      return numpy.where(leap400, True, cor1)
  else:
    year = int(year)
    if year % 100 == 0:
      return year % 400 == 0
    return year % 4 == 0


def is_leap_year_test():
  import os
  file = os.path.join(os.path.dirname(__file__), "is_leap_year.txt")
  with open(file, "r") as f:
    years = [int(line.strip()) for line in f if line.strip()]

  years_dict = dict.fromkeys(years, True)
  for y in range(years[0], years[-1]+1):
    if y in years_dict:
      assert is_leap_year(y), f"{y} should be a leap year"
    else:
      assert not is_leap_year(y), f"{y} should not be a leap year"

if __name__ == "__main__":
  is_leap_year_test()