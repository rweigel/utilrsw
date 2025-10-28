
import numpy

import utilrsw

def print_dict(d: dict, sort_dicts=False, indent=0, style=None) -> None:
  """Print result of format_dict() to stdout."""
  print(format_dict(d, sort_dicts=sort_dicts, indent=indent, style=style))


def format_dict(d: dict, sort_dicts=False, indent=0, style=None) -> str:
  """Format a dictionary for printing"""
  if not isinstance(d, dict):
    return str(d)

  styles = ['json', 'yaml', 'pprint', None]
  if style not in styles:
    msg = f"Unknown style '{style}'. Must be one of {styles}."
    raise ValueError(msg)

  if sort_dicts:
    d = utilrsw.sort_dict(d)

  if style == 'json':
    import json
    return json.dumps(d, indent=2)

  if style == 'yaml':
    import yaml
    return yaml.dump(d)

  if style == 'pprint':
    import pprint
    pp = pprint.PrettyPrinter(indent=0, depth=4, width=1, compact=True)
    return pp.pformat(d)

  # TODO: There must be a library that does this. Find it. Note that yaml
  # does not handle non-string values.
  msg = ''
  for key, value in d.items():
    end = ''
    if isinstance(value, dict):
      end = '\n'
    msg += _print_to_string(f"{' '*indent}{key}: ", end=end)
    if isinstance(value, dict):
      msg += format_dict(value, sort_dicts=sort_dicts, indent=indent+1)
      msg += '\n'
    else:
      if isinstance(value, str):
        msg += _print_to_string(f"'{value}'")
      else:
        if isinstance(value, list):
          if len(value) < 5:
            msg += _print_to_string(f"{value}")
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
          msg += _print_to_string(f"{value}")

  return msg.rstrip('\n')

def _print_to_string(*args, **kwargs):
  # https://stackoverflow.com/a/39823534
  import io
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

  print(10*"-")
  print("d = ")
  print(d)
  print("")
  print('print_dict(d)')
  print_dict(d)
  print("print_dict(d, style='json')")
  print_dict(d, style='json')
  print("print_dict(d, style='yaml')")
  print_dict(d, style='yaml')
  print("print_dict(d, style='pprint')")
  print_dict(d, style='pprint')
  print(10*"-")
  d = {
    "a": ['a', 1.2, 3, 4, 5, 6, 7],
    "d": {
      "e": [1, 2, 3, 4, 5, 'x', print_dict],
    }
   }
  print_dict(d)
