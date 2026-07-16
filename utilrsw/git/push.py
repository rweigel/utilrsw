def push(repo_dir, repo_url, msg="", logger=None, logger_indent=''):
  import os
  from git import Repo

  def xprint(msg):
    if logger is not None:
      logger.info(f"{logger_indent}{msg}")
    else:
      print(f"{logger_indent}{msg}")


  if not os.path.isdir(os.path.join(repo_dir, '.git')):
    emsg = f"{repo_dir} does not exist or is not a git repository."
    if logger is not None:
      logger.error(f"{logger_indent}{emsg}")
    else:
      print(f"{logger_indent}{emsg}")
    raise RuntimeError(emsg)

  repo = Repo(repo_dir)

  try:
    xprint(f"Committing tracked changes in {repo_dir}")
    repo.git.commit('-a', '-m', msg)
  except Exception as e:
    estr = str(e)
    if 'nothing to commit' in estr.lower():
      xprint(f"{logger_indent}No changes to commit in {repo_dir}")
      return
    raise

  xprint(f"{logger_indent}Pushing {repo_dir} repo to remote")

  repo.remote().push()
