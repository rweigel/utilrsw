def set_path(d, value, path, sep='.'):
  """ Set a value in a nested dict/list structure given a path."""

  if isinstance(path, str):
    if sep in path:
      path = path.split(sep)
    else:
      path = [path]

  obj = d
  for i in range(0, len(path)):
    key = path[i]

    if i == len(path) - 1:
      # Last element in path, set the value
      if isinstance(key, int):
        # Ensure obj is a list
        if not isinstance(obj, list):
          raise ValueError(f"Expected list at path {'/'.join(path[:i])}, got {type(obj)}")
        # Expand list if needed
        while len(obj) <= key:
          obj.append(None)
        obj[key] = value
      else:
        # Ensure obj is a dict
        if not isinstance(obj, dict):
          raise ValueError(f"Expected dict at path {'/'.join(path[:i])}, got {type(obj)}")
        obj[key] = value
    else:
      # Intermediate element in path, ensure the structure exists
      if isinstance(key, int):
        # Ensure obj is a list
        if not isinstance(obj, list):
          raise ValueError(f"Expected list at path {'/'.join(path[:i])}, got {type(obj)}")
        # Expand list if needed
        while len(obj) <= key:
          obj.append(None)
        if obj[key] is None:
          # Create a new dict for the next level
          obj[key] = {}
        obj = obj[key]
      else:
        # Ensure obj is a dict
        if not isinstance(obj, dict):
          raise ValueError(f"Expected dict at path {'/'.join(path[:i])}, got {type(obj)}")
        if key not in obj or obj[key] is None:
          # Create a new dict for the next level
          obj[key] = {}
        obj = obj[key]

  return d

def get_path_test():
  obj = {
    "a": {
      "b": {
        "c": [1, 2, 3],
        "d": {
          "e": "old"
        }
      }
    }
  }
  assert set_path(obj, "new", ["a", "b", "d", "e"])['a']['b']['d']['e'] == "new"
  assert set_path(obj, "99", ["a", "b", "c", 0])['a']['b']['c'] == [ "99", 2, 3]

if __name__ == "__main__":
  get_path_test()