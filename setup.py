try: from setuptools import setup
except: from distutils.core import setup

setup(	long_description=open("README.rst").read(), 
	long_description_content_type="text/x-rst",
	name="""PyAgg""",
	license="""MIT""",
	author="""Karim Bahgat""",
	author_email="""karim.bahgat.norway@gmail.com""",
	url="""http://github.com/karimbahgat/PyAgg""",
	package_data={'pyagg': ['fonts/DejaVuMathTeXGyre.ttf', 'fonts/DejaVuSans-Bold.ttf', 'fonts/DejaVuSans-BoldOblique.ttf', 'fonts/DejaVuSans-Oblique.ttf', 'fonts/DejaVuSans.ttf', 'fonts/DejaVuSerif-Bold.ttf', 'fonts/DejaVuSerif-BoldItalic.ttf', 'fonts/DejaVuSerif-Italic.ttf', 'fonts/DejaVuSerif.ttf']},
	version="""0.3.0""",
	keywords="""graphics rendering drawing visualization imaging AGG aggdraw""",
	packages=['pyagg'],
	requires=['PIL', 'aggdraw'],
	classifiers=['License :: OSI Approved', 'Programming Language :: Python', 'Development Status :: 4 - Beta', 'Intended Audience :: Developers', 'Intended Audience :: Science/Research', 'Intended Audience :: End Users/Desktop', 'Topic :: Scientific/Engineering :: Visualization', 'Topic :: Multimedia :: Graphics', 'Topic :: Scientific/Engineering :: GIS'],
	description="""Simple user-oriented graphics drawing and image manipulation.""",
	)
