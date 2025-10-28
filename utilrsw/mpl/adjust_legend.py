def adjust_legend(axis):
  """Adjust the legend position to avoid overlapping with data points.

  Given a matplotlib axis with a legend, compute max data y-value below the
  legend's x-position range, and shift the legend up so that its lower edge
  aligns with that max y-value.
  """

  import numpy
  import datetime
  import matplotlib

  # Make lower edge of legend align with highest data point in axis
  def y_to_bbox_anchor(y_data):
    # Get current y-limits
    y0, y1 = axis.get_ylim()
    # Map y_data to axes fraction (0 at bottom, 1 at top)
    y_frac = (y_data - y0) / (y1 - y0)
    # bbox_to_anchor is (x, y) in axes fraction coordinates
    return (0, y_frac)

  legend = axis.get_legend()
  if legend is None:
    return

  legend.set_loc('upper left')
  # Get extent of legend along x axis in axis coordinates
  renderer = axis.figure.canvas.get_renderer()
  bbox = legend.get_window_extent(renderer=renderer)
  bbox_axes = bbox.transformed(axis.transAxes.inverted())
  # Convert legend_x0 from axis coordinates to data coordinates
  #legend_x0 = axis.get_xlim()[0] + bbox_axes.x0 * (axis.get_xlim()[1] - axis.get_xlim()[0])
  legend_x1 = axis.get_xlim()[0] + bbox_axes.x1 * (axis.get_xlim()[1] - axis.get_xlim()[0])
  legend_y0 = axis.get_ylim()[0] + bbox_axes.y0 * (axis.get_ylim()[1] - axis.get_ylim()[0])
  #legend_width = legend_x1 - legend_x0
  #print(f"Legend x extent in axis coordinates: x0={legend_x0}, x1={legend_x1}, width={legend_width}")

  max_y = legend_y0
  #print(f"Legend bottom: {max_y}")
  for line in axis.get_lines():
    if line.get_visible() and len(line.get_ydata()) > 0:
      xdata = line.get_xdata()
      ydata = numpy.array(line.get_ydata())

      if isinstance(xdata[0], numpy.datetime64) or isinstance(xdata[0], datetime.datetime):
        xdata = matplotlib.dates.date2num(xdata)

      mask = xdata < legend_x1
      filtered_y = ydata[mask]
      if len(filtered_y) > 0:
        line_max = numpy.nanmax(filtered_y)
        if line_max > max_y:
          max_y = line_max

  #print(f"Max data y below legend: {max_y}")
  y0, y1 = axis.get_ylim()
  legend.set_bbox_to_anchor(y_to_bbox_anchor(max_y))
  legend.set_loc('lower left')

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