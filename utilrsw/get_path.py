def get_path(obj, path, default=None, sep='.'):

  if obj is None:
    return default

  if isinstance(path, str):
    if sep in path:
      path = path.split(sep)
    else:
      path = [path]

  for key in path:
    if obj is None:
      return default

    if key == '':
      return obj

    if not isinstance(obj, dict):
      if not isinstance(obj, list):
        if not isinstance(obj, tuple):
          return default

    if isinstance(key, int):
      if not isinstance(obj, list):
        return default
      if key < 0:
        key = len(obj) + key
      if key < 0 or key > len(obj) - 1:
        return default

    if isinstance(obj, dict):
      if key not in obj:
        return default

    obj = obj[key]

  return obj

def get_path_test():
  obj = {
    "a": {
      "b": {
        "c": [1, 2, 3],
        "d": {
          "e": "hello"
        }
      }
    }
  }

  assert get_path(obj, [""]) == obj

  assert get_path(obj, "a.b.c") == [1, 2, 3]
  assert get_path(obj, "a/b/c", sep='/') == [1, 2, 3]
  assert get_path(obj, "a.x") is None
  assert get_path(obj, "a.x.y") is None

  assert get_path(obj, ["a", "b", "c"]) == [1, 2, 3]
  assert get_path(obj, ["a", "b", "d"]) == {"e": "hello"}

  assert get_path(obj, ["a", "b", "c", 0]) == 1
  assert get_path(obj, ["a", "b", "c", -3]) == 1
  assert get_path(obj, ["a", "b", "c", 1]) == 2
  assert get_path(obj, ["a", "b", "c", -2]) == 2
  assert get_path(obj, ["a", "b", "c", 2]) == 3
  assert get_path(obj, ["a", "b", "c", -1]) == 3

  assert get_path(obj, ["a", "b", "c", 3]) is None
  assert get_path(obj, ["a", "b", "c", -4]) is None

if __name__ == "__main__":
  get_path_test()
  #print("All tests passed.")