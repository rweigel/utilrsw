def map_dict(d, mapping):
  from .get_path import get_path
  from .set_path import set_path
  result = {}
  for path in mapping:
    value = get_path(d, path, sep='/')
    if value is not None:
      set_path(result, value, mapping[path], sep='/')
  return result
