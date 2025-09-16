def format_exponent(x, precision=1, exclude_range=None):
  """
  Format a number using LaTeX-formatted scientific notation (e.g., 10 = 1 \\cdot 10^{1}).

  kwargs:

    precision:  Number of decimal places to include in the base.

    exclude_range: If provided, the function will return the number
                   formatted in floating point notation (e.g., if  is in
                   exclude_range[0] <= 0.01 <= exclude_range[1], and
                   precision = 2, '0.01' is returned instead.

  Examples:

  >>> format_exponent(10, precision=0)
  '1 \\cdot 10^{1}'
  >>> format_exponent(100, precision=1)
  '1.0 \\cdot 10^{2}'
  >>> format_exponent(0.01, precision=2, exclude_range=(0.01, 1000))
  '0.01'
  >>> format_exponent(0.009, precision=2, exclude_range=(0.01, 1000))
  '9.00 \\cdot 10^{-3}'

  """
  if exclude_range is not None:
    if x >= exclude_range[0] and x <= exclude_range[1]:
      return f"{x:.{precision}f}"
  base, exponent = f"{x:.{precision}e}".split("e")
  return f"{base} \\cdot 10^{{{int(exponent)}}}"

def format_exponent_test():
  tests = {
    (100, 1, None): "1.0 \\cdot 10^{2}",
    (10, 1, None): "1.0 \\cdot 10^{1}",
    (1, 1, None): "1.0 \\cdot 10^{0}",
    (1e-1, 1, None): "1.0 \\cdot 10^{-1}",
    (1e-3, 1, None): "1.0 \\cdot 10^{-3}",
    (1e-10, 1, None): "1.0 \\cdot 10^{-10}",
    (110, 1, None): "1.1 \\cdot 10^{2}",
    (0.011, 2, None): "1.10 \\cdot 10^{-2}",
    (110, 0, None): "1 \\cdot 10^{2}",
    (0.01, 2, (0.01, 1000)): "0.01",
    (0.009, 2, (0.01, 1000)): "9.00 \\cdot 10^{-3}"
  }

  for test in tests:
    value, precision, exclude_range = test
    expected = tests[test]
    result = format_exponent(*test)
    print(f"x = {test[0]}, precision = {test[1]}, exclude_range = {test[2]}")
    print(f"  expected = {expected} result = {result}")
    assert result == expected, f"Failed for {test}: expected {expected}, got {result}"

if __name__ == "__main__":
  #import doctest
  #doctest.testmod()
  # Doctest not working b/c of issue with escaping with backslashes.
  print("Running format_exponent_test()")
  format_exponent_test()
