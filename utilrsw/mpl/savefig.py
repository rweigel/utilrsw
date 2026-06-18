def savefig(fname, fdir='', exclude_date_metadata=True, formats=None, subdirs=False, bbox_inches='tight'):

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
    rc = {}
    kwargs = {'bbox_inches': bbox_inches}
    if format == 'png':
      kwargs['dpi'] = 300

    """
    Note: If exclude_date_metadata, don't include metadata in SVG and PDF to
          avoid non-deterministic content that prevents caching and causes
          differences in version controlled files
    """
    if format == 'svg':
      kwargs['metadata'] = {"Date": None} # See note above.
      # svg.fonttype => Don't convert text to paths to keep it searchable and selectable
      # svg.hashsalt => See note above
      rc = {'svg.fonttype': 'none'}
      if exclude_date_metadata:
        rc['svg.hashsalt'] = '67'

    if format == 'pdf' and exclude_date_metadata:
      # See note above
      kwargs['metadata'] = {'CreationDate': None, 'ModDate': None}

    if format in subdirs:
      fname_full = os.path.join(fdir, format, f'{fname}.{format}')
    else:
      fname_full = os.path.join(fdir, f'{fname}.{format}')

    os.makedirs(os.path.dirname(fname_full), exist_ok=True)
    print(f"  Writing {fname_full}")
    with plt.rc_context(rc):
      plt.savefig(fname_full, **kwargs)

  plt.close()
