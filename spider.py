# coding:utf-8

from urllib import parse, request
import re
import json
import html

class Spider():
	def __init__(self, **kwargs):
		options = {
			'url': 'http://store.united-arrows.co.jp/shop/uasons/goods.html?gid=9700472',
			'user_agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
		}
		options.update(kwargs)
		self.user_agent = options['user_agent']
		self.url = options['url']

	def get_page(self):
		headers = { 'User-Agent': self.user_agent }
		url = request.Request(self.url, None, headers)  
		response = request.urlopen(url)  
		html = response.read() 
		return html.decode('shift_jisx0213')


class Parser():
	def __init__(self, page, regex = {}):
		self.page = page
		self.regex = {
			'product_name': r'brand">.*?item">(.*?)<\/p>',
			'product_id': r'品　番<\/td>.*?>(.*?)<\/td>',
			'size_table': r'アイテムサイズ<\/p>(.*?)<div',
			'size_categories': r'dtl">(.*?)<\/th>',
			'sizes': r'size">(.*?)<\/td>',
			'sizes_data': r'dtl">(.*?)<\/td>'
		}
		self.regex = self.__extend_regex(regex)
		self.__size_table = self.__parse_table()

	def get_json(self, *args):
		all_data = {}
		for arg in args:
			all_data.update(arg)
		return json.loads(str(all_data).replace("'",'"'))

	def get_product_name(self):
		result = self.__parse_content(self.regex['product_name'], flag = re.DOTALL)
		return { 'name': html.unescape(self.__safe_return(result)) }

	def get_product_id(self):
		result = self.__parse_content(self.regex['product_id'], flag = re.DOTALL)
		return { 'id': self.__safe_return(result) }

	def get_sizes(self):
		sizes = { 'sizes': {} }
		size_categories = self.__parse_size_categories()
		sizes_data = self.__parse_sizes_data()
		for size in self.__parse_sizes():
			sizes['sizes'].update({ size: { size_categories[i]: float(sizes_data.pop(0)) for i in range(len(size_categories)) } })
		return sizes

	def __parse_content(self, pattern, **kwargs):
		options = {
			'page': self.page,
			'flag': re.IGNORECASE
		}
		options.update(kwargs)
		return re.findall(pattern, options['page'], options['flag'])

	def __parse_table(self):
		return self.__parse_content(self.regex['size_table'], flag = re.DOTALL)[0]

	def __parse_size_categories(self):
		return self.__parse_content(self.regex['size_categories'], page = self.__size_table)

	def __parse_sizes(self):
		return self.__parse_content(self.regex['sizes'], page = self.__size_table)

	def __parse_sizes_data(self):
		return self.__parse_content(self.regex['sizes_data'], page = self.__size_table)

	def __extend_regex(self, regex_extensions):
		if (type(regex_extensions) is not dict):
			raise Exception('You should pass in a dictionary as regex extensions')
		else:
			return dict(self.regex, **regex_extensions)

	def __safe_return(self, lst):
		return lst[0] if (len(lst) > 0) else ''


if __name__ == "__main__":
	spider = Spider()
	parser = Parser(spider.get_page())

	output = parser.get_json(parser.get_product_id(), parser.get_product_name(), parser.get_sizes())
	print(json.dumps(output, indent = 2, ensure_ascii = False))
