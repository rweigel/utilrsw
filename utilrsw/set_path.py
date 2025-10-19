from typeguard import typechecked
from typing import Any, Union, List, Dict

@typechecked
def set_path(
              d: Union[Dict[Any, Any], List[Any]],
              value: Any,
              path: Union[str, List[Union[str, int]]],
              sep: str = '.'
            ) -> Union[Dict[Any, Any], List[Any]]:
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
          emsg = f"Expected list at path {'/'.join(path[:i])}, got {type(obj)}"
          raise ValueError(emsg)
        # Expand list if needed
        while len(obj) <= key:
          obj.append(None)
        obj[key] = value
      else:
        # Ensure obj is a dict
        if not isinstance(obj, dict):
          emsg = f"Expected dict at path {'/'.join(path[:i])}, got {type(obj)}"
          raise ValueError(emsg)
        obj[key] = value
    else:
      # Intermediate element in path, ensure the structure exists
      if isinstance(key, int):
        # Ensure obj is a list
        if not isinstance(obj, list):
          emsg = f"Expected list at path {'/'.join(path[:i])}, got {type(obj)}"
          raise ValueError()
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
          emsg = f"Expected dict at path {'/'.join(path[:i])}, got {type(obj)}"
          raise ValueError(emsg)
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