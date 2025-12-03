from setuptools import setup, find_packages

# Need requests_cache 1.2 because of
# https://github.com/requests-cache/requests-cache/issues/927
# and fact that https://spase-metadata.org/ returns json with
# "Content-Type": "application/json; charset=utf-8"
# (charset=utf-8 is redundant and causes requests_cache not not cache
# _decoded_content)
# See also utilrsw/get_json.py/_requests_cache_bug()
install_requires = [
    "requests_cache>=1.2.1",
    "deepdiff>=6.3.1",
    "xmltodict",
    "pyyaml",
    "lxml",
    "typeguard",
]

# Make the default install include the full set of dependencies. Provide a
# "minimal" extra to allow installing with no dependencies when desired.

# Installs all normal deps
#   pip install utilrsw
#   pip install utilrsw[full]
# Installs no extra deps
#   pip install utilrsw[minimal]
# Install only deps for xprint
#   pip install utilrsw[xprint]

extras_require = {
    "full": install_requires,
    "minimal": [],
    "xprint": []
}

setup(
    name='utilrsw',
    version='0.0.2',
    author='Bob Weigel',
    author_email='rweigel@gmu.edu',
    packages=find_packages(),
    license='LICENSE.txt',
    description='Misc utility functions.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=install_requires,
    extras_require=extras_require,
)
