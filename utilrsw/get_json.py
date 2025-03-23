import os
import json
import shutil
import logging
import datetime
import tempfile
import xmltodict

import deepdiff

import requests_cache
from requests.adapters import HTTPAdapter

# TODO: Use
#  https://stackoverflow.com/a/71775172/1491619

def get_json(url, cache_dir=None, headers=None, timeout=20, max_retries=5, diffs=False, csopts=None):

  if cache_dir is None:
    cache_dir = tempfile.gettempdir()
    if os.path.exists('/tmp'):
      cache_dir = '/tmp'

  session = _CachedSession(cache_dir, csopts)

  protocol = url.split(':')[0]
  session.mount(f'{protocol}://', HTTPAdapter(max_retries=max_retries))

  try:
    resp = session.get(url, protocol, headers=headers, timeout=timeout)
    resp.raise_for_status()
  except Exception as e:
    status_code = getattr(e.response, 'status_code', -1)
    reason = getattr(e.response, 'reason', e)
    # using e as below for message shows a ?https at the end of the url, which
    # is misleading because it was not the actual url attempted.
    #return {'response': resp, 'data': None, 'diff': None, 'emsg': e}
    emsg = f"HTTP status code {status_code} and reason '{reason}' for {url}"
    return {'response': e.response,
            'data': None,
            'diff': None,
            'emsg': emsg,
            'log': None
          }

  try:
    if resp.headers['Content-Type'] == 'text/xml':
      text = resp.text
      json_dict = xmltodict.parse(text)
    else:
      json_dict = resp.json()

    diff = None
    if diffs:
      diff = _diff(cache_dir, resp.cache_key)

    cache_file = os.path.join(cache_dir, resp.cache_key + ".json")

    # https://stackoverflow.com/questions/55638905/how-to-convert-os-stat-result-to-a-json-that-is-an-object
    stat = os.stat(cache_file)
    stat_dict = {attr: getattr(stat, attr) for attr in dir(stat) if attr.startswith('st_')}

    return {'response': resp,
            'status_code': resp.status_code,
            'url': url,
            'headers': {
              'request': dict(resp.request.headers),
              'response': dict(resp.headers)
            },
            'cache_dir': cache_dir,
            'cache_key': resp.cache_key,
            'cache_file': cache_file,
            'cache_file_stat': stat_dict,
            'from_cache': resp.from_cache,
            'revalidated': resp.revalidated,
            'is_expired': resp.is_expired,
            'options': csopts,
            'emsg': None,
            'log': _log(resp, diff),
            'diff': diff,
            'data': json_dict
          }

  except Exception as e:
    return {'response': resp, 'data': None, 'diff': None, 'emsg': e, 'log': _log(resp, None)}

def _diff(cache_dir, cache_key):

  def read(fname):
    with open(fname, encoding='utf-8') as f:
      return json.load(f)

  subdir = os.path.join(cache_dir, cache_key)
  file_last = os.path.join(subdir, cache_key + ".json")
  os.makedirs(subdir, exist_ok=True)

  file_now = os.path.join(cache_dir, cache_key + ".json")
  try:
    data_now = read(file_now)
  except Exception as e:
    return {"diff": None, "file_now": None, "file_last": None}

  if not os.path.exists(file_last):
    shutil.copyfile(file_now, file_last)
    return {"diff": None, "file_now": file_now, "file_last": None}

  try:
    data_last = read(file_last)
  except Exception as e:
    return {"diff": None, "file": file_now, "file_last": None}

  diff = deepdiff.DeepDiff(data_last, data_now)
  timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
  file_diff = os.path.join(subdir, f"{cache_key}.{timestamp}.diff.json")

  with open(file_diff, 'w', encoding='utf-8') as f:
    json.dump(diff, f, indent=2, ensure_ascii=False)

  shutil.copyfile(file_now, file_last)

  return {"diff": diff, "file_now": file_now, "file_last": file_last}

