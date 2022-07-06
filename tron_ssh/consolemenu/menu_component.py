import textwrap

from consolemenu.format.menu_bar import create_bar
from consolemenu.format.menu_color import MenuColor, RED, GREEN, DEFAULT
from consolemenu.format import MenuStyle
from os import popen, path
from urllib.request import urlopen
from datetime import datetime

def create_style_colored_info(styles, text, color_style, color_text):
	content = MenuColor.set_color_section(styles[0], color_style)
	content += MenuColor.set_color_section(text, color_text)
	content += MenuColor.set_color_section(styles[1], color_style)
	return content

class MenuBanner:
	def __init__(self):
		self.hostname = self.get_hostname()
		self.ram = self.get_ram()
		self.author = 'c0n3ct4r'
		self.script_name = 'TRON SSH'
		self.styles = ('[',']')
		self.color = MenuColor()
		self.content = ''

	def get_hostname(self):
		if path.exists('/etc/ip'):
			return open('/etc/ip').read().strip()
		import socket
		return socket.gethostbyname(socket.gethostname())

	def get_ram(self):
		return list(map(int, popen('free -tm').readlines()[-1].split()[1:]))

	def set_content_date(self):
		date = datetime.now()
		self.content += '=' * 50 + '\n'
		self.content += '   %02d/%02d/%02d %33s\n' % (
			date.day, date.month, date.year,
			date.strftime('%H:%M:%S')
		)
		self.content += '-' * 50 + '\n'

	def set_content_info(self):
		self.content += '   %s     %s     %s\n' % (
			create_style_colored_info(self.styles, self.script_name, MenuColor.GREEN, MenuColor.RED),
			create_style_colored_info(self.styles, self.hostname, MenuColor.GREEN, MenuColor.RED),
			create_style_colored_info(self.styles, self.author, MenuColor.GREEN, MenuColor.RED)
		)
		self.content += '-' * 50
	def builder(self):
		self.set_content_date()
		self.set_content_info()
		return self.content

class Dimension(object):
	"""
	The Dimension class encapsulates the height and width of a component.

	Args:
		width (int): the width of the Dimension, in columns.
		height (int): the height of the Dimension, in rows.
		dimension (Dimension, optional): an existing Dimension from which to duplicate the height and width.
	"""

	def __init__(self, width=0, height=0, dimension=None):
		self.width = width
		self.height = height
		if dimension is not None:
			self.width = dimension.width
			self.height = dimension.height


