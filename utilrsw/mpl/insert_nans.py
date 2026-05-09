def insert_nans(x, matrix, x_thresh=None, y_thresh=None):
  """Insert NaN values in matrix where x or y gaps are greater than a threshold.

  For preventing Matplotlib from connecting points across large gaps.

  Parameters:
    x: list of `x` values (e.g. datetime objects or numeric timestamps)

    matrix: 2D array-like of shape (nr, nc) or 1D array-like of shape (n,)

    x_thresh: threshold for x gaps. If a gap between consecutive entries in
              `x` exceeds this threshold, a NaN will be inserted in the
              corresponding row of `matrix`. If None, no NaNs will be inserted
              based on time gaps. If 'min', the minimum `x` gap will be
              used as the threshold.

    y_thresh: threshold for value gaps. If the absolute difference between
              consecutive entries in `matrix` exceeds this threshold, a NaN
              will be inserted in the corresponding row of `matrix`. Only
              applicable if `matrix` is 1D or has only one column. If None,
              no NaNs will be inserted.

  """

  import numpy

  matrixc = matrix.copy().astype(float)

  if len(x) < 2:
    return list(x), matrixc

  y_values = None
  if y_thresh is not None:
    if matrixc.ndim == 1:
      y_values = matrixc
    else:
      if matrixc.shape[1] != 1:
        raise ValueError("y_thresh requires matrix to have exactly one column")
      y_values = matrixc[:, 0]

  # Compute x differences
  x_diffs = [t2 - t1 for t1, t2 in zip(x[:-1], x[1:])]

  unique_diffs, counts = numpy.unique(x_diffs, return_counts=True)
  # Set x_thresh to most common x difference if not provided
  if x_thresh is None:
    x_thresh = unique_diffs[numpy.argmax(counts)]
    #print(f"  No x_thresh provided, using most common x difference: {max_gap}")

  if False:
    print("Time difference histogram:")
    for diff, count in zip(unique_diffs, counts):
      print(f"  {diff}: {count} occurrences")

  # If x_thresh is None, set to minimum x difference
  if isinstance(x_thresh, str) and x_thresh.lower() == 'min':
    x_thresh = min(x_diffs)

  # Identify indices where x gap exceeds x_thresh
  gap_indices = {i for i, diff in enumerate(x_diffs) if diff > x_thresh}

  # Identify indices where y gap exceeds y_thresh
  if y_values is not None:
    y_diffs = numpy.abs(numpy.diff(y_values))
    gap_indices.update(i for i, diff in enumerate(y_diffs) if diff > y_thresh)

  gap_indices = sorted(gap_indices)

  # Insert NaN in x and matrix at identified gap indices
  xc = list(x)
  for idx in reversed(gap_indices):
    gap_x = xc[idx] + (xc[idx + 1] - xc[idx]) / 2
    xc.insert(idx + 1, gap_x)

  for idx in reversed(gap_indices):
    matrixc = numpy.insert(matrixc, idx + 1, numpy.nan, axis=0)

  return xc, matrixc


def insert_nans_demo():
  import numpy
  from datetime import datetime, timedelta


  def _run_demo(x, matrix, x_thresh=None, y_thresh=None):
    new_x, new_matrix = insert_nans(x, matrix, x_thresh=x_thresh, y_thresh=y_thresh)

    print("Original x and matrix rows:")
    for t, row in zip(x, matrix):
      print(f"  {t}: {row}")

    print(f"New x and matrix rows; x_thresh={x_thresh}, y_thresh={y_thresh}:")
    for t, row in zip(new_x, new_matrix):
      print(f"  {t}: {row}")


  # datetime time gap
  x = [datetime(2000,1,1)]
  for i in range(5):
    seconds = 1 if i != 2 else 3
    x.append(x[-1] + timedelta(seconds=seconds))

  matrix = numpy.array([[i, i+1] for i in range(5)])
  x_thresh = timedelta(seconds=2)
  _run_demo(x, matrix, x_thresh=x_thresh, y_thresh=None)

  # integer time gap
  x = [0, 1, 2, 5, 6]
  matrix = numpy.array([[i, i + 10] for i in range(len(x))])
  _run_demo(x, matrix, x_thresh=1, y_thresh=None)

  # y value gap
  x = [0, 1, 2, 3, 4]
  matrix = numpy.array([0.0, 1.0, 2.0, 10.0, 11.0])
  _run_demo(x, matrix, x_thresh=None, y_thresh=5)


if __name__ == "__main__":
  insert_nans_demo()
