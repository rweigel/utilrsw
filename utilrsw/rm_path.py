def rm_paths(d, list_of_keys, sep=None, ignore_error=True):
  for keys in list_of_keys:
    rm_path(d, keys, sep=sep, ignore_error=ignore_error)

def rm_path(d, keys, sep=None, ignore_error=True):

  if sep is not None:
    if not isinstance(keys, str):
      raise ValueError("If sep is given, keys must be a string.")
    keys = keys.split(sep)
    if keys[-1] == '':
      keys = keys[:-1]

  # https://stackoverflow.com/a/74583007
  for k in keys[:-1]:
    if isinstance(k, list):
      raise ValueError("keys must be a string or a list of strings.")
    if k not in d:
      if ignore_error:
        return
      else:
        raise KeyError(k)
    d = d[k]

  if ignore_error:
    d.pop(keys[-1], None)
  else:
    d.pop(keys[-1])

if __name__ == '__main__':
  import deepdiff
  cases = [
    [
      {'a': {'b': {'c': 1}}},
      ['a', 'b'],
      {'a': {}}
    ],
    [
      {'a': {'b': {'c': 1}}},
      ['a', 'b'],
      {'a': {}}
    ],
    [
      {'a': {'b': {'c': 1, 'd': 2}}},
      ['a', 'b', 'c'],
      {'a': {'b': {'d': 2}}}
    ],
    [
      {'a': {'b': {'c': 1}}},
      ['a', 'x'],
      {'a': {'b': {'c': 1}}}
    ]
  ]
  for d, path, expected in cases:
    print(f"d = {d}")
    print(f"rm_path(d, {path})")
    rm_path(d, path)
    print(f"d = {d}")
    assert deepdiff.DeepDiff(d, expected) == {}
    print("")

  for d, path, expected in cases:
    path = "/".join(path)
    print(f"d = {d}")
    print(f"rm_path(d, {path})")
    rm_path(d, path)
    print(f"d = {d}")
    assert deepdiff.DeepDiff(d, expected) == {}
    print("")

  try:
    print(f"d = {d}")
    print(f"rm_path(d, {path}, ignore_error=False)")
    rm_path(d, ['a', 'x'], ignore_error=False)
  except KeyError as e:
    print(f"d = {d}")
    assert deepdiff.DeepDiff(d, {'a': {'b': {'c': 1}}}) == {}
    assert str(e) == "'x'"

  for d, path, expected in cases:
    print(f"d = {d}")
    print(f"rm_paths(d, [{path}, {path}])")
    rm_paths(d, [path, path])
    print(f"d = {d}")
    assert deepdiff.DeepDiff(d, expected) == {}
    print("")

  cases = [
    [
      {'a': {'b': {'c': 1, 'd': 2, 'e': 3}}},
      [['a', 'b', 'c'], ['a', 'b', 'd']],
      {'a': {'b': {'e': 3}}}
    ]
  ]

  for d, paths, expected in cases:
    print(f"d = {d}")
    print(f"rm_paths(d, {paths}])")
    rm_paths(d, paths)
    print(f"d = {d}")
    assert deepdiff.DeepDiff(d, expected) == {}
    print("")

  for d, paths, expected in cases:
    print(f"d = {d}")
    paths[0] = "/".join(paths[0])
    print(f"rm_paths(d, {paths}])")
    rm_paths(d, paths)
    print(f"d = {d}")
    assert deepdiff.DeepDiff(d, expected) == {}
    print("")
