def datetime_list(dto, dtf, dt_delta):
  import numpy
  import datetime

  t = []
  delta = datetime.timedelta(**dt_delta)
  i = 0
  while True:
    dt = dto + i*delta
    i = i + 1
    t.append([dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond])
    if dt >= dtf:
      break

  return numpy.array(t)

