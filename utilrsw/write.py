def write(fname, data, logger=None):

  import os
  import csv
  import json
  import pickle

  import utilrsw

  utilrsw.mkdir(os.path.dirname(fname), logger=logger)

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
      data = json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
      emsg = f"json.dumps() raised: {e}"
      _finish(fname, logger=logger, e=e, emsg=emsg)
    return

  if not isinstance(data, str):
    emsg = f"Unknown data type: {type(data)} for file extension '{ext}'"
    raise ValueError()

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
