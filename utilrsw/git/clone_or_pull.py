def clone_or_pull(repo_dir, repo_url, rebase=True, logger=None, logger_indent=''):
  import os
  import utilrsw.git

  if os.path.isdir(repo_dir):
    utilrsw.git.pull(repo_dir, repo_url, logger=logger, logger_indent=logger_indent)
  else:
    utilrsw.git.clone(repo_dir, repo_url, rebase=rebase, logger=logger, logger_indent=logger_indent)
