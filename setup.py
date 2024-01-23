from setuptools import setup, find_packages
from ethanalysis import __version__

setup(
    name='ethanalysis',
    version=__version__,

    url='https://github.com/ethan-r-hansen/ethanalysis',
    author='Ethan R. Hansen',
    author_email='hansen.ethan@gmail.com',

    py_modules=find_packages(),
    
    install_requires=[
        'scikit-rf',
        'numpy',
        'pandas'
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
    ],
)