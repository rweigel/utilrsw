def flatten_dicts(d, parent_key='', sep='/'):
  """Flattens dict
    d = {
      'a': 1,
      'b': {
        'c': 2,
        'd': 3
      }
    }
    d = flatten_dict(d)
    d = {
      'a': 1,
      'b/c': 2,
      'b/d' 3
    }
    d = flatten_dict(d, sep='.')
    d = {
      'a': 1,
      'b.c': 2,
      'b.d' 3
    }
    d = flatten_dict(d, sep='.', parent_key='Z')
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
    sep = None

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
      items.extend(flatten_dicts(v, parent_key=new_key, sep=sep).items())
    else:
      items.append((new_key, v))

  return dict(items)

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
  print("flatten_dicts(d, sep='.')")
  utilrsw.print_dict(flatten_dicts(d, sep='.'))
  print("flatten_dicts(d, sep='.', parent_key='b')")
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
  print(10*"-")
