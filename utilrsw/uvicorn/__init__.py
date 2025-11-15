import logging
logger = logging.getLogger(__name__)
logger.propagate = True

def run(app_function, config=None, config_server=None, config_app=None):
  import os
  import json
  import uvicorn


  import utilrsw

  app = utilrsw.get_func(app_function)

  if config is not None and (config_server is not None or config_app is not None):
    raise ValueError("Provide either 'config' or 'config_server' and 'config_app'.")

  if config is not None:
    if isinstance(config, str):
      with open(config, "r") as f:
        config_data = f.read()
        config = json.loads(config_data)
    if not isinstance(config, dict):
      raise ValueError("config must be a dict or path to JSON file.")
    if 'server' not in config:
      raise ValueError("config must contain 'server'")
    if 'app' not in config:
      raise ValueError("config must contain 'app'")
  else:
    config = {}

  if config_server is not None:
    if isinstance(config_server, str):
      with open(config_server, "r") as f:
        data = f.read()
        config['server'] = json.loads(data)
    else:
      if not isinstance(config_server, dict):
        raise ValueError("config_server must be a dict or path to JSON file.")
      config['server'] = config_server

  if False:
    if int(config['server'].get('--workers', 1)) == 1:
      # To have this work, would need to modify config['server'] to map uvicorn
      # command line args to uvicorn.run() args.
      logger.info("Starting uvicorn with single worker")
      logger.info(f"  by executing uvicorn.run({app_function}(config_app), **config_server)")
      uvicorn.run(app(config_app), **config['server'])
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
    logger.debug(f"config['server']: {config['server']}")
    logger.info(f"Setting shell environment variable APP_CONFIG = {config_app_file}")
    args = ["uvicorn", 'utilrsw.uvicorn:factory', "--factory"]
    for key in config['server']:
      if isinstance(config['server'][key], bool):
        if config['server'][key]:
          args += [key]
      else:
        args += [key, str(config['server'][key])]
    logger.info(f"Executing shell command: {' '.join(args)}")
    os.execvp(args[0], args)


def factory(**args):
  """Factory function for uvicorn to create the app in each worker process.
  When
    APP_CONFIG=<file> uvicorn APP --factory ...
  is executed, this function is called to start each process.
  """
  import os
  import logging

  import utilrsw

  app_function = os.environ.get("APP_FUNCTION")
  logger = logging.getLogger(app_function.split('.')[0])

  app = utilrsw.get_func(app_function)

  config = os.environ.get("APP_CONFIG")
  with open(config, "r") as f:
    import json
    config_data = f.read()
    config_dict = json.loads(config_data)

  logger.info(f"Factory returning app with config: {config_dict}")

  return app(config)


def start(app_function, config=None, config_server=None, config_app=None, wait=None):
  import logging
  import atexit
  import multiprocessing

  logger = logging.getLogger(app_function.split('.')[0])

  logger.info("Starting server in background process")
  kwargs = {
    "target": _start_server_process,
    "args": (app_function, config, config_server, config_app),
    "daemon": True
  }
  server_proc = multiprocessing.Process(**kwargs)
  server_proc.start()
  atexit.register(_stop_server, server_proc)

  if wait is not None:
    if 'url' not in wait:
      raise ValueError("wait parameter must include 'url' field")
    _wait(wait['url'], retries=wait['retries'], delay=wait['delay'])


def cli(defaults=None, parser=None):

  default_defaults = {
    "host": "0.0.0.0",
    "port": 5001,
    "workers": 1
  }

  if parser is not None:
    args, unknown_args = parser.parse_known_args()
    args = vars(args)
    logger.debug(f"Parsed known args: {args}")
    logger.debug(f"Parsed unknown args: {unknown_args}")
    for arg in args.copy():
      if arg in default_defaults.keys():
        args[f'--{arg}'] = args.pop(arg)

    unknown_args_dict = {}
    for i, arg in enumerate(unknown_args):
      if arg.startswith('--'):
        if (i + 1) < len(unknown_args) and not unknown_args[i + 1].startswith('--'):
          value = unknown_args[i + 1]
          unknown_args_dict[arg] = value
        else:
          unknown_args_dict[arg] = True

    return {**args, **unknown_args_dict}

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


def _start_server_process(app_function, config=None, config_server=None, config_app=None):
  import logging
  logger = logging.getLogger(app_function.split('.')[0])
  logger.info("Starting server")
  run(app_function, config=config, config_server=config_server, config_app=config_app)


def _stop_server(server_proc):
  try:
    if server_proc.is_alive():
      #logger.info("Terminating server process")
      server_proc.terminate()
      server_proc.join(timeout=2)
  except Exception:
    pass


def _wait(url, retries=50, delay=0.2):
  import time
  import requests

  print(f"Checking if server is ready by making request to {url} ...")
  for i in range(retries):
    try:
      response = requests.get(url, timeout=0.5)
      if response.status_code == 200:
        break
    except Exception:
      print(f"Server not ready. Next try in {delay} sec...")
      time.sleep(delay)
  else:
    raise RuntimeError(f"Server did not start after {retries} attempts.")