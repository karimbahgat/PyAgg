import pipy
 
packpath = "pyagg"
pipy.define_upload(packpath,
                   name="PyAgg",
                   description="Simple user-oriented graphics drawing and image manipulation.",
                   author="Karim Bahgat",
                   author_email="karim.bahgat.norway@gmail.com",
                   license="MIT",
                   url="http://github.com/karimbahgat/PyAgg",
                   requires=["PIL"],
                   keywords="graphics rendering drawing visualization imaging AGG aggdraw",
                   classifiers=["License :: OSI Approved",
                                "Programming Language :: Python",
                                "Development Status :: 4 - Beta",
                                "Intended Audience :: Developers",
                                "Intended Audience :: Science/Research",
                                'Intended Audience :: End Users/Desktop',
                                "Topic :: Scientific/Engineering :: Visualization",
                                "Topic :: Multimedia :: Graphics",
                                "Topic :: Scientific/Engineering :: GIS"],
                   changes=[],
                   )

#pipy.upload_test(packpath)
pipy.generate_docs(packpath)

#pipy.upload(packpath)
