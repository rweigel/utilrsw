def flatten_dicts(d, parent_key='', sep='/', simplify=False):
  """Flattens dict
    d = {
      'a': 1,
      'b': {
        'c': 2,
        'd': 3
      }
    }
    d = flatten_dicts(d)
    d = {
      'a': 1,
      'b/c': 2,
      'b/d' 3
    }
    d = flatten_dicts(d, sep='.')
    d = {
      'a': 1,
      'b.c': 2,
      'b.d' 3
    }
    d = flatten_dicts(d, sep='.', parent_key='Z')
    d = {
      'Z.a': 1,
      'Z.b.c': 2,
      'Z.b.d' 3
    }
  """
  if sep is None:
    df = flatten_dicts(d, sep='')
    keys_joined = "".join(list(df.keys()))
    possible_seps = ['/', '.', '_', '-', '#', '|', '&', '+', '%', '!']

    for n in range(1, 11):
      for possible_sep in possible_seps:
        if n*possible_sep not in keys_joined:
          return flatten_dicts(d, parent_key=parent_key, sep=n*possible_sep)
      if sep is None:
        emsg = f"Could not find a unique sep string. Tried {possible_seps}"
        emsg =+ " and 2-10 repeats of each element in list."
        raise ValueError(emsg)

  items = []
  for k, v in d.items():
    new_key = parent_key + sep + k if parent_key else k

    if isinstance(v, dict):
      items.extend(flatten_dicts(v, parent_key=new_key, sep=sep, simplify=simplify).items())
    else:
      items.append((new_key, v))

  if simplify:
    keys = [item[0] for item in items]
    simplified_keys = _simplify_keys(keys, sep)
    items = [(simplified_keys[i], items[i][1]) for i in range(len(items))]

  return dict(items)


def _simplify_keys(keys, sep):
  """
  Trim off leading parts from keys such that resulting list is still unique.
  Examples: ["a/0", "a/1", "b/0"] -> ["0", "1", "b/0"]
  Examples: ["a/a/0", "a/b/0"] -> ["a/0", "b/0"]
  """
  if not keys or len(keys) <= 1:
    return keys

  # Split all keys into parts
  split_keys = [key.split(sep) for key in keys]
  max_parts = max(len(parts) for parts in split_keys)

  # Try removing leading parts, starting from 1 part, then 2, etc.
  for parts_to_remove in range(1, max_parts):
    # Create simplified keys by removing leading parts
    simplified = []
    for parts in split_keys:
      if len(parts) > parts_to_remove:
        # Remove leading parts
        new_parts = parts[parts_to_remove:]
        simplified.append(sep.join(new_parts))
      else:
        # If removing would result in empty key, keep original
        simplified.append(sep.join(parts))

    # Check if simplified keys are still unique
    if len(set(simplified)) == len(simplified):
      return simplified

  # If no simplification possible while maintaining uniqueness, return original
  return keys


if __name__ == '__main__':
  import utilrsw

  d = {
    'a': 1,
    'b': {
      'c': 2,
      'd': 3
    }
  }

  print(10*"-")
  print("d = ")
  utilrsw.print_dict(d, indent=2)

  print('flatten_dicts(d)')
  utilrsw.print_dict(flatten_dicts(d))

  print('flatten_dicts(d, simplify=True)')
  utilrsw.print_dict(flatten_dicts(d, simplify=True))

  print("flatten_dicts(d, sep='.')")
  utilrsw.print_dict(flatten_dicts(d, sep='.'))

  print("flatten_dicts(d, sep='.', parent_key='Z')")
  utilrsw.print_dict(flatten_dicts(d, sep='.', parent_key='Z'))

  print(10*"-")

  d = {
    'a/u': 1,
    'b/v': {
      'c/x': 2,
      'd/y': 3
    }
  }

  print("d = ")
  utilrsw.print_dict(d, indent=2)

  print("flatten_dicts(d, sep=None)")
  utilrsw.print_dict(flatten_dicts(d, sep=None))

  d = {
    'a': {
      "0": 0,
      "1": 1
    },
    'b': {
      "0": 1,
    }
  }

  print("flatten_dicts(d, simplify=True)")
  utilrsw.print_dict(flatten_dicts(d, simplify=True))

  print(10*"-")