class MenuComponent(object):
	"""
	Base class for a menu component.

	Args:
		menu_style (:obj:`MenuStyle`): the style for this component.
		max_dimension (:obj:`Dimension`): the maximum Dimension (width x height) for the menu. Defaults to width=80
			and height=40 if not specified.

	Raises:
		TypeError: if menu_style is not a :obj:`MenuStyle`.
	"""

	def __init__(self, menu_style, max_dimension=None):
		if not isinstance(menu_style, MenuStyle):
			raise TypeError('menu_style must be of type MenuStyle')
		if max_dimension is None:
			max_dimension = Dimension(width=80, height=40)
		self.__max_dimension = max_dimension
		self.__style = menu_style

	@property
	def max_dimension(self):
		"""
		:obj:`Dimension`: The maximum dimension for the menu.
		"""
		return self.__max_dimension

	@property
	def style(self):
		"""
		:obj:`consolemenu.format.MenuStyle`: The style for this component.
		"""
		return self.__style

	@property
	def margins(self):
		"""
		:obj:`consolemenu.format.MenuMargins`: The margins for this component.
		"""
		return self.__style.margins

	@property
	def padding(self):
		"""
		:obj:`consolemenu.format.MenuPadding`: The padding for this component.
		"""
		return self.__style.padding

	@property
	def border_style(self):
		"""
		:obj:`consolemenu.format.MenuBorderStyle`: The border style for this component.
		"""
		return self.__style.border_style

	def calculate_border_width(self):
		"""
		Calculate the width of the menu border. This will be the width of the maximum allowable
		dimensions (usually the screen size), minus the left and right margins and the newline character.
		For example, given a maximum width of 80 characters, with left and right margins both
		set to 1, the border width would be 77 (80 - 1 - 1 - 1 = 77).

		Returns:
			int: the menu border width in columns.
		"""
		return self.max_dimension.width - self.margins.left - self.margins.right - 1  # 1=newline

	def calculate_content_width(self):
		"""
		Calculate the width of inner content of the border.  This will be the width of the menu borders,
		minus the left and right padding, and minus the two vertical border characters.
		For example, given a border width of 77, with left and right margins each set to 2, the content
		width would be 71 (77 - 2 - 2 - 2 = 71).

		Returns:
			int: the inner content width in columns.
		"""
		return self.calculate_border_width() - self.padding.left - self.padding.right - 2

	def generate(self):
		"""
		Generate this component.

		Yields:
			str: The next string of characters for drawing this component.
		"""
		raise NotImplemented()

	def inner_horizontals(self):
		"""
		The string of inner horizontal border characters of the required length for this component (not including
		the menu margins or verticals).

		Returns:
			str: The inner horizontal characters.
		"""
		return u"{0}".format(self.border_style.inner_horizontal * (self.calculate_border_width() - 2))

	def inner_horizontal_border(self):
		"""
		The complete inner horizontal border section, including the left and right border verticals.

		Returns:
			str: The complete inner horizontal border.
		"""
		return u"{lm}{lv}{hz}{rv}".format(lm=' ' * self.margins.left,
										  lv=self.border_style.outer_vertical_inner_right,
										  rv=self.border_style.outer_vertical_inner_left,
										  hz=self.inner_horizontals())

	def outer_horizontals(self):
		"""
		The string of outer horizontal border characters of the required length for this component (not including
		the menu margins or verticals).

		Returns:
			str: The outer horizontal characters.
		"""
		return u"{0}".format(self.border_style.outer_horizontal * (self.calculate_border_width() - 2))

	def outer_horizontal_border_bottom(self):
		"""
		The complete outer bottom horizontal border section, including left and right margins.

		Returns:
			str: The bottom menu border.
		"""
		return u"{lm}{lv}{hz}{rv}".format(lm=' ' * self.margins.left,
										  lv=self.border_style.bottom_left_corner,
										  rv=self.border_style.bottom_right_corner,
										  hz=self.outer_horizontals())

	def outer_horizontal_border_top(self):
		"""
		The complete outer top horizontal border section, including left and right margins.

		Returns:
			str: The top menu border.
		"""
		return u"{lm}{lv}{hz}{rv}".format(lm=' ' * self.margins.left,
										  lv=self.border_style.top_left_corner,
										  rv=self.border_style.top_right_corner,
										  hz=self.outer_horizontals())

	def row(self, content='', align='left'):
		"""
		A row of the menu, which comprises the left and right verticals plus the given content.

		Returns:
			str: A row of this menu component with the specified content.
		"""
		return u"{lm}{vert}{cont}{vert}".format(lm=' ' * self.margins.left,
												vert=self.border_style.outer_vertical,
												cont=self._format_content(content, align))

	@staticmethod
	def _alignment_char(align):
		if str(align).strip() == 'center':
			return '^'
		elif str(align).strip() == 'right':
			return '>'
		else:
			return '<'

	def _format_content(self, content='', align='left'):
		return '{lp}{text:{al}{width}}{rp}'.format(lp=' ' * self.padding.left,
												   rp=' ' * self.padding.right,
												   text=content, al=self._alignment_char(align),
												   width=(self.calculate_border_width() - self.padding.left -
														  self.padding.right - 2))


class MenuHeader(MenuComponent):
	"""
	The menu header section.
	The menu header contains the top margin, menu top, title/subtitle verticals, bottom padding verticals,
	and optionally a bottom border to separate the header from the next section.
	"""

	def __init__(self, menu_style, max_dimension=None, title=None, title_align='left',
				 subtitle=None, subtitle_align='left', show_bottom_border=False):
		super(MenuHeader, self).__init__(menu_style, max_dimension)
		self.title = title
		self.title_align = title_align
		self.subtitle = subtitle
		self.subtitle_align = subtitle_align
		self.show_bottom_border = show_bottom_border

	def generate(self):
		yield MenuBanner().builder()
		if self.title is not None and self.title != '':
			yield create_bar(self.title)
		


