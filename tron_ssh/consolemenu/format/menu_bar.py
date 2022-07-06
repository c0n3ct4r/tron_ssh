from consolemenu.format.menu_color import MenuColor

class MenuBar:
    def __init__(self, title, size=50, style='=', color_title=MenuColor.GREEN):
        self.title = title
        self.size = size
        self.style = style
        self.color_title = color_title
        self.color = MenuColor()
    
    def set_color_title(self, color):
        self.color_title = color

    def set_size(self, size):
        self.size = size

    def set_style(self, style):
        self.style = style

    def create_style_bar(self):
        size_title = len(self.title) + 2
        size_bar = (self.size - size_title) // 2
        bars = [self.style * size_bar, self.style * size_bar]
        size_bars = len(''.join(bars)) + len(self.title) + 2
        if size_bars % 2 != 0:
            bars[1] += self.style
        return bars

    def create(self):
        bars = self.create_style_bar()
        return '%s[%s]%s' % (
            self.color.set_color_section(bars[0], MenuColor.WHITE),
            self.color.set_color_section(self.title, self.color_title),
            self.color.set_color_section(bars[1], MenuColor.WHITE)
        )

def create_bar(title, style='=', color_tile=MenuColor.GREEN):
    bar = MenuBar(title)
    return bar.create()
    