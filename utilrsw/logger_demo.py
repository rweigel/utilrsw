import os

from utilrsw import logger
debug_logger = True

log_dir = os.path.dirname(__file__)
log_dir = os.path.join(log_dir, 'logger_demo')

config0 = {
  'color': True,
  'debug_logger': debug_logger
}

logger0 = logger(**config0)
logger0.error('"logger0 error message"')
logger0.info('"logger0 info message"')

logger0.setLevel('ERROR')
logger0.info('logger0 info message not shown')

logger0.disabled = True
logger0.error('"logger0 error message not shown"')
if not debug_logger:
  print('Wrote logger.log and logger.errors.log')


config1 = {
  'name': 'logger1',
  # Defaults are logger_demo.log and logger_demo.errors.log
  # (Calling file name is used if not provided.)
  'file_log': os.path.join(log_dir, 'logger_demo1.log'),
  'file_error': os.path.join(log_dir, 'logger_demo1.errors.log'),
  'color': True,
  'debug_logger': debug_logger
}
logger1 = logger(**config1)
logger1.info('"logger1 info message"')
logger1.error('"logger1 error message"')
if not debug_logger:
  print('Wrote logger_demo1.log and logger_demo1.errors.log')

if debug_logger:
  print('\n')


config2 = {
  'name': 'logger2',
  'log_level': 'DEBUG',
  'file_log': os.path.join(log_dir, 'logger_demo2.log'),
  'file_error': os.path.join(log_dir, 'logger_demo2.errors.log'),
  'console_format': '%(asctime)s p%(process)s %(pathname)s:%(lineno)d %(levelname)s - %(message)s',
  'file_format': u'%(asctime)s %(levelname)s %(name)s %(message)s',
  'datefmt': '%Y-%m-%dT%H:%M:%S',
  'rm_string': log_dir + '/',
  'color': True,
  'debug_logger': debug_logger
}

logger2 = logger(**config2)
logger2.info('"logger2 info message"')
logger2.error('"logger2 error message"')
logger2.debug('"logger2 debug message"')
if not debug_logger:
  print('Wrote logger_demo2.log and logger_demo2.errors.log')


config3 = {
  'log_level': 'DEBUG',
  'file_log': os.path.join(log_dir, 'logger_demo3.log'),
  'file_error': os.path.join(log_dir, 'logger_demo3.errors.log'),
  'console_format': '%(asctime)s p%(process)s %(pathname)s:%(lineno)d %(levelname)s - %(message)s',
  'file_format': u'%(asctime)s %(levelname)s %(name)s %(message)s',
  'datefmt': '%Y-%m-%dT%H:%M:%S',
  'rm_string': log_dir + '/',
  'color': True,
  'debug_logger': debug_logger
}

logger3 = logger(**config3)
logger3.info('"logger3 info message"')
logger3.error('"logger3 error message"')
logger3.debug('"logger3 debug message"')
if not debug_logger:
  print('Wrote logger_demo3.log and logger_demo3.errors.log')