# utilrsw

Misc Python functions.

# Install with minimal dependencies

```
git clone https://github.com/rweigel/utilrsw
pip install -e .
```

To use in `setup.py`, use

``
install_requires = [
  ...
  "utilrsw @ git+https://github.com/rweigel/datetick@main"
]
```

In `pyproject.toml`, use
```
dependencies = [..., "utilrsw @ git+https://github.com/rweigel/datetick@main"]

# Install with dependencies

```
pip install -e utilrsw[X]
# where
# X is one of mpl, net, svg, time, test, xprint, release
# e.g.,
pip install -e utilrsw[net]
# or a comma-separated list, e.g.,
pip install -e utilrsw[mpl,net]
```

Also,

```
utilrsw[net] @ git+https://github.com/rweigel/datetick@main
utilrsw[mpl,net] @ git+https://github.com/rweigel/datetick@main
```
