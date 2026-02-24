def clone(repo_dir, repo_url, rebase=True, logger=None, logger_indent=''):
  import os
  from git import Repo

  def xprint(msg):
    if logger is not None:
      logger.info(f"{logger_indent}{msg}")
    else:
      print(f"{logger_indent}{msg}")

  if not os.path.exists(repo_dir):
    # git clone <repo_url>
    xprint(f"{logger_indent}Cloning {repo_url} into {repo_dir}")
    Repo.clone_from(repo_url, repo_dir)
    return
