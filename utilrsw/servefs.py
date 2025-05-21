def servefs(app=None, run=True, root=".", host="0.0.0.0", port=6001, workers=1):

  import os
  import html
  import datetime
  import pathlib
  import urllib.parse

  import uvicorn

  from fastapi import FastAPI, HTTPException
  from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
  from fastapi.middleware.cors import CORSMiddleware

  import logging
  logging.basicConfig()
  logger = logging.getLogger("servefs")
  logger.setLevel(logging.DEBUG)

  if app is None:
    app = FastAPI()

  STREAM_THRESHOLD = 10 * 1024 * 1024  # 10 MB threshold for streaming

  # Removes: server: uvicorn from HTTP response headers
  uvicorn.SERVER_SOFTWARE = None

  # Convert root to an absolute path
  root = os.path.abspath(root)

  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["GET", "HEAD"],
      allow_headers=["Content-Type"]
  )

  @app.get("{path:path}", response_class=HTMLResponse)
  async def serve_directory_or_file(path: str = ""):
    """Serve directory listing or a file."""

    if path.startswith(".."):
      # Prevent directory traversal attacks
      # Note that
      #   http://server/../
      #   http://server/./
      #   http://server/./../
      # results in
      # path = "/" being passed to this function, so this is not needed.
      raise HTTPException(status_code=403, detail="Permission denied")

    # path[1:] to remove leading slash
    full_path = pathlib.Path(os.path.join(root, path[1:]))
    logger.debug(f"Requested path: {path}")
    logger.debug(f"root path:      {root}")
    logger.debug(f"Resolved path:  {full_path}")

    if full_path.is_file():
      if full_path.stat().st_size < STREAM_THRESHOLD:
        return FileResponse(full_path)
      else:
        # If the file size > STREAM_THRESHOLD, stream it
        def iterfile(full_path):
          with open(full_path, mode="rb") as file_like:
            yield from file_like
        return StreamingResponse(iterfile(full_path))

    # If the path is not a directory, send 404 error
    if not full_path.is_dir():
        raise HTTPException(status_code=404, detail="File or directory not found")

    # Generate directory listing
    try:
      items = os.listdir(full_path)
    except PermissionError:
      raise HTTPException(status_code=403, detail="Permission denied")

    server_path = html.escape(urllib.parse.unquote(path), quote=False)

    return HTMLResponse(content=_dir_listing(full_path, server_path, items))

  @app.head("{path:path}")
  async def head_request(path: str = ""):
      """Handle HEAD requests."""
      full_path = pathlib.Path(os.path.join(root, path))

      # Add Last-Modified header for files
      if full_path.is_file():
        last_modified = datetime.datetime.fromtimestamp(full_path.stat().st_mtime)
        last_modified_str = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
        return FileResponse(full_path, headers={
          "Content-Length": str(full_path.stat().st_size),
          "Last-Modified": last_modified_str
        })

      # If the path is not a directory, raise a 404 error
      if not full_path.is_dir():
        raise HTTPException(status_code=404, detail="File or directory not found")

      # For directories, return a generic response with no body
      return HTMLResponse(content="", headers={"Content-Type": "text/html"})

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
  """.replace("\n  ", "\n")[1:]

  def _dir_listing(full_path, server_path, items):

    items.sort(key=lambda a: a.lower())
    rows = []

    for name in items:
        fullname = pathlib.Path(full_path / name)
        size = fullname.stat().st_size
        displayname = linkname = name

        # Append / for directories or @ for symbolic links
        if fullname.is_dir():
            displayname = name + "/"
            linkname = name + "/"
        if fullname.is_symlink():
            displayname = name + "@"

        href = urllib.parse.quote(linkname, errors="surrogatepass")
        text = html.escape(displayname, quote=False)
        modified = datetime.datetime.fromtimestamp(fullname.stat().st_mtime)
        modified = modified.strftime('%Y-%m-%dT%H:%M:%SZ')
        a = f'<a href="{href}">{text}</a>'
        rows.append(f'      <tr><td>{a}</td><td>{size}</td><td>{modified}</td></tr>')

    # Replace placeholders in the template
    listing_html = _DIR_LISTING.replace("__DIRECTORY__", server_path)
    listing_html = listing_html.replace("__DIRECTORY_HTML__", "\n".join(rows))
    return listing_html

  if run:
    uvicorn.run(app, host=host, port=port, server_header=False, workers=1)

  return app

if __name__ == '__main__':
  servefs(run=True)