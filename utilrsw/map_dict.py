def map_dict(d, mapping):
  from .get_path import get_path
  from .set_path import set_path
  result = {}
  for path in mapping:
    value = get_path(d, path, sep='/')
    if value is not None:
      if isinstance(mapping[path], str):
        set_path(result, value, mapping[path], sep='/')
      elif isinstance(mapping[path], list):
        for p in mapping[path]:
          if isinstance(p, str):
            set_path(result, value, p, sep='/')
          else:
            raise ValueError(f"Target path in list is not a string: {p}")
      else:
        raise ValueError(f"Value is not a string or list of strings: {value}")
  return result
