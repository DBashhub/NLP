import pandas as pd
import re
import requests

from bs4 import BeautifulSoup
from time import sleep
from .requester import Requester

class Crawler:
	"""
	"""
	def __init__(self, url, sarcasm, as_archived=False):
		self.__url = url
		self.__sarcasm = sarcasm
		self.__as_archived = as_archived

		self.__data = list()
		self.__requests = list()


	def set_requests(self, html_class, regex, remove, element="a", shorter=0):

		find_pages = re.compile(regex)
		urls = list()

		html = Requester.get_one_request(self.__url + ("1", "")[self.__as_archived], force=True)
		bs = BeautifulSoup(html.text, "html.parser")
		element = str(bs.find_all(element, class_=html_class))

		if self.__as_archived == True:
			for page in find_pages.finditer(element):
				urls.append(str(self.__url[:-shorter]) + element[page.start()+remove[0]:page.end()-remove[1]])
		else:
			for page in find_pages.finditer(element):
				pages = int(element[page.start()+remove[0]:page.end()-remove[1]]) + 1
			for page in range(1, pages):
				urls.append(self.__url + str(page))
		self.__requests = Requester(urls, num_threads=24).get_requests()


	def get_raw_data(self, html_class, regex, element="div"):

		find_element = re.compile(regex)
		raw_data = list()

		for request in self.__requests:
			bs = BeautifulSoup(request.text, "html.parser")
			raw = str(bs.find_all(element, class_=html_class))
			for text in find_element.finditer(raw):
				raw_data.append(raw[text.start():text.end()])

		print("[+] Total of {0:04d} raw data collected".format(len(raw_data)))
		return raw_data

	def set_data(self, raw_args, regex, remove, html_options, url_prefix=0):

		find_link = re.compile(regex[0])
		find_title = re.compile(regex[1])
		find_text = re.compile(r"<.*?>")
		# find_text = re.compile(r"<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
		urls = list()

		for raw in self.get_raw_data(**raw_args):
			data = [None,None,None,None]
			data[0] = self.__sarcasm
			for tmp in find_link.finditer(raw):
				data[1] = self.__url[:url_prefix] + raw[tmp.start()+remove[0][0]:tmp.end()-remove[0][1]]
			urls.append(data[1])
			for tmp in find_title.finditer(raw):
				data[2] = raw[tmp.start()+remove[1][0]:tmp.end()-remove[1][1]]
			if data[2] == [""]:
				continue
			data[3] = ""
			self.__data.append(data)


		print("[+] Dataframe completed")

	def get_data(self):
		return self.__data
