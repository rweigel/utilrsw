def run_serial(fn, jobs):
  for job_args in jobs:
    try:
      fn(*job_args)
    except Exception as exc:
      fn_name = fn.__name__ if hasattr(fn, '__name__') else str(fn)
      raise RuntimeError(f"Failed processing {fn_name} with args {job_args}: {exc}") from exc

def run_serial_demo():
  import time

  def _demo_fn(x, letter):
    print(f"_demo_fn started with arguments x = {x} and letter = {letter}")
    time.sleep(1)
    print(f"_demo_fn finished with arguments x = {x} and letter = {letter}")

  jobs = [(1, 'a'), (2, 'b'), (3, 'c'), (4, 'd')]
  try:
    run_serial(_demo_fn, jobs)
  except RuntimeError as exc:
    print(f"Caught error: {exc}")

if __name__ == "__main__":
  run_serial_demo()