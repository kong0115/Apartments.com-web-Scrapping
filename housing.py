# Web Scrapping for Apartments.com


"""
Created on Thu May 31 11:34:20 2018
@author: dhuang
"""

from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import re
import pandas as pd
import numpy as np
	
def initialSetup(websiteURL, x):
	regex = re.search(".*/\?",websiteURL)
	index = regex.span()
	my_url = websiteURL[:index[1]-1] + str(x) + "/" + websiteURL[index[1]-1:]
	uClient = uReq(my_url)
	page_html = uClient.read()
	uClient.close()
	page_soup = soup(page_html, 'html.parser')

def getApartmentList(minRange,maxRange):
	for x in range(minRange,maxRange):
		initialSetup(websiteURL,x)
		containers = page_soup.findAll('article', {'class': 'placard'})
		print('\nPage ', x)
		#sleeper
		count = 1
		for container in containers:
			try:
				#link = container.find('a', {'class':'placardTitle js-placardTitle '}).get('data-url')
				link = container.get('data-url')
				print(count, ' ',link)
				link_list.append(link)
				count +=1
			except:
				print('     somthing here')
				error_list.append(link)

def main(websiteURL):	
	link_list = []
	error_list = []
	getApartmentList(websiteURL,1,2)

if __name__ == '__main__':
	main(websiteURL)
