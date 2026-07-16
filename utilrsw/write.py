from importlib.resources import path


def write_atomic(path, data):

  import os
  import json
  import pickle
  import warnings

  import numpy


def write(fname, data, atomic=False, logger=None):

  import os
  import csv
  import json
  import pickle
  import secrets

  import utilrsw

  utilrsw.mkdir(os.path.dirname(fname), logger=logger)

  if atomic:
    _base, _ext = os.path.splitext(fname)
    fname_tmp = f"{_base}.{secrets.token_hex(3)}.tmp{_ext}"
    # filename.json -> filename.abcdef.tmp.json
    try:
      write(fname_tmp, data, logger=logger)
      if logger is not None:
        logger.info(f"Renaming {fname_tmp} to {fname}")
      try:
        os.replace(fname_tmp, fname)
      except PermissionError:
        # On Windows, os.replace() raises PermissionError if the destination
        # file is open by another process.
        if logger is not None:
          msg = f"atomic write failed. File '{fname}' is open by another process. "
          msg += f"Removing temp file: '{fname_tmp}'."
          logger.error(msg)
        raise
    except Exception as e:
      if os.path.exists(fname_tmp):
        os.remove(fname_tmp)
      raise e
    return


  if logger is not None:
    logger.info(f"Writing {fname}")

  exto = os.path.splitext(fname)[1]
  if len(exto) == 1:
    # No extension.
    ext = '.txt'
  else:
    ext = exto.lower()

  if '.pkl' == ext:
    try:
      with open(fname, 'wb') as f:
        pickle.dump(data, f, protocol=4)
      _finish(fname, logger=logger)
      return
    except Exception as e:
      emsg = f"pickle.dump() raised: {e}"
      _finish(fname, logger=logger, e=e, emsg=emsg)

  if '.csv' == ext and type(data).__name__ == "DataFrame":
    # type(data)... used instead of isinstance(data, pandas.DataFrame),
    # so no pandas import needed.
    try:
      data.to_csv(fname, index=False, date_format="%Y-%m-%dT%H:%M:%S.%fZ")
      _finish(fname, logger=logger)
    except Exception as e:
      emsg = f"data.to_csv() raised: {e}"
      _finish(fname, logger=logger, e=e, emsg=emsg)
    return

  iscsv = isinstance(data, list) or isinstance(data, tuple)
  if '.csv' == ext and iscsv:
    if not isinstance(data[0], list) and not isinstance(data[0], tuple):
      # Assume data = ["a", "b", "c"] means one row.
      data = [data]
    try:
      with open(fname, 'w', newline='') as f:
        # https://github.com/python/cpython/issues/97503 for escapechar need
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerows(data)
        _finish(fname, logger=logger)
        return
    except Exception as e:
      try:
        with open(fname, 'w', newline='') as f:
          # https://github.com/python/cpython/issues/97503
          writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL, escapechar='\\')
          writer.writerows(data)
        _finish(fname, logger=logger)
        return
      except Exception as e:
        emsg = f"csv.writerows() raised: {e}"
        with open(fname, 'w', newline='') as f:
          writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
          for row in data:
            try:
              writer.writerow(row)
            except Exception as e:
              print(row)
              raise e
    return

  if '.json' == ext:
    try:
      data = _to_json_safe(data)
    except Exception as e:
      emsg = f"_to_json_safe() raised: {e}"
      _finish(fname, logger=logger, e=e, emsg=emsg)
    try:
      with open(fname, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
      _finish(fname, logger=logger)
    except Exception as e:
      emsg = f"json.dumps() raised: {e}"
      _finish(fname, logger=logger, e=e, emsg=emsg)
    return

  if not isinstance(data, str):
    emsg = f"Unknown data type: {type(data)} for file extension '{ext}'"
    raise ValueError(emsg)

  try:
    f = open(fname, 'w', encoding='utf-8')
  except Exception as e:
    os.remove(fname)
    emsg = f"f.open() raised: {e}"
    _finish(fname, logger=logger, e=e, emsg=emsg)

  try:
    f.write(data)
    _finish(fname, logger=logger)
  except Exception as e:
    os.remove(fname)
    emsg = f"Error writing {fname}: {e}"
    _finish(fname, logger=logger, e=e, emsg=emsg)

def _finish(fname, logger=None, e=None, emsg=None):
  if e is not None:
    if logger is not None:
      logger.error(emsg)
    else:
      print(emsg)
    raise e

  if logger is not None:
    logger.info(f"Wrote {fname}")

def _to_json_safe(obj):
  import datetime
  import numpy as np
  if isinstance(obj, np.ndarray):
    return [_to_json_safe(i) for i in obj.tolist()]
  if isinstance(obj, np.floating):
    return float(obj)
  if isinstance(obj, np.integer):
    return int(obj)
  if isinstance(obj, np.generic):
    return obj.item()
  if isinstance(obj, dict):
    return {(k.item() if isinstance(k, np.generic) else k): _to_json_safe(v) for k, v in obj.items()}
  if isinstance(obj, (list, tuple)):
    return [_to_json_safe(i) for i in obj]
  if isinstance(obj, (datetime.datetime, datetime.date)):
    return obj.isoformat()
  return obj

