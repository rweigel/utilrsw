def calendar(year):

  import os

  from utilrsw.time.is_leap_year import is_leap_year

  if is_leap_year(year):
    file = "calendar.leap.txt"
  else:
    file = "calendar.nonleap.txt"

  file = os.path.join(os.path.dirname(__file__), file)
  calendar_dict = {}
  with open(file, "r") as f:
    month = 1
    for line in f:
      line = line.strip().split()[1:]
      calendar_dict[month] = [int(x) for x in line]
      month += 1

  return calendar_dict