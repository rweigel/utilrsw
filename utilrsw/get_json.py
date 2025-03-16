import os
import json
import shutil
import logging
import tempfile
import xmltodict

import deepdiff

import requests_cache
from requests.adapters import HTTPAdapter

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
    #import pdb; pdb.set_trace()
    # using e as below for message shows a ?https at the end of the url, which
    # is misleading because it was not the actual url attempted.
    #return {'response': resp, 'data': None, 'diff': None, 'emsg': e}
    emsg = f"HTTP status code {e.response.status_code} and reason '{e.response.reason}' for {url}"
    return {'response': resp, 'data': None, 'diff': None, 'emsg': emsg}

  try:
    if resp.headers['Content-Type'] == 'text/xml':
      text = resp.text
      json_dict = xmltodict.parse(text)
    else:
      json_dict = resp.json()
    diff = None
    if diffs:
      diff = _diff(cache_dir, resp.cache_key)
    return {'response': resp, 'data': json_dict, 'diff': diff, 'emsg': None}
  except Exception as e:
    return {'response': resp, 'data': None, 'diff': None, 'emsg': e}

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
    return {"diff": None, "file_now": file_now, "file_last": None}

  try:
    data_last = read(file_last)
  except Exception as e:
    return {"diff": None, "file": file_now, "file_last": None}

  diff = deepdiff.DeepDiff(data_last, data_now)
  file_diff = os.path.join(subdir, cache_key + ".diff.json")

  with open(file_diff, 'w', encoding='utf-8') as f:
    json.dump(diff.to_json(), f, indent=2, ensure_ascii=False)

  shutil.copyfile(file_now, file_last)

  return {"diff": diff, "file_now": file_now, "file_last": file_last}

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
    # This causes caching to not work.
    #"expire_after": 0,

    # Cache responses with these status codes
    "allowable_codes": [200],

    # In case of request errors, use stale cache data if possible
    "stale_if_error": True,

    "serializer": "json",

    # This causes caching to not work unless decode_content = False
    # See https://github.com/requests-cache/requests-cache/issues/963
    "backend": "filesystem",

    "decode_content": False
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
    # Setting to 0 causes caching to not work?
    # Need to find test that demonstrate the issue.
    # httpbin test does not seem to show. This may have been
    # caused by using a cache created by a different version of 
    # requests-cache.
    #"expire_after": 0,

    # Cache responses with these status codes
    "allowable_codes": [200],

    # In case of request errors, use stale cache data if possible
    "stale_if_error": True,

    "serializer": "json",

    # This causes caching to not work unless decode_content = False
    # https://github.com/requests-cache/requests-cache/issues/963
    "backend": "filesystem",
    "decode_content": False
  }
  session = requests_cache.CachedSession('/tmp/CachedSession/', **copts)

  from datetime import datetime
  from urllib.parse import quote

  #headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
  headers = {'Accept': 'application/json'}
  url = "https://cdaweb.gsfc.nasa.gov/WS/cdasr/1/dataviews/sp_phys/datasets/AC_H2_MFI/orig_data/19970902T000000Z,20240323T230000Z"
  url = "https://spdf.gsfc.nasa.gov/pub/catalogs/all.xml"
  url = "https://httpbin.org/cache/10"
  resp = session.get(url, headers=headers)
  print(resp.from_cache)

if __name__ == '__main__':
  _requests_cache_bug()