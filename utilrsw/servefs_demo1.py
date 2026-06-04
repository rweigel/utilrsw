# Execute this from a directory outside of the utilrsw package, e.g.,
#   cp utilrsw/utilrsw/servefs_demo1.py /tmp
#   cd ../; python utilrsw/servefs_demo1.py

import utilrsw
import uvicorn

app_config = {
    "debug": True,
    "root": "."
}

app = utilrsw.servefs(app_config)
uvicorn.run(app, host="0.0.0.0", port=6002)
