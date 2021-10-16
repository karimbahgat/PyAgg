
import unittest

import pyagg

# base class

class BaseTestCases:

    class DrawShapes(unittest.TestCase):
        width = 200
        height = 200
        kwargs = {'fillcolor':'yellow', 'outlinecolor':'black'}
        output_prefix = 'size_units'

        def create_canvas(self):
            self.canvas = pyagg.Canvas(self.width, self.height, background='gray')
            self.canvas.percent_space()

        def save_canvas(self, name):
            print('save',self.output_prefix,name)
            self.canvas.save('outputs/{}_{}.png'.format(self.output_prefix, name))

        def test_circle(self):
            self.create_canvas()
            print(self.kwargs)
            self.canvas.draw_circle(xy=(50,50), **self.kwargs)
            self.save_canvas('circle')

        def test_box(self):
            self.create_canvas()
            print(self.kwargs)
            self.canvas.draw_box(xy=(50,50), **self.kwargs)
            self.save_canvas('box')

        def test_line(self):
            self.create_canvas()
            print(self.kwargs)
            self.canvas.draw_line([(5,50),(95,50)], **self.kwargs)
            self.save_canvas('line')

# px

class TestFillPixelUnits(BaseTestCases.DrawShapes):

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.output_prefix += '_fill_pixel'
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '{}px'.format(self.width//3)}
        self.kwargs.update(extra)

class TestOutlinePixelUnits(BaseTestCases.DrawShapes):

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.output_prefix += '_outline_pixel'
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '{}px'.format(self.width//3),
                'outlinewidth': '{}px'.format(2)}
        self.kwargs.update(extra)

# x/y

class TestFillXUnits(BaseTestCases.DrawShapes):
    
    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.output_prefix += '_fill_x'
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '{}x'.format(33)}
        self.kwargs.update(extra)

class TestOutlineXUnits(BaseTestCases.DrawShapes):

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.output_prefix += '_outline_x'
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '{}x'.format(33),
                'outlinewidth': '{}x'.format(1)}
        self.kwargs.update(extra)

# pt

class TestFillPointUnits(BaseTestCases.DrawShapes):
    
    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.output_prefix += '_fill_point'
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '{}pt'.format(5)}
        self.kwargs.update(extra)

class TestOutlinePointUnits(BaseTestCases.DrawShapes):
    
    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.output_prefix += '_outline_point'
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '{}pt'.format(5),
                'outlinewidth': '{}pt'.format(0.5)}
        self.kwargs.update(extra)

# cm

# mm

# in

# percwidth

# percheight

# percmin

# percmax


if __name__ == '__main__':
    unittest.main()
