import io
import json
import yaml
import pprint

import numpy

import utilrsw

def print_dict(d, sort_dicts=False, indent=0, style=None):

  print(format_dict(d, sort_dicts=sort_dicts, indent=indent, style=style))

def format_dict(d, sort_dicts=False, indent=0, style=None):

  if not isinstance(d, dict):
    return str(d)

  if sort_dicts:
    d = utilrsw.sort_dict(d)

  if style == 'json':
    return json.dumps(d, indent=2)

  if style == 'yaml':
    return yaml.dump(d)

  if style == 'pprint':
    pp = pprint.PrettyPrinter(depth=4, indent=0, compact=True)
    return pp.pformat(d)

  # TODO: There must be a library that does this. Find it. Note that yaml
  # does not handle non-string values.
  msg = ''
  for key, value in d.items():
    end = ''
    if isinstance(value, dict):
      end = '\n'
    msg += _print_to_string(' ' * indent + str(key), end=end)
    if isinstance(value, dict):
      msg += format_dict(value, sort_dicts=sort_dicts, indent=indent+1)
    else:
      if isinstance(value, str):
        msg += _print_to_string(f": '{value}'")
      else:
        if isinstance(value, list):
          if len(value) < 5:
            msg += _print_to_string(f": {value}")
          else:
            # TODO: If element is string, they are not quoted in the following. Fix this.
            msg += _print_to_string(f": [{value[0]}, {value[1]}, ..., {value[len(value)-2]}, {value[len(value)-1]} ({len(value)} elements)")
        elif isinstance(value, numpy.ndarray):
          if value.ndim == 1:
            if len(value) < 5:
              msg += _print_to_string(f": {value.tolist()}")
            else:
              msg += _print_to_string(f": [{value[0]}, {value[1]}, ..., {value[len(value)-2]}, {value[len(value)-1]}] ({len(value)} elements)")
          elif value.ndim == 2:
            if value.shape[0] < 5 and value.shape[1] < 5:
              msg += _print_to_string(f": {value.tolist()}")
            else:
              pad = ' ' * (indent + len(key) + 2)
              msg += _print_to_string(f": [{value[0,:]}]")
              msg += f"{pad}..."
              msg += f"\n{pad}[{value[value.shape[0]-1,:]}]"
              msg += f"\n{pad}({value.shape[0]} rows, {value.shape[1]} columns)"
              msg += "\n"
          else:
            msg += _print_to_string(f": {value}")
        else:
          msg += _print_to_string(f": {value}")
  return msg

def _print_to_string(*args, **kwargs):
  # https://stackoverflow.com/a/39823534
  output = io.StringIO()
  print(*args, file=output, **kwargs)
  contents = output.getvalue()
  output.close()
  return contents

if __name__ == "__main__":

  d = {
    "a": 1,
    "b": 2,
    "c": 3,
    "d": {
      "e": 4,
      "f": 5,
      "g": 6
    }
  }
  print_dict(d)
  print_dict(d, style='json')
  print_dict(d, style='yaml')
