def merge_dicts(base, override, base_name='base', override_name='override', depth=0, verbose=True, logger=None, logger_indent=''):
  """Verbose merge of two dictionaries.

  Equivalent to {**base, **override}, but verbose and shows diffs.

  """
  import copy
  import json

  import deepdiff

  def xprint(msg):
    if not verbose:
      return
    if logger:
      logger.info(msg)
    else:
      print(msg)

  new = copy.deepcopy(base)
  for key, value in override.items():

    if isinstance(value, dict) and key in base and isinstance(base[key], dict):
      merge_dicts(base[key],
                  value,
                  base_name=base_name,
                  override_name=override_name,
                  depth=depth+1)
    else:
      if key not in base:
        msg = f"{logger_indent}Adding {key} = '{value}' from {override_name}"
        xprint(msg)
        new[key] = value
      else:
        msgo = f"{key} = '{override[key]}' in {override_name} is"
        if base[key] == value:
          if logger is not None:
            msg = f"{logger_indent}No update: {msgo} same as in {base_name}."
            logger.info(msg)
        else:
          new[key] = value
          msg = f"{logger_indent}Update:    {msgo} different from {base_name} '{base[key]}'. "
          msg += f"Using {override_name} value."
          if logger is not None:
            logger.info(msg)
  diff = deepdiff.DeepDiff(base, new, ignore_order=True)
  diff = json.loads(diff.to_json())
  if not diff and depth == 0 and logger is not None:
    logger.info(f"{logger_indent}No updates needed.")

  return new, diff
