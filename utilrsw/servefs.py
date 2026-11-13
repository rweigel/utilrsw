import asyncio
import itertools
import sys
import threading
import time
import traceback


class RequestDiagnosticsMiddleware:
  def __init__(self, asgi_app, logger, slow_request_seconds):
    self.app = asgi_app
    self.logger = logger
    self.slow_request_seconds = slow_request_seconds
    self.request_ids = itertools.count(1)

  async def __call__(self, scope, receive, send):
    if scope["type"] != "http":
      await self.app(scope, receive, send)
      return

    request_id = next(self.request_ids)
    started = time.monotonic()
    method = scope.get("method", "-")
    path = scope.get("path", "/")
    query = scope.get("query_string", b"").decode("latin-1")
    if query:
      path += f"?{query}"
    self.logger.info(f"request={request_id} started method={method} path={path}")

    def warn_if_slow():
      elapsed = time.monotonic() - started
      thread_names = {thread.ident: thread.name for thread in threading.enumerate()}
      stacks = []
      for thread_id, frame in sys._current_frames().items():
        name = thread_names.get(thread_id, "unknown")
        stacks.append(
          f"Thread {name} ({thread_id}):\n{''.join(traceback.format_stack(frame)).rstrip()}"
        )
      self.logger.warning(
        f"request={request_id} still running after {elapsed:.1f}s "
        f"method={method} path={path}\n" + "\n\n".join(stacks)
      )

    watchdog = asyncio.get_running_loop().call_later(
      self.slow_request_seconds, warn_if_slow
    )
    status_code = 500
    response_finished = False

    async def send_diagnostics(message):
      nonlocal status_code, response_finished
      if message["type"] == "http.response.start":
        status_code = message["status"]
      await send(message)
      if message["type"] == "http.response.body" and not message.get("more_body", False):
        response_finished = True

    try:
      await self.app(scope, receive, send_diagnostics)
    except Exception:
      self.logger.exception(f"request={request_id} failed method={method} path={path}")
      raise
    finally:
      watchdog.cancel()
      elapsed = time.monotonic() - started
      self.logger.info(
        f"request={request_id} finished status={status_code} complete={response_finished} "
        f"duration={elapsed:.3f}s method={method} path={path}"
      )


