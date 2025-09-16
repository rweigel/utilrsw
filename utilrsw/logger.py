import os
import sys
import time
import inspect
import datetime
import logging
import logging.config

def logger(name=None,
           console_format=u"%(asctime)s %(levelname)s %(name)s %(message)s",
           file_format=u"%(asctime)s %(levelname)s %(name)s %(message)s",
           log_dir=None,
           file_log=None,
           file_error=None,
           datefmt="%Y-%m-%dT%H:%M:%S.%f",
           utc_timestamps=True,
           rm_existing=True,
           rm_string='',
           color=None,
           disable_existing_loggers=False,
           debug_logger=False):

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

  def get_filename(filename, ext):
    if filename is None:
      frame = inspect.stack()[2]
      module = inspect.getmodule(frame[0])
      file_log = os.path.splitext(module.__file__)[0] + ext
      if log_dir is not None:
        file_log_dir = os.path.dirname(file_log)
        file_log_name = os.path.basename(file_log)
        file_log = os.path.join(file_log_dir, log_dir, file_log_name)
    else:
      if os.path.isabs(filename):
        file_log = filename
      else:
        frame = inspect.stack()[2]
        module = inspect.getmodule(frame[0])
        file_log = os.path.join(os.path.dirname(module.__file__), filename)
    return file_log

  if utc_timestamps:
    logging.Formatter.converter = time.gmtime

  if name is None:
    if debug_logger:
      print("No logger name provided, using inspect.stack() to determine name.")
      for idx, frame in enumerate(inspect.stack()):
        print(f"  Frame {idx}: {frame.frame}")
        #module = inspect.getmodule(frame[0])
        #print(f"    Module: {module}")
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    if module and hasattr(module, '__file__'):
      name = os.path.basename(module.__file__)
    else:
      name = '__main__'

  file_log = get_filename(file_log, ".log")
  if not file_error:
    file_error = os.path.splitext(file_log)[0] + ".errors.log"
  else:
    file_error = get_filename(file_error, ".errors.log")

  if rm_existing:
    if os.path.exists(file_log):
      os.remove(file_log)
    if file_error and os.path.exists(file_error):
      os.remove(file_error)

  from . import mkdir as mkdir
  if file_log:
    mkdir(os.path.dirname(file_log))
  if file_error:
    mkdir(os.path.dirname(file_error))

  handlers = [
            'console_stderr',
            'console_stdout',
            'file_stdout'
          ]

  if file_error:
    handlers.append('file_stderr')

  # Based on https://stackoverflow.com/a/66728490
  config = {
      'version': 1,
      'disable_existing_loggers': disable_existing_loggers,
      'filters': {
          'exclude_errors': {
              '()': ExcludeErrorsFilter
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
              'stream': sys.stderr
          },
          'file_stderr': {
              # Sends all log messages to a file
              'class': 'logging.FileHandler',
              'level': 'ERROR',
              'formatter': 'file_formatter',
              'filename': file_error,
              'encoding': 'utf8'
          },
          'console_stdout': {
              # Sends log messages with log level lower than ERROR to stdout
              'class': 'logging.StreamHandler',
              'level': 'DEBUG',
              'formatter': 'console_formatter',
              'filters': ['exclude_errors'],
              'stream': sys.stdout
          },
          'file_stdout': {
              # Sends all log messages to a file
              'class': 'logging.FileHandler',
              'level': 'DEBUG',
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
          #   In general, this should be kept at 'NOTSET'.
          #   Otherwise it would interfere with the log levels set for each handler.
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

    print(f'  Logging output to: {file_log}')

  if file_error:
    if debug_logger:
      print(f'  Logging errors to: {file_error}')
  else:
    del config['handlers']['file_stderr']


  logging.config.dictConfig(config)

  _logger = logging.getLogger(name)
  for handler in _logger.handlers:
    if handler.name.startswith('console'):
      handler.setFormatter(CustomFormatter(fmt=handler.formatter._fmt, color=color, name=handler.name))
    else:
      handler.setFormatter(CustomFormatter(fmt=handler.formatter._fmt, color=False, name=handler.name))

  return logging.getLogger(name)
