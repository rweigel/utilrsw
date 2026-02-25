def isoduration_to_timedelta(duration, start=None, end=None):
  # Convert ISO 8601 duration to timedelta
  import datetime
  import isodate

  parsed = isodate.parse_duration(duration)
  if isinstance(parsed, datetime.timedelta):
    return parsed

  return parsed.totimedelta(start=start, end=end)

def isoduration_to_timedelta_test():
  import datetime
  tests = [
    {
       "duration": "PT1S",
       "expected": datetime.timedelta(seconds=1)
    },
    {
      "duration": "PT1M1S",
      "expected": datetime.timedelta(minutes=1, seconds=1)
    },
    {
      "duration": "P1Y1D",
      "expected": datetime.timedelta(hours=24*366 + 24),
      "start": datetime.datetime(2020, 1, 1)
    }
  ]

  for test in tests:
    duration = test["duration"]
    expected = test["expected"]
    start = test.get("start", None)
    result = isoduration_to_timedelta(duration, start=start)
    assert result == expected, f"Test failed for duration: {duration}. Expected: {expected}, Got: {result}"
  print("All tests passed.")

if __name__ == "__main__":
  isoduration_to_timedelta_test()
