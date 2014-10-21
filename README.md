# PyAgg

**Precompiled library for lightweight, easy, and convenient graphics rendering based on the aggdraw module**

*Karim Bahgat*

*October 2014*

## Introduction

There are many ways to create beautiful drawings and graphics in Python. However, the most commonly used one is Matplotlib, a 60 mb monster, which also requires another 60 mb titan Numpy. The size of these distributions may be a problem for a number of purposes when making distributable software or libraries. 

Another option is the wonderful and lightweight Aggdraw library, except the problem is it has no binary installers and requires the user to have a compiler, thus heightening the installation barrier and limiting the type of users that can use it. There are also a number of convenience barriers in its API that makes one have to stop and think instead of just creatively drawing away. It also has no way of saving or viewing the graphics one creates except if one has the PIL imaging library. 

A final option is the PyCairo package, but it is also a quite large package, can be troublesome to compile, rendering text is not straightforward and requires a lot of technical magic, it is slower than the other options, and its state-like API may seem unpythonic to some. 

The current library, PyAgg, aims to solve these problems. By building on the lightweight aggdraw module and including the necessary pre-compiled binaries for all Python and architecture versions in the same package, PyAgg is ready to use out of the box, no installation or compiling required. 

PyAgg also wraps around and offers several convenience functions for easier no-brain drawing, such as a much more intuitive drawing transform, smoothing of coordinate sequences, and viewing, rotating, stretching, cropping, and saving the image. The only requirement is PIL/Pillow. 

Also available are a set of basic data graphs such as linegraph, scatterplot, histogram, etc. 

Heres to at least another 5 years of beautiful and lightweight Python image drawing - cheers! After that, Python 2x will no longer be maintained, and while people can still continue to use it, it is likely that most people will be using Python 3x. At that point someone will have to update the c++ Aggdraw wrapper so it can be compiled for Python 3x if Python users are to continue to enjoy the power of the Agg graphics library.
