import os
import sys
import time
import atexit
import inspect
import datetime
import traceback

import logging
import logging.config

_registered_cleanups = set()


def logger(name=None,
           log_level='INFO',
           console_format=u"%(asctime)s %(levelname)s %(name)s %(message)s",
           console_level=None,
           log_dir=None,
           file_format=u"%(asctime)s %(levelname)s %(name)s %(message)s",
           file_level=None,
           file_log=None,
           file_error=None,
           file_exception=None,
           datefmt="%Y-%m-%dT%H:%M:%S.%f",
           utc_timestamps=True,
           rm_existing=True,
           rm_empty=True,
           rm_string='',
           color=None,
           disable_existing_loggers=False,
           debug_logger=False):
  """Create and return a configured logging.Logger instance.

  Parameters
  ----------
  name : str, optional
      Logger name. Defaults to the calling module's ``__name__``.
  log_level : str
      Root log level (e.g. ``'DEBUG'``, ``'INFO'``). Default ``'INFO'``.
  log_dir : str, optional
      Directory for log files. No file logging when ``None``.

  console_format : str
      Format string for console (stderr) output.
  console_level : str, optional
      Console handler level. Defaults to ``log_level``.
  color : bool, optional
      Colorize console output. Auto-detected when ``None``.

  file_format : str
      Format string for file output.
  file_level : str, optional
      File handler level. Defaults to ``log_level``.
  file_log : str, optional
      Path to the main log file. Derived from ``name`` when ``None``.
  file_error : str or False, optional
      Path to the error log file. Derived from ``file_log`` when ``None``.
      Pass ``False`` to suppress the error log file.
  file_exception : str, optional
      Path to the exception log file. Derived from ``name`` when ``None``.

  datefmt : str
      ``strftime`` format for timestamps.
  utc_timestamps : bool
      Use UTC timestamps. Default ``True``.

  rm_existing : bool
      Remove existing log files on startup. Default ``True``.
  rm_empty : bool
      Remove empty log files on exit. Default ``True``.
  rm_string : str
      String stripped from status messages.

  disable_existing_loggers : bool
      Passed to ``logging.config.dictConfig``. Default ``False``.
  debug_logger : bool
      Log internal logger setup details. Default ``False``.

  Returns
  -------
  logging.Logger
  """

  if debug_logger:
    frame = inspect.currentframe()
    kwargs = frame.f_locals


  class CustomFormatter(logging.Formatter):
    converter = datetime.datetime.fromtimestamp

    def __init__(self, datefmt=datefmt, color=color, name=name, *args, **kwargs):
      if debug_logger:
        print("  logger.CustomFormatter().__init__ called for", name)
        print(f"    self.name: '{name}'")
        print(f"    self.color: '{color}'")
        print(f"    self.datefmt: '{datefmt}'")
      super(CustomFormatter, self).__init__(*args, **kwargs)
      self.color = color
      self.datefmt = datefmt
      self.name = name

    def formatTime(self, record, datefmt=None):
      ct = self.converter(record.created)
      if datefmt:
          s = ct.strftime(datefmt)
      else:
        s = ct.strftime("%Y-%m-%dT%H:%M:%S.%f")
      if utc_timestamps:
        s = s + "Z"
      return s

    def format(self, record):
      if debug_logger:
        print(f"  logger.CustomFormatter().format called for {self.name}")

      if hasattr(record, "threadName"):
        record.threadName = record.threadName.replace("ThreadPoolExecutor-0_", "T")

      levelname_original = record.levelname
      if self.color:
        if debug_logger:
          print(f"    Applying color to record.levelname = '{record.levelname}'")
        record.levelname = self.color_levelname(record.levelname)
        if debug_logger:
          print(f"    record.levelname: '{record.levelname}'")
      else:
        record.levelname = self.pad_levelname(record.levelname)
        if debug_logger:
          print(f"    Not applying color to record.levelname = '{record.levelname}'")

      ret = logging.Formatter.format(self, record)
      record.levelname = levelname_original

      ret = ret.replace(rm_string, "")
      if debug_logger and self.name == 'file_stdout':
        print(f"   Writing to file_stdout: '{ret}'")
      if debug_logger and self.name == 'file_stderr':
        print(f"   Writing to file_stderr: '{ret}'")
      return ret

    def pad_levelname(self, levelname):
      if levelname == 'DEBUG':
        return 'DEBUG'
      if levelname == 'INFO':
        return 'INFO '
      if levelname == 'WARNING':
        return 'WARN '
      if levelname == 'ERROR':
        return 'ERROR'
      if levelname == 'CRITICAL':
        return 'CRIT '

    def color_levelname(self, levelname):
      if levelname.startswith('\033'):
        return levelname
      if levelname == 'DEBUG':
        return '\033[94m' + self.pad_levelname(levelname) + '\033[0m'
      if levelname == 'INFO':
        return '\033[92m' + self.pad_levelname(levelname) + '\033[0m'
      if levelname == 'WARNING':
        return '\033[93m' + self.pad_levelname(levelname) + '\033[0m'
      if levelname == 'ERROR':
        return '\033[91m' + self.pad_levelname(levelname) + '\033[0m'
      if levelname == 'CRITICAL':
        return '\033[95m' + self.pad_levelname(levelname) + '\033[0m'
      return levelname


  class ExcludeErrorsFilter(logging.Filter):
    def filter(self, record):
      """Only show log messages with log level below ERROR."""
      return record.levelno < logging.ERROR


  class IncludeErrorsFilter(logging.Filter):
    def filter(self, record):
      """Only show log messages with log level ERROR or higher."""
      return record.levelno >= logging.ERROR


  def logger_name():
    if debug_logger:
      msg = "No logger name provided, using sys.argv[0] and inspect.stack() "
      msg += "to determine name."
      print()
      for idx, frame in enumerate(inspect.stack()):
        print(f"  Frame {idx}: {frame.frame}")

    import pathlib
    script = (sys.argv[0] if sys.argv else '') or ''
    script_name = pathlib.Path(script).name

    if script_name and script_name not in ('-c', '-m'):
      if script_name.endswith('.py'):
        script_name = script_name[:-3]
      return script_name

    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    if module and hasattr(module, '__file__'):
      name = os.path.splitext(os.path.basename(module.__file__))[0]
    else:
      name = '__main__'

    return name


  def setLevel(self, level):
    # Accept either numeric or string levels (e.g., 10 or "DEBUG").
    level_no = logging._checkLevel(level)
    for handler in self.handlers:
      # Keep error-only handlers pinned at ERROR so .errors.log and stderr
      # never receive INFO/DEBUG records when lowering logger level.
      is_error_file = False
      if file_error and isinstance(handler, logging.FileHandler):
        try:
          a = os.path.abspath(handler.baseFilename)
          b = os.path.abspath(file_error)
          is_error_file = a == b
        except Exception:
          is_error_file = False

      is_stderr_stream = (
        isinstance(handler, logging.StreamHandler)
        and not isinstance(handler, logging.FileHandler)
        and getattr(handler, 'stream', None) is sys.stderr
      )

      if is_error_file or is_stderr_stream:
        handler.setLevel(logging.ERROR)
      else:
        handler.setLevel(level_no)


  log_level = log_level.upper()
  if console_level is None:
    console_level = log_level
  if file_level is None:
    file_level = log_level

  if utc_timestamps:
    logging.Formatter.converter = time.gmtime

  if name is None:
    name = logger_name()

  if file_log is None:
    file_log = name + ".log"

  if file_exception is None:
    base, ext = os.path.splitext(file_log)
    file_exception = base + f".exceptions{ext}"

  if file_error is None:
    base, ext = os.path.splitext(file_log)
    file_error = base + f".errors.{ext.lstrip('.')}"

  if not os.path.isabs(file_log) and log_dir is not None:
    file_log = os.path.join(log_dir, file_log)
  if not os.path.isabs(file_exception) and log_dir is not None:
    file_exception = os.path.join(log_dir, file_exception)
  if file_error and not os.path.isabs(file_error) and log_dir is not None:
    file_error = os.path.join(log_dir, file_error)

  def _remove_or_truncate(path):
    """Remove a log file, or truncate it on Windows if the file is locked."""
    if not os.path.exists(path):
      return
    try:
      os.remove(path)
    except PermissionError:
      # Windows: file is locked by another process; truncate instead.
      try:
        open(path, 'w').close()
      except PermissionError:
        pass

  if rm_existing:
    _remove_or_truncate(file_log)
    _remove_or_truncate(file_exception)
    if file_error:
      _remove_or_truncate(file_error)

  def cleanup(file_log=file_log, file_error=file_error, file_exception=file_exception):
    def _rm_if_empty(path):
      if not path:
        return
      if os.path.exists(path) and os.path.getsize(path) == 0:
        _logger.debug(f"Removing empty log file: {path}")
        os.remove(path)

    for file in [file_log, file_error, file_exception]:
      if file and os.path.exists(file) and os.path.getsize(file) == 0:
        _logger.debug(f"Removing empty log file: {file}")
        os.remove(file)
      if file and os.path.exists(file) and os.path.getsize(file) > 0:
        _logger.info(f"Wrote file '{file}' ({os.path.getsize(file)} bytes)")

    _rm_if_empty(file_log)
    _rm_if_empty(file_error)
    _rm_if_empty(file_exception)

    logging.shutdown()

  from . import mkdir as mkdir
  if file_log:
    mkdir(os.path.dirname(file_log))
  if file_exception:
    mkdir(os.path.dirname(file_exception))
  if file_error:
    mkdir(os.path.dirname(file_error))


  handlers = ['console_stderr', 'console_stdout', 'file_stdout']

  if file_error is not False:
    handlers.append('file_stderr')

  # Based on https://stackoverflow.com/a/66728490
  config = {
      'version': 1,
      'disable_existing_loggers': disable_existing_loggers,
      'filters': {
          'exclude_errors': {
              '()': ExcludeErrorsFilter
          },
          'include_errors': {
            '()': IncludeErrorsFilter
          }
      },
      'formatters': {
          'console_formatter': {
            "class": "logging.Formatter",
            "datefmt": datefmt,
            "format": console_format
           },
          'file_formatter': {
            "class": "logging.Formatter",
            "datefmt": datefmt,
            'format': file_format
          }
      },
      'handlers': {
          'console_stderr': {
              # Sends log messages with log level ERROR or higher to stderr
              'class': 'logging.StreamHandler',
              'level': 'ERROR',
              'formatter': 'console_formatter',
              'filters': ['include_errors'],
              'stream': sys.stderr
          },
          'file_stderr': {
              # Sends all log messages to a file
              'class': 'logging.FileHandler',
              'level': 'ERROR',
              'formatter': 'file_formatter',
              'filters': ['include_errors'],
              'filename': file_error,
              'encoding': 'utf8'
          },
          'console_stdout': {
              # Sends log messages with log level lower than ERROR to stdout
              'class': 'logging.StreamHandler',
              'level': console_level,
              'formatter': 'console_formatter',
              'filters': ['exclude_errors'],
              'stream': sys.stdout
          },
          'file_stdout': {
              # Sends all log messages to a file
              'class': 'logging.FileHandler',
              'level': file_level,
              'formatter': 'file_formatter',
              'filename': file_log,
              'encoding': 'utf8'
          }
      },
      'loggers': {
          name: {
              'level': 'DEBUG',
              'handlers': handlers,
              'propagate': False
          }
      },
      'xroot': {
          # Docs say:
          #   In general, this should be kept at 'NOTSET'. Otherwise
          #   it would interfere with the log levels set for each handler.
          # However, this leads to duplicate log messages.
          'level': 'NOTSET',
          'handlers': handlers
      }
  }


  if debug_logger:
    print(f"Initializing logger with name='{name}'")
    print("  kwargs:")
    for key, value in kwargs.items():
      if key == 'frame':
        continue
      print(f"    {key}: {value}")

    print(f'  Logging output to:     {file_log}')
    print(f'  Logging exceptions to: {file_exception}')

  if file_error:
    if debug_logger:
      print(f'  Logging errors to:     {file_error}')
  else:
    del config['handlers']['file_stderr']

  logging.config.dictConfig(config)

  _logger = logging.getLogger(name)
  for handler in _logger.handlers:
    _fmt = handler.formatter._fmt
    if handler.name.startswith('console'):
      cf = CustomFormatter(fmt=_fmt, color=color, name=handler.name)
      handler.setFormatter(cf)
    else:
      cf = CustomFormatter(fmt=_fmt, color=False, name=handler.name)
      handler.setFormatter(cf)

  if rm_empty:
    _cleanup_key = (file_log, file_error, file_exception)
    if _cleanup_key not in _registered_cleanups:
      _registered_cleanups.add(_cleanup_key)
      atexit.register(cleanup)


  import types
  if getattr(_logger, '_utilrsw_setlevel_wrapped', False) is False:
    _logger.setLevel = types.MethodType(setLevel, _logger)
    _logger._utilrsw_setlevel_wrapped = True


  def append_uncaught_exception(exc_type, exc_value, exc_traceback):
    if exc_type is KeyboardInterrupt:
      return

    tf = '%Y-%m-%dT%H:%M:%S.%fZ'
    ts = datetime.datetime.now(datetime.timezone.utc).strftime(tf)
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    with open(file_exception, 'a', encoding='utf8') as f:
      f.write(f"[{ts}] Uncaught exception\n")
      f.writelines(lines)
      if not lines[-1].endswith('\n'):
        f.write('\n')
      f.write('\n')
      if debug_logger:
        print(f' Wrote: {file_exception}')

  previous_excepthook = sys.excepthook
  def utilrsw_excepthook(exc_type, exc_value, exc_traceback):
    append_uncaught_exception(exc_type, exc_value, exc_traceback)
    previous_excepthook(exc_type, exc_value, exc_traceback)
  sys.excepthook = utilrsw_excepthook

  if hasattr(sys, 'unraisablehook'):
    previous_unraisablehook = sys.unraisablehook
    def utilrsw_unraisablehook(unraisable):
      args = [type(unraisable.exc_value),
              unraisable.exc_value,
              unraisable.exc_traceback]
      append_uncaught_exception(*args)
      previous_unraisablehook(unraisable)
    sys.unraisablehook = utilrsw_unraisablehook

  try:
    import threading
    if hasattr(threading, 'excepthook'):
      previous_thread_excepthook = threading.excepthook
      def utilrsw_thread_excepthook(args):
        append_uncaught_exception(args.exc_type, args.exc_value, args.exc_traceback)
        previous_thread_excepthook(args)
      threading.excepthook = utilrsw_thread_excepthook
  except Exception:
    pass

  return _logger
