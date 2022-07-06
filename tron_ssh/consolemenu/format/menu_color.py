DEFAULT = '\033[00m'
RED = '\033[1;31m'
GREEN = '\033[1;32m'
YELLOW = '\033[1;33m'
WHITE = '\033[1;37m'
BGGREY = '\033[1;100m'

class Colors:
    DEFAULT = '\033[00m'
    RED = '\033[1;31m'
    GREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    WHITE = '\033[1;37m'

class MenuColor(Colors):
    def __init__(self):
        self.items = None
        
    def set_items(self, items):
        self.items = items

    def set_color_item(self, color):
        items = list()
        for item in self.items:
            if item:
                item.text = color + item.text + self.DEFAULT
                items.append(item)
        self.items = items

    @staticmethod
    def set_color_section(sec, color):
        return color + sec + Colors.DEFAULT