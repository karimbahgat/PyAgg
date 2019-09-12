try: from setuptools import setup
except: from distutils.core import setup

setup(	long_description=open("README.rst").read(), 
	name="""PyAgg""",
	license="""MIT""",
	author="""Karim Bahgat""",
	author_email="""karim.bahgat.norway@gmail.com""",
	url="""http://github.com/karimbahgat/PyAgg""",
	package_data={'pyagg': ['precompiled/unix/bit64/py27/aggdraw.so', 'precompiled/win/bit32/py26/aggdraw.pyd', 'precompiled/win/bit32/py27/aggdraw.pyd', 'precompiled/win/bit64/py27/aggdraw.pyd']},
	version="""0.2.0""",
	keywords="""graphics rendering drawing visualization imaging AGG aggdraw""",
	packages=['pyagg'],
	requires=['PIL'],
	classifiers=['License :: OSI Approved', 'Programming Language :: Python', 'Development Status :: 4 - Beta', 'Intended Audience :: Developers', 'Intended Audience :: Science/Research', 'Intended Audience :: End Users/Desktop', 'Topic :: Scientific/Engineering :: Visualization', 'Topic :: Multimedia :: Graphics', 'Topic :: Scientific/Engineering :: GIS'],
	description="""Simple user-oriented graphics drawing and image manipulation.""",
	)
