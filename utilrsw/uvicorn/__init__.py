def run(app_function, config=None, config_server=None, config_app=None):
  import os
  import json
  import uvicorn

  import logging

  import utilrsw

  logger = logging.getLogger(app_function.split('.')[0])
  app = utilrsw.get_func(app_function)

  if config is not None and (config_server is not None or config_app is not None):
    raise ValueError("Provide either 'config' or 'config_server' and 'config_app'.")

  if config is not None:
    if isinstance(config, str):
      with open(config, "r") as f:
        config_data = f.read()
        config = json.loads(config_data)
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
      config['server'] = config_server

  config_app_file = None
  if config_app is not None:
    if isinstance(config_app, str):
      config_app_file = config_app
      with open(config_app, "r") as f:
        data = f.read()
        config['app'] = json.loads(data)
    else:
      config['app'] = config_app

  if config['server']['workers'] == 1:
    logger.info("Starting uvicorn with single worker")
    logger.info(f"  by executing uvicorn.run({app_function}(config['app']), **config['server'])")
    uvicorn.run(app(config['app']), **config['server'])
  else:
    # If multiple workers, cannot start using uvicorn.run() because that
    # would start multiple instances of the main process.
    # The following approach does not work:
    #   uvicorn.run("hapiserver:factory", factory=True, **config['server'])

    if config_app_file is None:
      # Write temporary config file
      import tempfile
      with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        config_app_file = tf.name
        json.dump(config['app'], tf)

    os.environ["APP_CONFIG"] = config_app_file
    os.environ["APP_FUNCTION"] = app_function
    logger.info(f"Setting shell environment variable APP_CONFIG = {config_app_file}")
    args = ["uvicorn", 'utilrsw.uvicorn:factory', "--factory"]
    if 'host' in config['server']:
      args += ["--host", str(config['server']['host'])]
    if 'port' in config['server']:
      args += ["--port", str(config['server']['port'])]
    if 'workers' in config['server']:
      args += ["--workers", str(config['server']['workers'])]
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