try: from setuptools import setup
except: from distutils.core import setup

setup(	long_description=open("README.rst").read(), 
	name="""PyAgg""",
	license="""MIT""",
	author="""Karim Bahgat""",
	author_email="""karim.bahgat.norway@gmail.com""",
	url="""http://github.com/karimbahgat/PyAgg""",
	package_data={'pyagg': ['fontTools\\ttLib\\tables\\table_API_readme.txt', 'precompiled\\mac\\bit64\\py27\\aggdraw.so', 'precompiled\\win\\bit32\\py26\\aggdraw.pyd', 'precompiled\\win\\bit32\\py27\\aggdraw.pyd', 'precompiled\\win\\bit64\\py27\\aggdraw.pyd']},
	version="""0.1""",
	keywords="""graphics rendering drawing visualization imaging AGG aggdraw""",
	packages=['pyagg', 'pyagg\\fontTools', 'pyagg\\fontTools\\encodings', 'pyagg\\fontTools\\misc', 'pyagg\\fontTools\\pens', 'pyagg\\fontTools\\ttLib', 'pyagg\\fontTools\\ttLib\\tables', 'pyagg\\precompiled', 'pyagg\\precompiled\\mac', 'pyagg\\precompiled\\mac\\bit64', 'pyagg\\precompiled\\mac\\bit64\\py27', 'pyagg\\precompiled\\win', 'pyagg\\precompiled\\win\\bit32', 'pyagg\\precompiled\\win\\bit32\\py26', 'pyagg\\precompiled\\win\\bit32\\py27', 'pyagg\\precompiled\\win\\bit64', 'pyagg\\precompiled\\win\\bit64\\py26', 'pyagg\\precompiled\\win\\bit64\\py27'],
	requires=['PIL'],
	classifiers=['License :: OSI Approved', 'Programming Language :: Python', 'Development Status :: 4 - Beta', 'Intended Audience :: Developers', 'Intended Audience :: Science/Research', 'Intended Audience :: End Users/Desktop', 'Topic :: Scientific/Engineering :: Visualization', 'Topic :: Multimedia :: Graphics', 'Topic :: Scientific/Engineering :: GIS'],
	description="""Simple user-oriented graphics drawing and image manipulation.""",
	)
