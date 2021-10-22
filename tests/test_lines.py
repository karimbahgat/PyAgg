
import unittest

import pyagg

# base class

class BaseTestCases:

    class DrawLines(unittest.TestCase):
        width = 200
        height = 200
        kwargs = {'fillsize':'2pt', 'outlinewidth':'0.1pt'}
        output_prefix = 'lines'

        def create_canvas(self):
            self.canvas = pyagg.Canvas(self.width, self.height, background='gray')
            self.canvas.percent_space()
            self.canvas.draw_grid(25, 25)

        def save_canvas(self, name):
            print('save',self.output_prefix,name)
            self.canvas.save('outputs/{}_{}.png'.format(self.output_prefix, name))

        def test_straight_2points(self):
            self.create_canvas()
            print(self.kwargs)
            line = [(10,50),(90,50)]
            self.canvas.draw_line(line, **self.kwargs)
            self.save_canvas('straight_2points')

        def test_straight_3points(self):
            self.create_canvas()
            print(self.kwargs)
            line = [(10,50),(50,50),(90,50)]
            self.canvas.draw_line(line, **self.kwargs)
            self.save_canvas('straight_3points')

        def test_straight_duplicates(self):
            self.create_canvas()
            print(self.kwargs)
            line = [(10,50),(50,50),(90,50)]
            self.canvas.draw_line(line, **self.kwargs)
            self.save_canvas('straight_duplicates')

        def test_bend_3points(self):
            self.create_canvas()
            print(self.kwargs)
            line = [(10,50),(50,50),(90,90)]
            self.canvas.draw_line(line, **self.kwargs)
            self.save_canvas('bend_3points')

        def test_bend_duplicates(self):
            self.create_canvas()
            print(self.kwargs)
            line = [(10,50),(50,50),(50,50),(90,90)]
            self.canvas.draw_line(line, **self.kwargs)
            self.save_canvas('bend_duplicates')

        def test_random(self):
            self.create_canvas()
            print(self.kwargs)
            from random import randint, seed
            seed(16)
            line = [(randint(0,100),randint(0,100)) for _ in range(50)]
            self.canvas.draw_line(line, **self.kwargs)
            self.save_canvas('random')


# basic line options

class TestLineDefault(BaseTestCases.DrawLines):

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawLines, self).__init__(*args, **kwargs)
        self.output_prefix += '_default'
        self.kwargs = self.kwargs.copy()
        extra = {}
        self.kwargs.update(extra)

class TestLineFillOutline(BaseTestCases.DrawLines):

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawLines, self).__init__(*args, **kwargs)
        self.output_prefix += '_fill_outline'
        self.kwargs = self.kwargs.copy()
        extra = {'fillcolor':'yellow', 'outlinecolor':'black'}
        self.kwargs.update(extra)

class TestLineFillOutlineArrow(BaseTestCases.DrawLines):

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawLines, self).__init__(*args, **kwargs)
        self.output_prefix += '_fill_outline'
        self.kwargs = self.kwargs.copy()
        extra = {'end':'arrow', 'fillcolor':'yellow', 'outlinecolor':'black'}
        self.kwargs.update(extra)

class TestLineFillOnly(BaseTestCases.DrawLines):

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawLines, self).__init__(*args, **kwargs)
        self.output_prefix += '_fill_only'
        self.kwargs = self.kwargs.copy()
        extra = {'fillcolor':'yellow', 'outlinecolor':None}
        self.kwargs.update(extra)

class TestLineOutlineOnly(BaseTestCases.DrawLines):

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawLines, self).__init__(*args, **kwargs)
        self.output_prefix += '_outline_only'
        self.kwargs = self.kwargs.copy()
        extra = {'fillcolor':None, 'outlinecolor':'black'}
        self.kwargs.update(extra)

# smooth line options

class TestSmoothLineFillOutline(BaseTestCases.DrawLines):

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawLines, self).__init__(*args, **kwargs)
        self.output_prefix += '_smooth_fill_outline'
        self.kwargs = self.kwargs.copy()
        extra = {'smooth':True, 'fillcolor':'yellow', 'outlinecolor':'black'}
        self.kwargs.update(extra)

class TestSmoothLineFillOutlineArrow(BaseTestCases.DrawLines):

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawLines, self).__init__(*args, **kwargs)
        self.output_prefix += '_smooth_fill_outline_arrow'
        self.kwargs = self.kwargs.copy()
        extra = {'smooth':True, 'end':'arrow', 'fillcolor':'yellow', 'outlinecolor':'black'}
        self.kwargs.update(extra)

class TestSmoothLineFillOnly(BaseTestCases.DrawLines):

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawLines, self).__init__(*args, **kwargs)
        self.output_prefix += '_smooth_fill_only'
        self.kwargs = self.kwargs.copy()
        extra = {'smooth':True, 'fillcolor':'yellow', 'outlinecolor':None}
        self.kwargs.update(extra)

class TestSmoothLineOutlineOnly(BaseTestCases.DrawLines):

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawLines, self).__init__(*args, **kwargs)
        self.output_prefix += '_smooth_outline_only'
        self.kwargs = self.kwargs.copy()
        extra = {'smooth':True, 'fillcolor':None, 'outlinecolor':'black'}
        self.kwargs.update(extra)

# smooth volume line options

def volume(prog, x, y): 
    perc = 2 + prog*10
    return '{}%w'.format(perc)

class TestSmoothVolumeLineFillOutline(BaseTestCases.DrawLines):

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawLines, self).__init__(*args, **kwargs)
        self.output_prefix += '_smoothvolume_fill_outline'
        self.kwargs = self.kwargs.copy()
        extra = {'smooth':True, 'volume':volume, 'fillcolor':'yellow', 'outlinecolor':'black'}
        self.kwargs.update(extra)

class TestSmoothVolumeLineFillOutlineArrow(BaseTestCases.DrawLines):

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawLines, self).__init__(*args, **kwargs)
        self.output_prefix += '_smoothvolume_fill_outline_arrow'
        self.kwargs = self.kwargs.copy()
        extra = {'smooth':True, 'volume':volume, 'end':'arrow', 'fillcolor':'yellow', 'outlinecolor':'black'}
        self.kwargs.update(extra)

class TestSmoothVolumeLineFillOnly(BaseTestCases.DrawLines):

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawLines, self).__init__(*args, **kwargs)
        self.output_prefix += '_smoothvolume_fill_only'
        self.kwargs = self.kwargs.copy()
        extra = {'smooth':True, 'volume':volume, 'fillcolor':'yellow', 'outlinecolor':None}
        self.kwargs.update(extra)

class TestSmoothVolumeLineOutlineOnly(BaseTestCases.DrawLines):

    def __init__(self, *args, **kwargs):
        super(BaseTestCases.DrawLines, self).__init__(*args, **kwargs)
        self.output_prefix += '_smoothvolume_outline_only'
        self.kwargs = self.kwargs.copy()
        extra = {'smooth':True, 'volume':volume, 'fillcolor':None, 'outlinecolor':'black'}
        self.kwargs.update(extra)


if __name__ == '__main__':
    unittest.main()

