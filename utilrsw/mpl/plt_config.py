def plt_config():
  import matplotlib
  from matplotlib import pyplot as plt
  matplotlib.use('Agg')
  matplotlib.pyplot.rcParams['font.family'] = 'Times New Roman'
  matplotlib.pyplot.rcParams['font.size'] = 15
  matplotlib.pyplot.rcParams['mathtext.fontset'] = 'cm'
  matplotlib.pyplot.rcParams['figure.constrained_layout.use'] = True
  matplotlib.pyplot.rcParams['figure.figsize'] = (8.5, 11)
