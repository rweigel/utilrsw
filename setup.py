import sys
from setuptools import setup, find_packages

extras_require = {
    "mpl": ["matplotlib"],
    "net": ["requests", "xmltodict", "requests_cache>=1.2.1", "deepdiff>=6.3.1"],
    "svg": ["lxml"],
    "test": [],
    "time": [],
    "xprint": [],
    "scm": ["twine", "build"] + ([] if sys.version_info >= (3, 11) else ["tomli"]),
}

extras_require["full"] = [pkg for deps in extras_require.values() for pkg in deps]

install_requires = ["typeguard"]

setup(
    name='utilrsw',
    use_scm_version={
        "version_scheme": "post-release",
    },
    setup_requires=['setuptools_scm'],
    author='Bob Weigel',
    author_email='rweigel@gmu.edu',
    packages=find_packages(),
    license='LICENSE.txt',
    description='Misc utility functions.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'scm-release=utilrsw.scm.release:cli_entry',
        ],
    },
)
