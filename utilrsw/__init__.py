from importlib.metadata import version

__version__ = version("utilrsw")

from .array_to_dict import array_to_dict
from .compare_dicts import compare_dicts
from .file_parts import file_parts
from .flatten_dicts import flatten_dicts
from .get_func import get_func
from .get_path import get_path
from .hline import hline
from .logger import logger
from .map_dict import map_dict
from .merge_dicts import merge_dicts
from .mkdir import mkdir
from .print_dict import format_dict, print_dict
from .read import read
from .reorder_dict import reorder_dict
from .rm_if_empty import rm_if_empty
from .rm_path import rm_path, rm_paths
from .run_parallel import run_parallel
from .run_serial import run_serial
from .script_info import script_info
from .servefs import servefs
from .set_path import set_path
from .sort_dict import sort_dict
from .timer import tick, tock
from .trim import trim
from .write import write
from .xprint import xprint

from . import git as git
from . import mpl as mpl
from . import net as net
from . import np as np
from . import svg as svg
from . import test as test
from . import time as time
