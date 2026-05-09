def adjust_legend(axis, debug=False):
  """Adjust the legend position to avoid overlapping with data points.

  Given a matplotlib axis with a legend, compute max data y-value below the
  legend's x-position range, and shift the legend up so that its lower edge
  aligns with that max y-value.
  """

  import numpy
  import matplotlib.legend as mlegend

  if isinstance(axis, (list, tuple, numpy.ndarray)):
    for ax in axis:
      adjust_legend(ax, debug=debug)
    return

  # Collect all legends: the axis legend plus any added as artists
  legends = [child for child in axis.get_children() if isinstance(child, mlegend.Legend)]
  if not legends:
    return
  for legend in legends:
    _adjust_one_legend(axis, legend, debug=debug)


def _adjust_one_legend(axis, legend, debug=False):
  import numpy
  import datetime
  import matplotlib

  # Get current legend location and set to upper left to get correct bbox
  loc = legend._get_loc()
  locs_known = {
    0: 'best',
    1: 'upper right',
    2: 'upper left',
    3: 'lower left',
    4: 'lower right',
    5: 'right',
    6: 'center left',
    7: 'center right',
    8: 'lower center',
    9: 'upper center',
    10: 'center'
  }
  # Map numeric loc to string
  loc_str = locs_known.get(loc, 'upper left')
  if loc == 0:
    loc_str = 'upper left'

  if loc_str not in ('upper left', 'upper right', 'upper center'):
    if debug:
      print(f"  Legend location '{loc_str}' not supported for adjustment. Skipping.")
    return

  # Place legend at the detected position to measure its bbox
  legend.set_loc(loc_str)
  renderer = axis.figure.canvas.get_renderer()
  bbox = legend.get_window_extent(renderer=renderer)
  bbox_axes = bbox.transformed(axis.transAxes.inverted())

  xmin_data = axis.get_xlim()[0]
  xmax_data = axis.get_xlim()[1]
  x_span = xmax_data - xmin_data

  legend_x0 = xmin_data + bbox_axes.x0 * x_span
  legend_x1 = xmin_data + bbox_axes.x1 * x_span
  legend_y0 = axis.get_ylim()[0] + bbox_axes.y0 * (axis.get_ylim()[1] - axis.get_ylim()[0])

  # x-range of data that could be hidden beneath the legend
  if loc_str == 'upper left':
    def x_mask(xd): return xd <= legend_x1
  elif loc_str == 'upper right':
    def x_mask(xd): return xd >= legend_x0
  else:  # upper center
    def x_mask(xd): return (xd >= legend_x0) & (xd <= legend_x1)

  max_y = legend_y0

  for line in axis.get_lines():
    if line.get_visible() and len(line.get_ydata()) > 0:
      xdata = line.get_xdata()
      ydata = numpy.array(line.get_ydata())

      if isinstance(xdata[0], numpy.datetime64) or isinstance(xdata[0], datetime.datetime):
        xdata = matplotlib.dates.date2num(xdata)

      filtered_y = ydata[x_mask(numpy.asarray(xdata, dtype=float))]
      if len(filtered_y) > 0:
        line_max = numpy.nanmax(filtered_y)
        if line_max > max_y:
          max_y = line_max

  # Compute anchor position in axes fraction coordinates
  y0_ax, y1_ax = axis.get_ylim()
  anchor_y = (max_y - y0_ax) / (y1_ax - y0_ax)

  if loc_str == 'upper left':
    # Place left edge of legend at the first x-tick
    xticks = axis.get_xticks()
    first_tick = xticks[0]
    xlim0, xlim1 = axis.get_xlim()
    anchor_x = (first_tick - xlim0) / (xlim1 - xlim0)
    new_loc = 'lower left'
  elif loc_str == 'upper right':
    # Place right edge of legend at the last x-tick
    xticks = axis.get_xticks()
    last_tick = xticks[-1]
    xlim0, xlim1 = axis.get_xlim()
    anchor_x = (last_tick - xlim0) / (xlim1 - xlim0)
    new_loc = 'lower right'
  else:  # upper center
    anchor_x = (bbox_axes.x0 + bbox_axes.x1) / 2
    new_loc = 'lower center'

  legend_top_axes = anchor_y + bbox_axes.height

  # Convert 3 pixels to axes-fraction and shift anchor up to account for
  # small gap between legend and data points. Ideally we would know extent
  # of the highest in pixels.
  ax_height_px = axis.get_window_extent(renderer).height
  anchor_y = anchor_y + 3 / ax_height_px

  legend.set_bbox_to_anchor((anchor_x, anchor_y))
  legend.set_loc(new_loc)

  _adjust_title(axis, legend, legend_top_axes=legend_top_axes, debug=debug)


def _adjust_title(ax, legend, legend_top_axes=None, debug=False):
  if legend is None or legend_top_axes is None:
    return
  if debug:
    print(f"  Legend top in axes fraction: {legend_top_axes:.3f}")
  if legend_top_axes > 1.0:
    import matplotlib
    overshoot_frac = legend_top_axes - 1.0
    renderer = ax.figure.canvas.get_renderer()
    ax_height_pts = ax.get_window_extent(renderer).height * 72 / ax.figure.dpi
    default_pad = matplotlib.rcParams.get('axes.titlepad', 6.0)
    new_pad = default_pad + overshoot_frac * ax_height_pts
    if debug:
      print(f"  Setting title pad to {new_pad:.1f} pts (was {default_pad:.1f})")
    ax.set_title(ax.get_title(), pad=new_pad)


if __name__ == "__main__":
  import matplotlib.pyplot as plt
  import numpy

  fig, ax = plt.subplots()

  x = numpy.linspace(0, 10, 100)
  y1 = numpy.sin(x)
  y2 = 0.5 * numpy.cos(x) + 0.5

  ax.plot(x, y1, label='sin(x)')
  ax.plot(x, y2, label='0.5*cos(x)+0.5')
  ax.spines['bottom'].set_visible(False)
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['left'].set_visible(False)
  # TODO: Create adjust_title() to put above legend.
  ax.set_title('Adjust Legend Example\n')
  ax.legend(ncols=2)
  ax.grid()

  adjust_legend(ax)

  plt.show()