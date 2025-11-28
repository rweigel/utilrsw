def UTtoHMS(UT, **kwargs):
  """Convert universal time in fractional hours into integer hour, minutes, seconds.

  Example
  -------
  >>> from hxform import hxform as hx
  >>> print(hx.UTtoHMS(12))              # [12, 0, 0]
  >>> print(hx.UTtoHMS(24))              # [0, 0, 0]
  >>> print(hx.UTtoHMS(24, keep24=True)) # [24, 0, 0]
  """

  keep24 = False
  if 'keep24' in kwargs:
    keep24 = kwargs['keep24']

  if UT > 24 or UT < 0:
    raise ValueError('Required: 0 <= UT <= 24.')

  hours = int(UT)
  minutes = int((UT-hours)*60.)
  seconds = int(round((UT-hours-minutes/60.)*3600.))
  if seconds == 60:
    seconds = 0
    minutes = minutes + 1
  if minutes == 60:
    minutes = 0
    hours = hours + 1

  if hours == 24 and keep24 == False:
    return [0, 0, 0]

  return [hours, minutes, seconds]
