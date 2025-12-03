def ints2datetime(t):
  import datetime
  import numpy

  times = []
  for i in range(len(t)):
    times.append(datetime.datetime(*t[i]))

  if isinstance(t, (list, tuple)):
    return times

  return numpy.array(times)

