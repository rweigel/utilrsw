# TODO: Automate.

from . import array_to_dict as array_to_dict
array_to_dict = array_to_dict.array_to_dict

from . import compare_dicts as compare_dicts
compare_dicts = compare_dicts.compare_dicts

from . import get_file as get_file
get_conditional = get_file.get_conditional
get_file = get_file.get_file

from . import get_json as get_json
get_json = get_json.get_json

from . import get_path as get_path
get_path = get_path.get_path

from . import file_parts as file_parts
file_parts = file_parts.file_parts

from . import flatten_dicts as flatten_dicts
flatten_dicts = flatten_dicts.flatten_dicts

from . import format_exponent as format_exponent
from .format_exponent import format_exponent

from . import logger as logger
logger = logger.logger

from . import mkdir as mkdir
mkdir = mkdir.mkdir

from . import pad_iso8601 as pad_iso8601
pad_iso8601 = pad_iso8601.pad_iso8601

from . import print_dict as print_dict
format_dict = print_dict.format_dict
print_dict = print_dict.print_dict

from . import read as read
read = read.read

from . import rm_path as rm_path
rm_path = rm_path.rm_path

from . import rm_if_empty as rm_if_empty
rm_if_empty = rm_if_empty.rm_if_empty

from . import set_path as set_path
set_path = set_path.set_path

from . import script_info as script_info
script_info = script_info.script_info

from . import servefs as servefs
servefs = servefs.servefs

from . import sort_dict as sort_dict
sort_dict = sort_dict.sort_dict

from . import svglinks as svglinks
svglinks = svglinks.svglinks

from . import timer as timer
tick = timer.tick
tock = timer.tock

from . import trim as trim
trim = trim.trim

from . import utc_now as utc_now
utc_now = utc_now.utc_now

from . import write as write
write = write.write

from . import xprint as xprint
xprint = xprint.xprint


from . import mpl as mpl

from . import time as time
