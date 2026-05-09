def set_fontsize(axis=None, fontsize=16, fontParamsDefault=None):

  import numpy
  if isinstance(axis, (list, tuple, numpy.ndarray)):
    for ax in axis:
      set_fontsize(axis=ax, fontsize=fontsize)
    return

  fontParamsDefault = {
      'font.size': fontsize,
      'figure.titlesize': fontsize,
      'axes.titlesize': fontsize,
      'axes.labelsize': fontsize,
      'xtick.labelsize': fontsize,
      'ytick.labelsize': fontsize,
      'legend.fontsize': fontsize,
      'legend.title_fontsize': fontsize,
  }
  if fontParamsDefault is not None:
    fontParamsDefault.update(fontParamsDefault)

  if axis is None:
    from matplotlib import rcParams
    rcParams.update(fontParamsDefault)
    return

  # Apply only to the given axis
  axis.title.set_fontsize(fontParamsDefault['axes.titlesize'])
  axis.xaxis.label.set_fontsize(fontParamsDefault['axes.labelsize'])
  axis.yaxis.label.set_fontsize(fontParamsDefault['axes.labelsize'])
  axis.tick_params(axis='x', labelsize=fontParamsDefault['xtick.labelsize'])
  axis.tick_params(axis='y', labelsize=fontParamsDefault['ytick.labelsize'])
  legend = axis.get_legend()
  if legend is not None:
    for text in legend.get_texts():
      text.set_fontsize(fontParamsDefault['legend.fontsize'])
    if legend.get_title():
      legend.get_title().set_fontsize(fontParamsDefault['legend.title_fontsize'])
