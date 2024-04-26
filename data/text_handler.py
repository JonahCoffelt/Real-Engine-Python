import pygame as pg
import pygame.freetype as freetype

class TextHandler():
    def __init__(self):
        self.fonts = {}
        freetype.init()
        self.load_font("serif")
        self.load_font("default")
        self.load_font("calibri")
        self.load_font("arial")

    def load_font(self, font):
        self.fonts[font] = freetype.SysFont(font, 24)
    
    def render_text(self, win, rect, text, font="default", size=16, color=(255, 255, 255), bg_color=(0, 0, 0, 0), center_width=False, center_height=False, bold=False, underline=False, italic=False):
        '''
        Renders any font which has been loaded to the class instance.
        Args:
            win::pygame.surface
                This is the drawing location for the text
            rect::(int, int, int, int)
                The rect of the surface to draw onto
            text::str
                Text to be rendered
            font::str (="Calibri")
                Any loaded or standard font can be specified
            size::int (=1)
                Sets the size of the text. Value can be either 0, 1, or 2, which is small, medium, or large.
            color::(int, int, int) =(255, 255, 255)
                The RGB value of the text
            bold::bool (=False)
                Specifies if the text should be rendered in bolded font
            underline::bool (=False)
                Specifies if the text should be underlined in bolded font
            italic::bool (=False)
                Specifies if the text should be rendered in italicized font
            center_width::bool (=False)
                If True, the text will be horizontaly centered on the X position provided by pos. Otherwise, the leftmost side will be on the X coordinate
        '''
        
        font = self.fonts[font]
        font.size = size
        font.strong = bold
        font.underline = underline
        font.oblique = italic

        surf = pg.Surface([*rect[2:]]).convert_alpha()
        surf.fill(bg_color)
        space = font.get_rect('L')

        words = text.split(' ')
        lines = []

        line = ''
        line_width = 0

        for word in words:
            line_width += font.get_rect(word).width + space[2]
            if line_width < rect[2]: line += word + ' '
            else:
                lines.append(line)
                line = word + ' '
                line_width = font.get_rect(word).width
        lines.append(line)

        for i, line in enumerate(lines):
            line = line[:-1]
            line_rect = font.get_rect(line)
            x = 0
            y = i * (space[3] * 1.5)
            if center_width: x += rect[2]/2 - line_rect[2]/2
            else: x += .5 * (space[2] * 1.5)
            if center_height: y += rect[3]/2 - (space[3] * 1.5 * len(lines))/2 + space[3] * .25
            else: y += .5 * (space[3] * 1.5)
            font.render_to(surf, (x, y), line, fgcolor=color)

        win.blit(surf, [*rect[:2]])