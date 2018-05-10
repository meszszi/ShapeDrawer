from PIL import Image, ImageDraw
import math
import json
from abc import ABC, abstractmethod
from re import findall
from itertools import chain
import argparse
import sys

class ImageManager():
    
    '''Represents an area on which all shapes from an input file are drawn'''
    
    def __init__(self, width, height, bg_color, fg_color=None):
            
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.fg_color = fg_color
        
        self._image = Image.new(size=(width, height), color=bg_color, mode='RGB')
        self._surface = ImageDraw.Draw(self._image)
        
    def draw(self, shape):
        
        shape.draw(self._surface)
            
    def display(self):
        
        self._image.show()
        
    def save(self, file_name):
        
        self._image.save(file_name)
               

class AbstractShape(ABC):
    
    '''Represents a single shape that may be drawn on canvas'''
    
    def __init__(self, color):
        self.color = color
        
    @abstractmethod
    def draw(self, surface):
        pass
    
    
class Point(AbstractShape):
    
    '''Point shape'''
    
    def __init__(self, x, y, color):
        
        super().__init__(color)
        self.x_coord = x
        self.y_coord = y

    def draw(self, surface):
        
        surface.point((self.x_coord, self.y_coord), fill=self.color)
        
        
class Circle(AbstractShape):
    
    '''Circle shape'''
    
    def __init__(self, x, y, radius, color):
        
        super().__init__(color)
        self.x_coord = x
        self.y_coord = y
        self.radius = radius

    def draw(self, surface):
        
        surface.ellipse((self.x_coord - self.radius,
                         self.y_coord - self.radius,
                         self.x_coord + self.radius,
                         self.y_coord + self.radius),
                        fill=self.color)


class Rectangle(AbstractShape):
    
    '''Rectangle shape'''
    
    def __init__(self, x, y, height, width, color):
        
        super().__init__(color)
        self.x_coord = x
        self.y_coord = y
        self.height = height
        self.width = width

    def draw(self, surface):
        
        surface.rectangle((self.x_coord - (self.width // 2), 
                           self.y_coord - (self.height // 2), 
                           self.x_coord + (self.width // 2), 
                           self.y_coord + (self.height // 2)),
                          fill=self.color)
        
        
class Square(Rectangle):
    
    '''Square shape'''
    
    def __init__(self, x, y, size, color):
        
        super().__init__(x, y, size, size, color)
        
        
class Polygon(AbstractShape):
    
    '''Polygon shape'''
    
    def __init__(self, points, color):
        
        super().__init__(color)
        self.points = points
        
    def draw(self, surface):
        
        surface.polygon(list(chain(*self.points)), fill=self.color)
    
    
class FileParser():

    '''Used for parsing all the data from the input file'''
    
    _FIGURE_CONSTRUCTORS = {
        'point': Point,
        'circle': Circle,
        'square': Square,
        'rectangle': Rectangle,
        'polygon': Polygon
    }
    
    def __init__(self, json_file):
        
        with open(json_file, 'r') as file:
            
            raw_dict = json.load(file)
            
            self.color_palette = raw_dict.get('Palette', {})
            for name, value in self.color_palette.items():
                self.color_palette[name] = FileParser._parse_color(value)
            
            self.screen_parameters = raw_dict['Screen']
            
            bg_color = self.screen_parameters['bg_color']
            self.screen_parameters['bg_color'] = self.color_palette.get(
                bg_color, FileParser._parse_color(bg_color))
            
            fg_color = self.screen_parameters['fg_color']
            self.screen_parameters['fg_color'] = self.color_palette.get(
                fg_color, FileParser._parse_color(fg_color))
            
            raw_figures = raw_dict['Figures']
            self.figures = [self._parse_figure(figure_dict) for figure_dict in raw_figures]

        
    def _parse_color(string_color):
        
        if string_color.startswith('#'):
            return string_color
        
        if string_color.startswith('('):
            (r, g, b) = findall('[0-9]+', string_color)
            return int(r), int(g), int(b)

        return None
    

    def _parse_figure(self, figure_dict):
        
        figure_type = figure_dict.pop('type')
        raw_color = figure_dict.get('color', self.screen_parameters['fg_color'])
        figure_dict['color'] = self.color_palette.get(raw_color, FileParser._parse_color(raw_color))
        constructor = FileParser._FIGURE_CONSTRUCTORS[figure_type]
        
        return constructor(**figure_dict)
    
    
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='json file containing image description')
    parser.add_argument('-o', '--output', help='save image to file')
    args = parser.parse_args()
    
    fp = FileParser(args.input)
    im = ImageManager(**fp.screen_parameters)
    for figure in fp.figures:
        im.draw(figure)
    
    im.display()
    
    if args.output:
        im.save(args.output)
        
        
if __name__ == '__main__':
    main()

