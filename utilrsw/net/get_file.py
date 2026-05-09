import os
import sys
import secrets
from urllib.request import urlopen
from shutil import copyfileobj

import utilrsw

def get_file(url, logger=None, url2file=None, use_cache=True, cache_dir=None):

  # TODO: Do HEAD request to determine if file needs to be downloaded if
  #       file.header.ext exists. Use keyword "update" instead of "use_cache"
  #       to be consistent with get().

  length=16*1024

  if url2file is not None:
    file_name = url2file(url)
  else:
    file_name = url.split('/')[-1]

  if cache_dir is not None:
    file_name = os.path.join(cache_dir, file_name)

  if use_cache:
    if os.path.exists(file_name):
      if logger is not None:
        logger.info(f"Using cached file: {file_name}")
      return file_name
  else:
    if logger is not None:
      logger.info(f"Ignoring cached file: {file_name} because use_cache=False")

  utilrsw.mkdir(os.path.dirname(file_name), logger=logger)

  if logger is not None:
    logger.info(f"Downloading {url} to {file_name}")

  file_name_tmp = file_name + "." + secrets.token_hex(4) + ".tmp"

  begin = utilrsw.tick()

  try:
    req = urlopen(url)
  except Exception as e:
    if logger is not None:
      logger.error(f"Error: {url}: {e}")
    raise e

  try:
    with open(file_name_tmp, 'wb') as fp:
      copyfileobj(req, fp, length)
  except Exception as e:
    if logger is not None:
      logger.error(f"Error: {url}: {e}")
    os.remove(file_name_tmp)
    raise e

  if logger is not None:
    logger.info(f"Got: {utilrsw.tock(begin):.2f}s {url}")

  try:
    os.rename(file_name_tmp, file_name)
  except Exception as e:
    if logger is not None:
      logger.error(f"Error: {url}: {e}")
    os.remove(file_name_tmp)
    raise e

  headers = dict(req.getheaders())
  utilrsw.write(file_name + ".headers.json", headers, logger=logger)

  return file_name

def get_conditional(url, file=None, gzip=False, stream=False, progress=False, logger=None):

  if file is None:
    file = url.split('/')[-1]
  if len(file) == 0:
    file = url.split('/')[-2]

  import requests
  from requests.adapters import HTTPAdapter
  from requests.packages.urllib3.util.retry import Retry

  from datetime import datetime, timezone

  def format_http_date(timestamp):
    """Format a timestamp as an HTTP-date (RFC 7231)."""
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")

  # Create output directory if needed
  if not os.path.exists(os.path.dirname(file)):
    os.makedirs(os.path.dirname(file))
    if logger is not None:
      logger.info(f"Creating directory: {os.path.dirname(file)}")

  headers = {}
  if gzip:
    headers['Accept-Encoding'] = 'gzip'

  if os.path.exists(file):
    # Get the last modified time of the file
    last_modified_time = os.path.getmtime(file)
    # Format the time as HTTP-date (RFC 7231)
    headers['If-Modified-Since'] = format_http_date(last_modified_time)

  # https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html
  retry_strategy = Retry(
      connect=3,
      read=3,
      status_forcelist=[429],
      allowed_methods=["GET"],
      backoff_factor=1
  )
  adapter = HTTPAdapter(max_retries=retry_strategy)
  session = requests.Session()
  session.mount("https://", adapter)
  session.mount("http://", adapter)

  # Perform the GET request with conditional headers
  try:
    #response = requests.get(url, headers=headers, stream=stream)
    response = session.get(url, headers=headers, stream=stream)
    response.raise_for_status()
  except Exception as e:
    status_code = getattr(e.response, 'status_code', -1)
    reason = getattr(e.response, 'reason', e)
    # using e as below for message shows a ?https at the end of the url, which
    # is misleading because it was not the actual url attempted.
    emsg = f"HTTP status code {status_code} and reason '{reason}' for {url}"
    if logger is not None:
      logger.error(emsg)
    return {'response': e.response,
            'data': None,
            'emsg': emsg
          }

  content = None

  file_tmp = file + "." + secrets.token_hex(4) + ".tmp"
  emsg = None
  if response.status_code == 200:

    if stream:
      # Stream the file to disk
      if logger is not None:
        logger.info(f"Streaming to: {file_tmp}")
      total_size = int(response.headers.get('content-length', 0))
      downloaded_size = 0
      if logger is not None:
        logger.info(f"Total size: {total_size} bytes")
      with open(file_tmp, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
          if chunk:  # Filter out keep-alive chunks
            f.write(chunk)
            downloaded_size += len(chunk)
            if progress:
              percent = (downloaded_size / total_size) * 100 if total_size else 0
              print(f"\rProgress: {percent:.0f}%", end="", flush=True)
      if progress:
        if sys.stdout.isatty():
          sys.stdout.write("\r\033[2K")
          sys.stdout.flush()
        else:
          print()

      if logger is not None:
        logger.info(f"Streamed: {downloaded_size} bytes to {file_tmp}")

    else:
      # Read the entire file into memory and save it
      if logger is not None:
        logger.info(f"Reading: {file}")
      with open(file, 'wb') as f:
        if logger is not None:
          logger.info(f"Writing: {file}")
        content = response.content
        f.write(content)
        if logger is not None:
          logger.info(f"Wrote: {file}")

    try:
      os.rename(file_tmp, file)
    except Exception as e:
      os.remove(file_tmp)
      raise e

  elif response.status_code == 304:
    if logger is not None:
      logger.info(f"File not modified: {file}")
    if not stream:
      with open(file, 'rb') as f:
        if logger is not None:
          logger.info(f"Reading: {file}")
        content = f.read()

  else:
    emsg = f"HTTP status code {response.status_code} and reason '{response.reason}' for {url}"
    if logger is not None:
      logger.error(emsg)

  info = {'response': response,
          'data': content,
          'status_code': response.status_code,
          'url': url,
          'headers': {
            'request': dict(response.request.headers),
            'response': dict(response.headers)
          },
          'cache_file': file
  }
  if emsg is not None:
    info['emsg'] = emsg

  if logger is not None:
    logger.debug(f"Returning info: {info}")

  return info
