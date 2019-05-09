from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import re
import pandas as pd
import numpy as np
import sys
import requests
import time
import random

def initialSetup(websiteURL, x):
	regex = re.search(".*/\?",websiteURL)
	index = regex.span()
	my_url = websiteURL[:index[1]-1] + str(x) + "/" + websiteURL[index[1]-1:]
	#uClient = uReq(my_url)
	#page_html = uClient.read()
	#uClient.close()
	headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
    }
	page_html = requests.get(my_url,headers=headers)
	page_soup = soup(page_html.text, 'html.parser')
	return page_soup

def getApartmentPageNum(websiteURL):
	page_soup = initialSetup(websiteURL, 1)
	page = page_soup.find('div', {'class': 'paging'})
	temp = page.findAll('a')
	numPages = temp[len(temp) - 2].get('data-page')
	return numPages

def getApartmentList(websiteURL,page):
	#for x in range(minRange,maxRange):
		page_soup = initialSetup(websiteURL,page)
		# page = page_soup.find('div', {'class': 'paging'})
		# temp = page.findAll('a')
		# numPages = temp[len(temp) - 2].get('data-page')
		# print(numPages)

		containers = page_soup.findAll('article', {'class': 'placard'})
		print('\nPage ', page)
		count = 1
		apartment_list = []
		for container in containers:
			#link = container.find('a', {'class':'placardTitle js-placardTitle '}).get('data-url')
			link = container.get('data-url')
			if link == None:
				container = container.find('a')
				link = container.get('href')
				apartment_list.append(link)
				count +=1
				"""
				debug info
				#print(count, ' ',link)
				#print('Warning' , count, ':Unusual way to get url')
				"""
			else:
				apartment_list.append(link)
				count +=1
				#print(count, ' ',link)
		return apartment_list
	
def getApartmentDetail(apartment, data):
	#data = pd.DataFrame(columns=['name', 'rent', 'minPrice', 'maxPrice', 'availability', 'year', 'address', 'phone', 'hours', 'link'])

	my_url = apartment
	print(my_url)
	headers = {
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
	}

	time.sleep(random.randint(5, 10))
	page_html = requests.get(my_url, headers=headers)
	page_soup = soup(page_html.text, 'html.parser')

	name = page_soup.find('h1', {'class': 'propertyName'}).text.strip()
	print(name)

	bedroom2B2B= []
	rentList = []
	availabilityList = []
	allPrice = []
	bedroom2B = page_soup.find('div', {'class': 'tabContent', 'data-tab-content-id': 'bed2'})
	if bedroom2B == None:
		return data
	bedroom2B2B = bedroom2B.findAll('tr', {'class': 'rentalGridRow', 'data-beds': '2', 'data-baths': ["2", "2.5"]})
	for bedroom in bedroom2B2B:
		rent = bedroom.find('td', {'class': 'rent'}).text.strip()
		availability = bedroom.find('td', {'class': 'available'}).text.strip()
		if rent != 'Call for Rent' and availability != 'Not Available':
			rent = re.sub('[$, ]', '', rent)
			if re.search('-', rent) != None:
				priceRange = rent.split('-')
				allPrice.append(int(priceRange[0]))
				allPrice.append(int(priceRange[1]))
			else:
				allPrice.append(int(rent))
			rentList.append(rent)
			availabilityList.append(availability)

	if len(allPrice) > 0:
		minPrice = 9999
		maxPrice = -9999
		for price in allPrice:
			if price < minPrice:
				minPrice = price
			if price > maxPrice:
				maxPrice = price
	else:
		return data

	print(rentList)
	print(minPrice)
	print(maxPrice)
	print(availabilityList)


	year = page_soup.find(string={re.compile('Built in')})
	if year == None:
		year = int('0')
	else:
		year = year.replace('Built in ', '')
		year = int(year)
	print(year)

	address = page_soup.find('div', {'class': 'propertyAddress'}).text.strip()
	address = " ".join(address.split())
	print(address)

	phone = page_soup.find('span', {'class': 'phoneNumber'})
	if phone != None:
		regex = re.search('([0-9-]){12}', phone.text.strip())
		phone = regex.group()
	print(phone)

	days = []
	hours = []
	officeHours = []
	days = page_soup.findAll('div', {'class': 'days'})
	hours = page_soup.findAll('div', {'class': 'hours'})
	count = 0
	for day in days:
		#officeHours = officeHours + " ".join(day.text.split()) + '  ' + " ".join(hours[count].text.split()) + ',\n'
		officeHours.append(" ".join(day.text.split()) + '  ' + " ".join(hours[count].text.split()))
		#officeHours[count].replace('\\n', '\n')
	print(officeHours)

	data = data.append(
		{'name': name, 'rent': rentList, 'minPrice': minPrice, 'maxPrice': maxPrice, 'availability': availabilityList, 'year': year, 'address': address, 'phone': phone, 'hours': officeHours,
		 'link': my_url}, ignore_index=True)

	return data

def main():
	numPages = int(getApartmentPageNum(sys.argv[1]))
	data = pd.DataFrame(
		columns=['name', 'rent', 'minPrice', 'maxPrice', 'availability', 'year', 'address', 'phone', 'hours',
				 'link'])
	for x in range(1, numPages+1):
		apartmentList = getApartmentList(sys.argv[1], x)
		for apartment in apartmentList:
			data = getApartmentDetail(apartment, data)
	fileName = 'Apartment.csv'
	data.to_csv(fileName, sep=',', encoding='utf-8')

	# apartment_list = getApartmentList(sys.argv[1], 1, numPages+1)
	# count = 1
	# for apartment in apartment_list:
	# 	print(count, apartment)
	# 	count += 1
	# getApartmentDetail(apartment_list)

if __name__ == '__main__':
	main()
