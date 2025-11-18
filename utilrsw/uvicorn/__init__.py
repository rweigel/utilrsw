import logging
logger = logging.getLogger(__name__)


def cli(defaults=None, parser=None):

  default_defaults = {
    "host": "0.0.0.0",
    "port": 5001,
    "workers": 1
  }

  configs = {'server': {}, 'app': {}}
  if parser is not None:
    args, unknown_args = parser.parse_known_args()
    args = vars(args)
    logger.debug(f"Parsed known args: {args}")
    logger.debug(f"Parsed unknown args: {unknown_args}")
    for key, value in args.items():
      if key in default_defaults.keys():
        configs['server'][f'--{key}'] = value
      else:
        configs['app'][key] = value

    for i, arg in enumerate(unknown_args):
      if arg.startswith('--'):
        if (i + 1) < len(unknown_args) and not unknown_args[i + 1].startswith('--'):
          value = unknown_args[i + 1]
          configs['server'][arg] = value
        else:
          configs['server'][arg] = True

    return configs

  if defaults is None:
    defaults = default_defaults
  else:
    defaults.update(default_defaults)

  return {
    "host": {
      "help": f"Serve table as a web page at http://host:port. Default: {defaults['host']}",
      "default": defaults['host']
    },
    "port": {
      "help": f"Serve table as a web page at http://host:port. Default: {defaults['port']}",
      "type": int,
      "default": defaults['port']
    },
    "workers": {
      "help": "Number of uvicorn worker processes to start. Default: 1",
      "type": int,
      "default": 1
    }
  }


def run(app_function, configs):

  import os
  import json
  import uvicorn

  import utilrsw

  config_server = configs.get('server', None)
  config_app = configs.get('app', None)

  app_debug = config_app.get("debug", False)
  if app_debug:
    logger.setLevel(logging.DEBUG)

  app = utilrsw.get_func(app_function)
  if config_server is not None:
    if isinstance(config_server, str):
      with open(config_server, "r") as f:
        data = f.read()
        config_server = json.loads(data)
    else:
      if not isinstance(config_server, dict):
        raise ValueError("config_server must be a dict or path to JSON file.")

  if False:
    if int(config['server'].get('--workers', 1)) == 1:
      # To have this work, would need to modify config['server'] to map uvicorn
      # command line args to uvicorn.run() args.
      logger.info("Starting uvicorn with single worker")
      logger.info(f"  by executing uvicorn.run({app_function}(config_app), **config_server)")
      uvicorn.run(app(config_app), **config_server)
  else:
    # If multiple workers, cannot start using uvicorn.run() because that
    # would start multiple instances of the main process.
    # The following approach does not work:
    #   uvicorn.run("hapiserver:factory", factory=True, **config['server'])

    if isinstance(config_app, str):
      config_app_file = config_app
    else:
      # Write temporary config file
      import tempfile
      with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        config_app_file = tf.name
        json.dump(config_app, tf)

    os.environ["APP_CONFIG"] = config_app_file
    os.environ["APP_FUNCTION"] = app_function
    logger.info(f"Setting shell environment variable APP_CONFIG = {config_app_file}")
    logger.info(f"Setting shell environment variable APP_FUNCTION = {app_function}")

    logger.info(f"Creating command line string using config_server = {config_server}")
    args = ["uvicorn", 'utilrsw.uvicorn:factory', "--factory"]
    for key in config_server:
      if isinstance(config_server[key], bool):
        if config_server[key]:
          args += [key]
      else:
        args += [key, str(config_server[key])]
    logger.info(f"Executing shell command: {' '.join(args)}")
    os.execvp(args[0], args)


def factory(**args):
  """Factory function for uvicorn to create the app in each worker process.
  When
    APP_CONFIG=<file> uvicorn APP --factory ...
  is executed, this function is called to start each process.
  """
  import os
  import utilrsw

  app_function = os.environ.get("APP_FUNCTION")
  app = utilrsw.get_func(app_function)
  config = os.environ.get("APP_CONFIG")
  with open(config, "r") as f:
    import json
    config_data = f.read()
    config_dict = json.loads(config_data)

  app_debug = config_dict.get("debug", False)
  if app_debug:
    logger.setLevel(logging.DEBUG)
  logger.info(f"Read APP_CONFIG environment variable: {config}")
  logger.info(f"Read APP_FUNCTION environment variable: {app_function}")
  logger.info("factory() returning app(config_file) with")
  logger.info(f"  config_file: {config}")
  logger.info(f"  config_file content: {config_data}")

  return app(config)


def start(app_function, configs, wait=None):
  import atexit
  import multiprocessing

  logger.info("Starting server in background process")
  kwargs = {
    "target": _start_server_process,
    "args": (app_function, configs),
    "daemon": True
  }
  process = multiprocessing.Process(**kwargs)
  process.start()
  atexit.register(stop, process)

  if wait is not None:
    if 'url' not in wait:
      raise ValueError("wait parameter must include 'url' field")
    _wait(wait['url'], retries=wait['retries'], delay=wait['delay'])

  return process

def stop(process):
  try:
    if process.is_alive():
      logger.info("Terminating server process")
      process.terminate()
      process.join(timeout=2)
  except Exception:
    pass


def _start_server_process(app_function, configs):

  logger.info("Starting server")
  run(app_function, configs)


def _wait(url, retries=50, delay=0.2):
  import time
  import requests

  logger.info(f"Checking if server is ready by making request to {url} ...")
  for i in range(retries):
    try:
      response = requests.get(url, timeout=0.5)
      if response.status_code == 200:
        break
    except Exception:
      logger.info(f"Server not ready. Next try in {delay} sec...")
      time.sleep(delay)
  else:
    raise RuntimeError(f"Server did not start after {retries} attempts.")