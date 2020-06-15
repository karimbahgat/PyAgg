import pipy
 
packpath = "pyagg"
pipy.define_upload(packpath,
                   name="PyAgg",
                   description="Simple user-oriented graphics drawing and image manipulation.",
                   author="Karim Bahgat",
                   author_email="karim.bahgat.norway@gmail.com",
                   license="MIT",
                   url="http://github.com/karimbahgat/PyAgg",
                   requires=["PIL", "aggdraw"],
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
                   changes=["Plenty of new feature additions",
                            "Drop precompiled aggdraw versions in favor of new maintained version of aggdraw",
                            "Plenty of bug fixes"],
                   )

pipy.generate_docs(packpath)
#pipy.upload_test(packpath)
pipy.upload(packpath)
