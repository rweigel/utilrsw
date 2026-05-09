def savefig(fname, fdir='', formats=None, subdirs=False, bbox_inches='tight'):

  import os
  from matplotlib import pyplot as plt

  if fdir is None:
    fdir = ''

  if formats is None:
    formats = ['svg', 'png', 'pdf']
  else:
    if isinstance(formats, str):
      formats = [formats]

  if isinstance(subdirs, bool):
    if subdirs is True:
      subdirs = formats
    else:
      subdirs = []

  for format in formats:
    kwargs = {'bbox_inches': bbox_inches}
    if format == 'png':
      kwargs['dpi'] = 300

    if format in subdirs:
      fname_full = os.path.join(fdir, format, f'{fname}.{format}')
    else:
      fname_full = os.path.join(fdir, f'{fname}.{format}')

    os.makedirs(os.path.dirname(fname_full), exist_ok=True)
    print(f"  Writing {fname_full}")
    plt.savefig(fname_full, bbox_inches=bbox_inches)

  plt.close()
