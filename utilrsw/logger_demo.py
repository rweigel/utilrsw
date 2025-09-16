import os
import logging

from utilrsw import logger
debug_logger = True

log_dir = os.path.dirname(__file__)

config1 = {
  'name': 'logger1',
  # Defaults are logger_demo.log and logger_demo.errors.log
  # (Calling file name is used if not provided.)
  'file_log': os.path.join(log_dir, 'logger_demo1.log'),
  'file_error': os.path.join(log_dir, 'logger_demo1.errors.log'),
  'color': True,
  'debug_logger': debug_logger
}

logger0 = logger(**config1)
logger0.error('"logger1 error message"')
logger0.debug('"logger1 debug message"')

print('Wrote logger.log and logger.errors.log')

if debug_logger:
  print('\n')

config2 = {
  'name': 'logger2',
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
print('Wrote logger2.log and logger2.errors.log')
