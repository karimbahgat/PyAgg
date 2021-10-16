
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

        def test_triangle(self):
            self.create_canvas()
            print(self.kwargs)
            self.canvas.draw_triangle(xy=(50,50), **self.kwargs)
            self.save_canvas('triangle')

# anchors

class TestAnchorDefault(BaseTestCases.DrawShapes):
    output_prefix = 'anchor_default'

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '5pt'}
        self.kwargs.update(extra)

class TestAnchorCenter(BaseTestCases.DrawShapes):
    output_prefix = 'anchor_center'

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '5pt',
                'anchor':'center'}
        self.kwargs.update(extra)

class TestAnchorNW(BaseTestCases.DrawShapes):
    output_prefix = 'anchor_nw'

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '5pt',
                'anchor':'nw'}
        self.kwargs.update(extra)

class TestAnchorNE(BaseTestCases.DrawShapes):
    output_prefix = 'anchor_ne'

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '5pt',
                'anchor':'ne'}
        self.kwargs.update(extra)

class TestAnchorSE(BaseTestCases.DrawShapes):
    output_prefix = 'anchor_se'

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '5pt',
                'anchor':'se'}
        self.kwargs.update(extra)

class TestAnchorSW(BaseTestCases.DrawShapes):
    output_prefix = 'anchor_sw'

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawShapes, self).__init__(*args, **kwargs)
        self.kwargs = self.kwargs.copy()
        extra = {'fillsize': '5pt',
                'anchor':'sw'}
        self.kwargs.update(extra)


if __name__ == '__main__':
    unittest.main()

