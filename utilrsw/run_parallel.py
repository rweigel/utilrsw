def run_parallel(fn, jobs, max_workers):
  from concurrent.futures import ProcessPoolExecutor, as_completed

  with ProcessPoolExecutor(max_workers=max_workers) as executor:
    futures = {executor.submit(fn, *job): job for job in jobs}
    try:
      for future in as_completed(futures):
        job_args = futures[future]
        try:
          future.result()
        except Exception as exc:
          fn_name = fn.__name__ if hasattr(fn, '__name__') else str(fn)
          raise RuntimeError(f"Failed processing {fn_name} with args {job_args}: {exc}") from exc
    except KeyboardInterrupt:
      executor.shutdown(wait=False, cancel_futures=True)
      raise

def _demo_fn(x, letter):
  # Function must be at top level to be picklable for multiprocessing
  import time
  print(f"_demo_fn started with arguments x = {x} and letter = {letter}")
  time.sleep(1)
  print(f"_demo_fn finished with arguments x = {x} and letter = {letter}")

def _run_serial_demo():

  jobs = [(1, 'a'), (2, 'b'), (3, 'c'), (4, 'd')]
  try:
    run_parallel(_demo_fn, jobs, max_workers=2)
  except RuntimeError as exc:
    print(f"Caught error: {exc}")


if __name__ == "__main__":
  _run_serial_demo()
