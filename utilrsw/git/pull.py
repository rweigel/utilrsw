def pull(repo_dir, repo_url, rebase=True, logger=None, logger_indent=''):
  # git -C servers pull --rebase
  import os
  from git import Repo

  def xprint(msg):
    if logger is not None:
      logger.info(f"{logger_indent}{msg}")
    else:
      print(f"{logger_indent}{msg}")

  if not os.path.isdir(os.path.join(repo_dir, '.git')):
    msg = f"{repo_dir} exists but is not a git repository."
    if logger is not None:
      logger.error(f"{logger_indent}{msg}")
    else:
      print(f"{logger_indent}{msg}")
    raise RuntimeError(msg)

  repo = Repo(repo_dir)
  if repo.is_dirty(untracked_files=True):
    xprint(f"{logger_indent}Stashing changes in {repo_dir}")
    repo.git.stash()

  if rebase:
    repo.git.pull('--rebase')
  else:
    repo.git.pull()