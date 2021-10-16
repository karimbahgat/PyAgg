
import unittest

import pyagg

# base class

class BaseTestCases:

    class DrawShapes(unittest.TestCase):
        width = 200
        height = 200
        kwargs = {'fillcolor':'yellow', 'outlinecolor':'black'}
        #output_prefix = ''

        def create_canvas(self):
            self.canvas = pyagg.Canvas(self.width, self.height, background='gray')
            self.canvas.percent_space()
            self.canvas.draw_grid(25, 25)

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

        def test_triangle_0(self):
            self.create_canvas()
            print(self.kwargs)
            self.canvas.draw_triangle(xy=(50,50), direction=0, **self.kwargs)
            self.save_canvas('triangle_0')

        def test_triangle_90(self):
            self.create_canvas()
            print(self.kwargs)
            self.canvas.draw_triangle(xy=(50,50), direction=90, **self.kwargs)
            self.save_canvas('triangle_90')

        def test_triangle_180(self):
            self.create_canvas()
            print(self.kwargs)
            self.canvas.draw_triangle(xy=(50,50), direction=180, **self.kwargs)
            self.save_canvas('triangle_180')

        def test_triangle_270(self):
            self.create_canvas()
            print(self.kwargs)
            self.canvas.draw_triangle(xy=(50,50), direction=270, **self.kwargs)
            self.save_canvas('triangle_270')

# anchors

class TestAnchorDefault(BaseTestCases.DrawShapes):
    output_prefix = 'anchor_default'

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '25%w'}
        self.kwargs.update(extra)

class TestAnchorCenter(BaseTestCases.DrawShapes):
    output_prefix = 'anchor_center'

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '25%w',
                'anchor':'center'}
        self.kwargs.update(extra)

class TestAnchorNW(BaseTestCases.DrawShapes):
    output_prefix = 'anchor_nw'

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '25%w',
                'anchor':'nw'}
        self.kwargs.update(extra)

class TestAnchorNE(BaseTestCases.DrawShapes):
    output_prefix = 'anchor_ne'

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '25%w',
                'anchor':'ne'}
        self.kwargs.update(extra)

class TestAnchorSE(BaseTestCases.DrawShapes):
    output_prefix = 'anchor_se'

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '25%w',
                'anchor':'se'}
        self.kwargs.update(extra)

class TestAnchorSW(BaseTestCases.DrawShapes):
    output_prefix = 'anchor_sw'

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '25%w',
                'anchor':'sw'}
        self.kwargs.update(extra)


if __name__ == '__main__':
    unittest.main()

