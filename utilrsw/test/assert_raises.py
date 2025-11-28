def assert_raises(exc_type, func, args, match=None, **kwargs):
  """Call a function and assert that it raises an exception.

  Args:
    exc_type (Exception): _expected exception type
    func (function): _function to call_
    args (list): _call function using func(*args)_
    match (str, optional): _string to match in exception message_. Defaults to None.

  Raises:
    AssertionError: _Expected assertion to raise exc_type_
    AssertionError: _Exception message does not match_
    AssertionError: _Exception not raised_

  Examples:
    # Assert that ValueError is raised when calling myfunc(arg1, arg2)
    assert_raises(ValueError, myfunc, [arg1, arg2])

    # Assert that ValueError is raised with message containing 'invalid value'
    # when calling myfunc(arg1, arg2)
    assert_raises(ValueError, myfunc, [arg1, arg2], match='invalid value')
  """
  try:
    func(*args, **kwargs)
  except Exception as e:
    if not isinstance(e, exc_type):
      emsg = f"Expected assertion to raise {exc_type}, got {type(e)}"
      raise AssertionError(emsg)
    if match and match not in str(e):
      raise AssertionError(f"Exception message '{str(e)}' does not contain '{match}'")
    return e
  raise AssertionError(f"{exc_type} not raised")
