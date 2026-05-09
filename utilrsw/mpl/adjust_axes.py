def adjust_axes(axis, which='both', dx=0.15, dy=0.15, debug=False):
  import numpy

  if isinstance(axis, (list, tuple, numpy.ndarray)):
    for ax in axis:
      adjust_axes(ax, which=which)
    return
  # Prevent offset notation on y-axis (e.g., 2.01e4)
  axis.get_yaxis().get_major_formatter().set_useOffset(False)

  # Remove short tick lines next to axis numbers
  axis.tick_params(axis='x', length=0)
  axis.tick_params(axis='x', which='minor', length=0)
  axis.tick_params(axis='y', length=0)
  axis.tick_params(axis='y', which='minor', length=0)
  axis.spines['bottom'].set_visible(False)
  axis.spines['top'].set_visible(False)
  axis.spines['right'].set_visible(False)
  axis.spines['left'].set_visible(False)

  which_axes = ['x', 'y'] if which == 'both' else [which]
  for which in which_axes:
    get_ticks = axis.get_xticks if which == 'x' else axis.get_yticks
    set_ticks = axis.set_xticks if which == 'x' else axis.set_yticks
    set_lim = axis.set_xlim if which == 'x' else axis.set_ylim

    ticks = get_ticks()

    if debug:
      print(f"  Original {which}-ticks: {ticks}")

    all_lines = get_lines(axis, which)
    if len(all_lines) == 0:
      if debug:
        print(f"    No lines with data in {which}-direction. Skipping adjustment.")
      continue
    all_data = numpy.concatenate(all_lines)
    min_data = all_data.min()
    max_data = all_data.max()
    if debug:
      print(f"    Data {which}-range: min={min_data}, max={max_data}")
    all_data = numpy.concatenate(all_lines)

    min_data = all_data.min()
    max_data = all_data.max()

    if all_data.dtype != ticks.dtype:
      if debug:
        print(f"    Data and {which}-ticks have same dtype {all_data.dtype}. Adjustment not implemented.")
      continue

    # If no data below second tick label, remove that tick label
    if min_data >= ticks[1]:
      if debug:
        print(f"    Removing {which}-tick {ticks[1]} since min={min_data} > {ticks[1]}")
      set_ticks(ticks[1:])

    if debug:
      print(f"    Adjusted {which}-ticks: {get_ticks()}")

    ticks = get_ticks()
    tick_delta = ticks[1] - ticks[0]
    set_lim(ticks[0] - dx*tick_delta, ticks[-1] + dy*tick_delta)

    set_ticks(ticks)

def get_lines(axis, which):
  import datetime
  import numpy
  import matplotlib

  result = []
  for line in axis.get_lines():
    data = line.get_xdata() if which == 'x' else line.get_ydata()
    #print(f"  Line {line.get_label()} {which}-data: {data}")
    if line.get_transform() != axis.transData:
      # Convert data from axes fraction to data coordinates
      lim = axis.get_xlim() if which == 'x' else axis.get_ylim()
      #data = lim[0] + (lim[1] - lim[0]) * numpy.array(data)
      #result.append(data)
      continue

    if isinstance(data[0], numpy.datetime64) or isinstance(data[0], datetime.datetime):
      data = matplotlib.dates.date2num(data)

    result.append(data)

  return result
