# Execute this from a directory outside of the utilrsw package, e.g.,
#   cp utilrsw/utilrsw/servefs_demo2.py /tmp
#   cd ../; python utilrsw/servefs_demo2.py

configs = {
    "server": {
        "--host": "0.0.0.0",
        "--port": 6002,
        "--workers": 2,
        "--no-access-log": True
    },
    "app": {
          "debug": True,
          "root": "."
      }
}
import utilrsw.uvicorn
utilrsw.uvicorn.run("utilrsw.servefs", configs)