def servefs(config=None):
  """Serve a directory listing or a file using FastAPI.

  Parameters
  ----------
  config : dict (see example for options) or str, optional
      Configuration dictionary or path to a JSON file. If a string, it is
      treated as the path to a JSON file containing such a dict.

  Returns
  -------
  app : FastAPI application
      A FastAPI application that serves files from the specified root

  Example
  -------
  Using Uvicorn directly (if using only a single worker):

  .. code-block:: python

      import utilrsw
      import uvicorn

      app_config = {
          "debug": True,
          "root": "."
      }

      app = utilrsw.servefs(app_config)
      uvicorn.run(app, host="0.0.0.0", port=6002)

  Using a wrapper that calls Uvicorn from the command line (needed for
  multiple workers):

  .. code-block:: python

      configs = {
          "server": {
              "--host": "0.0.0.0",
              "--port": 6002,
              "--workers": 2
          },
          "app": app_config
      }
      import utilrsw.uvicorn
      utilrsw.uvicorn.run("utilrsw.servefs", configs)

  """
  import os
  import html
  import json
  import http
  import stat
  import pathlib
  import datetime
  import urllib.parse
  from email.utils import format_datetime, parsedate_to_datetime

  from fastapi import FastAPI, HTTPException, Request, Response
  from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
  from fastapi.middleware.cors import CORSMiddleware

  import logging
  logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
  )
  logger = logging.getLogger("servefs")

  if config is None:
    config = {}
  if isinstance(config, str):
    with open(config, "r") as f:
      config = f.read()
      config = json.loads(config)

  root = config.get("root", ".")
  logger.setLevel(getattr(logging, config.get("log_level", "INFO").upper()))
  slow_request_seconds = config.get("slow_request_seconds", 10)
  # Convert root to an absolute path
  root = os.path.abspath(root)
  logger.info(f"Serving files from root directory: {root}")

  # Increase file descriptor limit if possible
  try:
    import resource
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    if soft < hard:
      hard = 1024 * 1024
      resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))
      logger.info(f"Increased file descriptor limit from {soft} to {hard}")
  except Exception as e:
    logger.warning(f"Could not increase file descriptor limit: {e}", exc_info=True)

  app = FastAPI()
  app.add_middleware(
    RequestDiagnosticsMiddleware,
    logger=logger,
    slow_request_seconds=slow_request_seconds
  )

  kwargs = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["GET", "HEAD"],
    "allow_headers": ["Content-Type"]
  }
  app.add_middleware(CORSMiddleware, **kwargs)

  @app.exception_handler(Exception)
  async def global_exception_handler(request, exc):
    logger.exception(f"Unhandled exception while serving {request.method} {request.url}: {exc}")
    return Response(status_code=500, content="Internal server error")

  def file_headers(full_path):
    stat = full_path.stat()
    last_modified = datetime.datetime.fromtimestamp(stat.st_mtime, tz=datetime.timezone.utc)
    headers = {
      "Content-Length": str(stat.st_size),
      "Last-Modified": format_datetime(last_modified, usegmt=True)
    }
    return headers, last_modified.replace(microsecond=0)

  def not_modified(request, last_modified):
    if_modified_since = request.headers.get("if-modified-since")
    if not if_modified_since:
      return False
    try:
      ims = parsedate_to_datetime(if_modified_since)
    except (TypeError, ValueError, IndexError, OverflowError):
      return False
    if ims.tzinfo is None:
      ims = ims.replace(tzinfo=datetime.timezone.utc)
    ims = ims.astimezone(datetime.timezone.utc).replace(microsecond=0)
    return last_modified <= ims

  def log_access(request, status_code):
    client_host = request.client.host if request.client else "-"
    client_port = request.client.port if request.client else "-"
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    raw_path = request.url.path or "/"
    if request.url.query:
      raw_path = f"{raw_path}?{request.url.query}"
    http_version = request.scope.get("http_version", "1.1")
    user_agent = request.headers.get("user-agent", "-")
    phrase = http.HTTPStatus(status_code).phrase if status_code in http.HTTPStatus._value2member_map_ else ""
    logger.info(
      '%s:%s %s "%s %s HTTP/%s" %d %s ua="%s"',
      client_host,
      client_port,
      now,
      request.method,
      raw_path,
      http_version,
      status_code,
      phrase,
      user_agent
    )

  @app.get("{path:path}", response_class=HTMLResponse)
  def serve_directory_or_file(request: Request, path: str = ""):
    """Serve directory listing or a file."""

    # Note that FastAPI handles paths such as "../../" and
    # prevents directory traversal attacks by returning a path of "/"
    # if the path is not valid. For example, http://localhost:6001/../../"
    # will return path = "/".

    # path[1:] to remove leading slash
    full_path = pathlib.Path(os.path.join(root, path[1:]))
    logger.debug(f"Requested path: {path}")
    logger.debug(f"root path:      {root}")
    logger.debug(f"Resolved path:  {full_path}")

    if full_path.is_file():
      headers, last_modified = file_headers(full_path)
      if not_modified(request, last_modified):
        response = Response(status_code=304, headers=headers)
        log_access(request, response.status_code)
        return response
      response = FileResponse(full_path, headers=headers)
      log_access(request, response.status_code)
      return response

    # If the path is not a directory, send 404 error
    if not full_path.is_dir():
      log_access(request, 404)
      raise HTTPException(status_code=404, detail="File or directory not found")

    # Redirect to trailing slash for directories
    if not path.endswith('/'):
      redirect_path = path + '/'
      response = RedirectResponse(url=redirect_path, status_code=301)
      log_access(request, response.status_code)
      return response

    # Generate directory listing
    try:
      items = os.listdir(full_path)
    except PermissionError:
      log_access(request, 403)
      raise HTTPException(status_code=403, detail="Permission denied")

    server_path = html.escape(urllib.parse.unquote(path), quote=False)

    response = HTMLResponse(content=_dir_listing(full_path, server_path, items))
    log_access(request, response.status_code)
    return response

  @app.head("{path:path}")
  def head_request(request: Request, path: str = ""):
      """Handle HEAD requests."""
      full_path = pathlib.Path(os.path.join(root, path[1:]))

      # Add Last-Modified header for files
      if full_path.is_file():
        headers, last_modified = file_headers(full_path)
        if not_modified(request, last_modified):
          response = Response(status_code=304, headers=headers)
          log_access(request, response.status_code)
          return response
        response = FileResponse(full_path, headers=headers)
        log_access(request, response.status_code)
        return response

      # If the path is not a directory, raise a 404 error
      if not full_path.is_dir():
        log_access(request, 404)
        raise HTTPException(status_code=404, detail="File or directory not found")

      # For directories, return a generic response with no body
      response = HTMLResponse(content="", headers={"Content-Type": "text/html"})
      log_access(request, response.status_code)
      return response

  DIR_LISTING = _DIR_LISTING.replace("\n  ", "\n")[1:]

  def _dir_listing(full_path, server_path, items):

    items.sort(key=lambda a: a.lower())
    rows = []

    for name in items:
        fullname = pathlib.Path(full_path / name)
        try:
            # Call stat() once and reuse the result to minimize file descriptor usage
            stat_result = fullname.stat()
            size = stat_result.st_size
            mtime = stat_result.st_mtime
            is_dir = stat.S_ISDIR(stat_result.st_mode)
            is_symlink = fullname.is_symlink()
        except (OSError, PermissionError):
            # Skip files that can't be accessed
            continue

        displayname = linkname = name

        # Append / for directories or @ for symbolic links
        if is_dir:
            displayname = name + "/"
            linkname = name + "/"
        if is_symlink:
            displayname = name + "@"

        href = urllib.parse.quote(linkname, errors="surrogatepass")
        text = html.escape(displayname, quote=False)
        modified = datetime.datetime.fromtimestamp(mtime, tz=datetime.timezone.utc)
        modified = modified.strftime('%Y-%m-%dT%H:%M:%SZ')
        a = f'<a href="{href}">{text}</a>'
        rows.append(f'      <tr><td>{a}</td><td>{size}</td><td>{modified}</td></tr>')

    # Replace placeholders in the template
    listing_html = DIR_LISTING.replace("__DIRECTORY__", server_path)
    listing_html = listing_html.replace("__DIRECTORY_HTML__", "\n".join(rows))
    return listing_html

  return app

_DIR_LISTING = """
  <!DOCTYPE html>
  <html lang="en">
  <head>
    <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
    <title>__DIRECTORY__</title>
  </head>
  <body>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Size</th>
          <th>Last Modified</th>
        </tr>
      </thead>
      <tbody>
        __DIRECTORY_HTML__
      </tbody>
    </table>
  </body>
  </html>
  """