def _log(resp, diff):
  # https://stackoverflow.com/questions/74317707/how-to-make-deepdiff-output-human-readable
  req_cache_headers = {k: v for k, v in resp.request.headers.items() if k in ['If-None-Match', 'If-Modified-Since', 'Accept-Endoding', 'Cache-Control']}
  res_cache_headers = {k: v for k, v in resp.headers.items() if k in ['ETag', 'Last-Modified', 'Cache-Control', 'Vary']}
  msg = "\n"
  msg += f"  Status code: {resp.status_code}\n"
  msg += f"  From cache: {resp.from_cache}\n"
  if diff and 'diff' in diff:
    msg += f"  Current cache file: {diff['file_now']}\n"
    if 'file_last' in diff:
      msg += f"  Last cache file:    {diff['file_last']}\n"
  msg += "  Request Cache-Related Headers:\n"
  for k, v in req_cache_headers.items():
    msg += f"    {k}: {v}\n"
  msg += "  Response Cache-Related Headers:\n"
  for k, v in res_cache_headers.items():
    msg += f"    {k}: {v}\n"
  if diff and 'diff' in diff:
    if diff['diff'] is None or len(diff['diff']) == 0:
      msg += "  Cache diff: None\n"
    else:
      msg += "  Cache diff:\n    "
      json_indented = "\n    ".join(diff['diff'].to_json(indent=2).split('\n'))
      msg += f"{json_indented}\n"
  return msg.rstrip()

def _CachedSession(cache_dir, csopts):

  # https://requests-cache.readthedocs.io/en/stable/#settings
  # https://requests-cache.readthedocs.io/en/stable/user_guide/headers.html

  logging.getLogger("requests").setLevel(logging.ERROR)
  logging.getLogger('requests_cache').setLevel(logging.ERROR)
  logging.getLogger("urllib3").setLevel(logging.ERROR)

  csopts_default = {
    # Save files in the default user cache dir
    "use_cache_dir": True,

    # Use Cache-Control response headers for expiration, if available
    "cache_control": True,

    # Expire responses after expire_after if no cache control header
    #"expire_after": 0,

    # Cache responses with these status codes
    "allowable_codes": [200],

    # In case of request errors, use stale cache data if possible
    "stale_if_error": True,

    "serializer": "json",

    # Pre 2.7.1 "backend": "filesystem" caused caching to not work unless
    # decode_content = False.
    # See https://github.com/requests-cache/requests-cache/issues/963
    "backend": "filesystem",

    "decode_content": True
  }

  if csopts is not None:
    csopts_default.update(csopts)

  # CachedSession does not handle relative paths properly.
  if not os.path.isabs(cache_dir):
    cache_dir = os.path.abspath(cache_dir)

  session = requests_cache.CachedSession(cache_dir, **csopts_default)

  return session

def _requests_cache_bug():
  from datetime import timedelta
  import requests_cache

  copts = {
    # Save files in the default user cache dir
    "use_cache_dir": True,

    # Use Cache-Control response headers for expiration, if available
    "cache_control": True,

    # Expire responses after expire_after if no cache control header
    "expire_after": 0,

    # Cache responses with these status codes
    "allowable_codes": [200],

    # In case of request errors, use stale cache data if possible
    "stale_if_error": False,

    "serializer": "json",

    # This causes caching to not work unless decode_content = False
    # https://github.com/requests-cache/requests-cache/issues/963
    # As of 2.7, it seems to be working.
    "backend": "filesystem",

    "decode_content": True
  }
  session = requests_cache.CachedSession('/tmp/CachedSession/', **copts)

  url = "https://httpbin.org/cache/4"
  resp = session.get(url)
  print(f"cache_key: {resp.cache_key}")
  print(f"from_cache: {resp.from_cache}")
  print(f"revalidated: {resp.revalidated}")
  print(f"is_expired: {resp.is_expired}")
  print(resp.cache_key)
  print("request headers")
  print(resp.request.headers)
  print("response headers")
  print(resp.headers)

def _demo():
  url = "https://httpbin.org/cache/4"
  #url = "https://httpbin.org/bytes/4"
  cache_dir = '/tmp/CachedSession/'
  csopts = {
    "use_cache_dir": True,
    "cache_control": True,
    "expire_after": 0,
    "allowable_codes": [200],
    "stale_if_error": False,
    "serializer": "json",
    "backend": "filesystem",
    "decode_content": True
  }
  result = get_json(url, cache_dir, diffs=True, csopts=csopts)
  import utilrsw
  utilrsw.print_dict(result)

if __name__ == '__main__':
  _demo()
  #_requests_cache_bug()