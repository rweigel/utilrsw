"""
Usage:
  python release.py --help
"""

import os
import sys
import subprocess

def main(toml_path, pypi_config_file, increment_version=None, dry_run=False):

  toml = _read_toml(toml_path)

  version = toml.get('project', {}).get('version')
  if not version:
    print(f"Could not find [project] version in {toml_path}")
    sys.exit(1)

  if increment_version is not None:
    version = _increment_version(toml_path, version, increment_version, dry_run)

  # Check if gh CLI is installed
  if not dry_run:
    try:
      subprocess.run(['gh', '--version'], check=True, stdout=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
      print("Error: gh CLI is not installed. Please install it from https://cli.github.com/")
      sys.exit(1)

  # Create GitHub release
  cmd_list = ['gh', 'release', 'create', version, '-t', version, '-n', f'Release {version}']
  _run(cmd_list, dry_run)

  # Build package
  cmd_list = [sys.executable, '-m', 'build']
  _run(cmd_list, dry_run)

  # Upload package to PyPi
  cmd_list = ['twine', 'upload', '--config-file', pypi_config_file, 'dist/*']
  _run(cmd_list, dry_run)


def _increment_version(toml_path, version, increment, dry_run=False):
    parts = version.split('.')
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
      print(f"Version '{version}' is not in MAJOR.MINOR.PATCH format")
      sys.exit(1)
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    if increment == 'major':
      major += 1; minor = 0; patch = 0
    elif increment == 'minor':
      minor += 1; patch = 0
    elif increment == 'patch':
      patch += 1
    new_version = f"{major}.{minor}.{patch}"
    with open(toml_path, 'r') as f:
      toml_text = f.read()
    old_line = f'version = "{version}"'
    new_line = f'version = "{new_version}"'
    if old_line not in toml_text:
      print(f"Could not find '{old_line}' in {toml_path}")
      sys.exit(1)
    toml_text = toml_text.replace(old_line, new_line, 1)
    if dry_run:
      print(f"[dry-run] Would increment version {version} -> {new_version} in {toml_path}")
    else:
      with open(toml_path, 'w') as f:
        f.write(toml_text)
      print(f"Incremented version {version} -> {new_version} in {toml_path}")
    version = new_version
    return version


def _read_toml(toml_path):
  try:
    import tomllib
  except ImportError:
    import tomli as tomllib

  if not os.path.exists(toml_path):
    print(f"Could not find pyproject.toml at {toml_path}")
    sys.exit(1)

  with open(toml_path, 'rb') as f:
    data = tomllib.load(f)

  return data


def _cli():
  import argparse

  default_toml_path = './pyproject.toml'

  description = """
  Create GitHub release and upload package to PyPi.

  Must execute 'gh auth login' on command line before running this script.

  Version is read from pyproject.toml and can be incremented with --increment-version flag.
  """

  parser = argparse.ArgumentParser(
    description=description,
    formatter_class=argparse.RawTextHelpFormatter
  )
  parser.add_argument(
    'toml_path',
    nargs='?',
    default=default_toml_path,
    help=f'Path to pyproject.toml [{default_toml_path}]'
  )
  parser.add_argument(
    '--pypi-config-file',
    default=os.path.expanduser('~/.pypirc'),
    help='Path to PyPi config file (default: ~/.pypirc)'
  )
  parser.add_argument(
    '--increment-version',
    choices=['major', 'minor', 'patch'],
    help='Increment the release version (e.g. 1.0.0 -> 1.1.0 for minor).'
  )
  parser.add_argument(
    '--dry-run',
    action='store_true',
    help='Print the commands that would be executed without actually running them.'
  )

  return parser.parse_args()


def _run(cmd_list, dry_run):
  if dry_run:
    msg = "[dry-run] Would execute:"
  else:
    msg = "Executing:"
  print(msg, " ".join(cmd_list))
  if not dry_run:
    subprocess.run(cmd_list, check=True)


def _install_deps():
  try:
    import build  # noqa: F401
  except ImportError:
    cmd_list = [sys.executable, '-m', 'pip', 'install', 'build']
    print("Executing:", " ".join(cmd_list))
    subprocess.run(cmd_list, check=True)

  try:
    import twine  # noqa: F401
  except ImportError:
    cmd_list = [sys.executable, '-m', 'pip', 'install', 'twine']
    print("Executing:", " ".join(cmd_list))
    subprocess.run(cmd_list, check=True)

  try:
    import tomllib
  except ImportError:
    try:
      import tomli as tomllib
    except ImportError:
      cmd_list = [sys.executable, '-m', 'pip', 'install', 'tomli']
      print("Executing:", " ".join(cmd_list))
      subprocess.run(cmd_list, check=True)


def cli_entry():
  _install_deps()
  args = _cli()
  main(
    args.toml_path,
    args.pypi_config_file,
    increment_version=args.increment_version,
    dry_run=args.dry_run
  )


if __name__ == '__main__':
  cli_entry()
