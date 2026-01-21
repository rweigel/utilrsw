def doy2md(year, doy):
  """Convert day of year to month and day.

  Args:
      year (int): The year (e.g., 2024).
      doy (int): The day of year (1-365 or 1-366 for leap years).

  Returns:
      tuple: A tuple containing the month (int) and day (int).
  """

  from utilrsw.time.is_leap_year import is_leap_year
  month_days = [31, 28 + is_leap_year(year), 31, 30, 31, 30,
                31, 31, 30, 31, 30, 31]

  month = 1
  for days_in_month in month_days:
    if doy <= days_in_month:
      day = doy
      return month, day
    else:
      doy -= days_in_month
      month += 1

def doy2md_test():

  from utilrsw.time.calendar import calendar
  from utilrsw.time.is_leap_year import is_leap_year

  for year in range(1804, 2401):
    calendar_dict = calendar(year)
    for doy in range(1, 366 + is_leap_year(year)):
      month, day = doy2md(year, doy)
      expected = calendar_dict[month][day-1]
      assert expected == doy, f"Failed for year={year}, doy={doy}: got month={month}, day={day}, expected doy={expected}"


if __name__ == "__main__":
  doy2md_test()