class MenuTextSection(MenuComponent):
	"""
	The menu text block section.
	A text block section can be used for displaying text to the user above or below the main items section.
	"""

	def __init__(self, menu_style, max_dimension=None, text=None, text_align='left',
				 show_top_border=False, show_bottom_border=False):
		super(MenuTextSection, self).__init__(menu_style, max_dimension)
		self.text = text
		self.text_align = text_align
		self.show_top_border = show_top_border
		self.show_bottom_border = show_bottom_border

	def generate(self):
		if self.show_top_border:
			yield self.inner_horizontal_border()
		for x in range(0, self.padding.top):
			yield self.row()
		if self.text is not None and self.text != '':
			for line in textwrap.wrap(self.text, width=self.calculate_content_width()):
				yield self.row(content=line, align=self.text_align)
		for x in range(0, self.padding.bottom):
			yield self.row()
		if self.show_bottom_border:
			yield self.inner_horizontal_border()


class MenuItemsSection(MenuComponent):
	"""
	The menu section for displaying the menu items.
	"""

	def __init__(self, menu_style, max_dimension=None, items=None, items_align='left'):
		super(MenuItemsSection, self).__init__(menu_style, max_dimension)
		if items is not None:
			self.__items = items
		else:
			self.__items = list()
		self.items_align = items_align
		self.__top_border_dict = dict()
		self.__bottom_border_dict = dict()
		self.color_item = MenuColor()

	@property
	def items(self):
		return self.__items

	@items.setter
	def items(self, items):
		self.__items = items

	@property
	def items_with_bottom_border(self):
		"""
		Return a list of the names (the item text property) of all items that should show a bottom border.
		:return: a list of item names that should show a bottom border.
		"""
		return self.__bottom_border_dict.keys()

	@property
	def items_with_top_border(self):
		"""
		Return a list of the names (the item text property) of all items that should show a top border.
		:return: a list of item names that should show a top border.
		"""
		return self.__top_border_dict.keys()

	def show_item_bottom_border(self, item_text, flag):
		"""
		Sets a flag that will show a bottom border for an item with the specified text.
		:param item_text: the text property of the item
		:param flag: boolean specifying if the border should be shown.
		"""
		if flag:
			self.__bottom_border_dict[item_text] = True
		else:
			self.__bottom_border_dict.pop(item_text, None)

	def show_item_top_border(self, item_text, flag):
		"""
		Sets a flag that will show a top border for an item with the specified text.
		:param item_text: the text property of the item
		:param flag: boolean specifying if the border should be shown.
		"""
		if flag:
			self.__top_border_dict[item_text] = True
		else:
			self.__top_border_dict.pop(item_text, None)
	
	def set_color_text(self, text):
		return RED + str(text) + DEFAULT
	
	def set_color_option(self, option):
		return GREEN + '%02d' % option +  DEFAULT
	
	def get_sizes_items(self):
		width = max(len(item.text) for item in self.items if item)
		size_items = len(self.items) // 2
		return width, size_items

	def generate(self):
		if len(self.items) < 10:
			for index, item in enumerate(self.items, 1):
				yield '[%s] - %s' % (self.set_color_option(index), self.set_color_text(item.text))
		else:
			if len(self.items) % 2 != 0: self.items.append('')
			width, size_items = self.get_sizes_items()
			idx1, idx2 = 1, size_items + 1
			for item1, item2 in zip(self.items[:size_items], self.items[size_items:]):
				if item2:
					yield '[%s] - %s[%s] - %s' % (
						self.set_color_option(idx1), self.set_color_text(item1.text.ljust(width)),
						self.set_color_option(idx2), self.set_color_text(item2.text)
					)
				else:
					yield '[%s] - %s' % (
						self.set_color_option(idx1), self.set_color_text(item1.text)
					)
				idx1 += 1
				idx2 += 1
		if not self.items[-1]:
			del self.items[-1]

class MenuFooter(MenuComponent):
	"""
	The menu footer section.
	The menu footer contains the menu bottom, bottom padding verticals, and bottom margin.
	"""

	def generate(self):
		for x in range(0, self.padding.top):
			yield self.row()
		yield self.outer_horizontal_border_bottom()
		for x in range(0, self.margins.bottom):
			yield ''


class MenuPrompt(MenuComponent):
	"""
	A string representing the menu prompt for user input.
	"""

	def __init__(self, menu_style, max_dimension=None, prompt_string='Escolha uma opcao: '):
		super(MenuPrompt, self).__init__(menu_style, max_dimension)
		self.__prompt = prompt_string

	@property
	def prompt(self):
		return self.__prompt

	@prompt.setter
	def prompt(self, prompt):
		self.__prompt = prompt

	def generate(self):
		yield self.__prompt
