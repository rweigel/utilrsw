def map_dict(d, mapping):
  result = {}
  for path in mapping:
    value = utilrsw.get_path(d, path, sep='/')
    if value is not None:
      utilrsw.set_path(result, value, mapping[path], sep='/')
  return result
