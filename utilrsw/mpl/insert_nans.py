def insert_nans(times, matrix, max_gap=None):
  """Insert NaN values in matrix where time gaps in times are greater than max_gap."""

  import numpy

  # Compute time differences
  time_diffs = [t2 - t1 for t1, t2 in zip(times[:-1], times[1:])]

  # If max_gap is None, set to minimum time difference
  if max_gap is None:
    max_gap = min(time_diffs)

  # Identify indices where time gap exceeds max_gap
  gap_indices = [i for i, diff in enumerate(time_diffs) if diff > max_gap]

  # Add a time entry at each gap index for plotting purposes
  for idx in reversed(gap_indices):
    times.insert(idx + 1, times[idx] + time_diffs[idx] / 2)

  # Add row of NaNs at each gap index
  matrixc = matrix.copy()
  # Convert to float to allow NaN values
  matrixc = matrixc.astype(float)

  for idx in reversed(gap_indices):
    matrixc = numpy.insert(matrixc, idx + 1, numpy.nan, axis=0)

  return times, matrixc


def insert_nans_demo():
  import numpy
  from datetime import datetime, timedelta

  times = [datetime(2000,1,1)]
  for i in range(5):
    seconds = 1 if i != 2 else 3
    times.append(times[-1] + timedelta(seconds=seconds))

  matrix = numpy.array([[i, i+1] for i in range(5)])

  # Insert NaN where gap > 2 seconds
  new_times, new_matrix = insert_nans(times.copy(), matrix.copy(), max_gap=timedelta(seconds=2))

  print("Original times and matrix:")
  for t, row in zip(times, matrix):
    print(f"{t}: {row}")

  print("New times and matrix:")
  for t, row in zip(new_times, new_matrix):
    print(f"{t}: {row}")
