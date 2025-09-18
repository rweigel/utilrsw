def timedelta_to_isoduration(td):
  """Converts a timedelta object to an ISO 8601 duration string (H, M, S only)."""

  # See also https://stackoverflow.com/a/77958275/1491619
  # Alternative is to use timedelta_isoformat package, but it returns shortest
  # duration string, e.g., milliseconds=7272000 -> PT7272S, not PT2H1M12S.

  # Negative durations are not typically represented this way; handle as absolute.
  is_negative = td.total_seconds() < 0
  td_abs = abs(td)

  hours, remainder = divmod(td_abs.seconds, 3600)
  minutes, seconds = divmod(remainder, 60)

  parts = []
  if td_abs.days > 0:
      parts.append(f"{td_abs.days}D")
  if hours > 0:
      parts.append(f"{hours}H")
  if minutes > 0:
      parts.append(f"{minutes}M")
  if seconds > 0 or td_abs.microseconds > 0:
      # Include microseconds if they exist
      if td_abs.microseconds > 0:
          seconds_with_micros = seconds + td_abs.microseconds / 1e6
          parts.append(f"{seconds_with_micros:.6f}".rstrip('0').rstrip('.') + "S")
      else:
          parts.append(f"{seconds}S")

  if not parts:
      return "PT0S"

  if td_abs.days > 0:
      if len(parts) > 1:
          result = "P" + parts[0] + "T" + "".join(parts[1:])
      else:
        result = "P" + parts[0]
  else:
      result = "PT" + "".join(parts)

  return f"-{result}" if is_negative else result


def timedelta_to_isoduration_test():
  from timedelta_to_isoduration import timedelta_to_isoduration
  from datetime import timedelta

  if False:
    # Demonstrate how timedelta.isoformat() returns shortest duration string.
    import timedelta_isoformat
    print(timedelta_isoformat.timedelta(milliseconds=7272000).isoformat())
    # PT7272S
    print(timedelta_to_isoduration(timedelta(milliseconds=7272000)))
    # PT2H1M12S

  test_cases = [
      (timedelta(seconds=30), "PT30S"),
      (timedelta(seconds=3661), "PT1H1M1S"),
      (timedelta(seconds=0.5), "PT0.5S"),
      (timedelta(days=1, hours=2, minutes=3, seconds=4), "P1DT2H3M4S"),
      (timedelta(days=-1, hours=-2, minutes=-3, seconds=-4), "-P1DT2H3M4S"),
      (timedelta(seconds=-45), "-PT45S"),
      (timedelta(microseconds=500000), "PT0.5S"),
      (timedelta(), "PT0S")
  ]
  for td, expected in test_cases:
      result = timedelta_to_isoduration(td)
      assert result == expected, f"Expected {expected}, got {result}"
  print("All tests passed.")

if __name__ == "__main__":
  timedelta_to_isoduration_test()