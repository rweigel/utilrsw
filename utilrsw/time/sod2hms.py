def sod2hms(sod, microsecond=False):
  if not (sod >= 0 and sod < 86400):
    raise ValueError("sod >= 0 and sod < 8600 required.")

  hour = sod // 3600
  minute = sod % 3600 // 60
  second = sod % 60

  if microsecond:
    second_int = int(second)
    microsec = int(round((second - second_int) * 1e6))
    return hour, minute, second_int, microsec

  return hour, minute, int(second)

if __name__ == "__main__":
  for sod in range(0, 86400):
    h, m, s = sod2hms(sod+0.1)
    print(f"SOD: {sod} -> {h}, {m}, {s}")