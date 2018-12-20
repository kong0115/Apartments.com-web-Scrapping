# Apartment-Finder-Hack for Apartment.com



"""
Created on Thu May 31 11:34:20 2018

@author: dhuang
"""

from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import re
import pandas as pd
import numpy as np

####################### Search result
my_url = 'https://www.apartments.com/2-bedrooms-under-1300/?bb=014wxvypzJ2u418xB'
uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, 'html.parser')


containers = page_soup.findAll('article', {'class': 'placard'})
#containers = page_soup.findAll('header', {'class':'placarHeader'})

link_list = []
print('Page 1')
for container in containers:
    link = container.find('a', {'class':'placardTitle js-placardTitle '}).get('href')
    print(link)
    link_list.append(link)



for x in range(2,8):
    my_url = 'https://www.apartments.com/2-bedrooms-under-1300/'+ str(x) + '/?bb=014wxvypzJ2u418xB'
    uClient = uReq(my_url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, 'html.parser')


    containers = page_soup.findAll('article', {'class': 'placard'})
    #containers = page_soup.findAll('article', {'class':'diamond placard'})

    print('\nPage ', x)

    count = 1
    for container in containers:

        try:
            link = container.find('a', {'class':'placardTitle js-placardTitle '}).get('href')
            print(count, ' ',link)
            link_list.append(link)
            count +=1
        except:
            print('     somthing here')




####################### individual apt page

## REMOVE link_list[122] https://www.apartments.com/11911-marsh-ln-dallas-tx-unit-216/kb25jmb/
## link_list[123] https://www.apartments.com/11911-marsh-ln-dallas-tx-unit-224/6b0zetv/
## info incomplete, fishy
link_list.remove('https://www.apartments.com/11911-marsh-ln-dallas-tx-unit-216/kb25jmb/')
link_list.remove('https://www.apartments.com/11911-marsh-ln-dallas-tx-unit-224/6b0zetv/')
## not available
## https://www.apartments.com/walnut-creek-apartments-carrollton-tx/ln9z0dd/
link_list.remove('https://www.apartments.com/walnut-creek-apartments-carrollton-tx/ln9z0dd/')
## not even in dallas
link_list.remove('https://www.apartments.com/villas-escondidas-apartments-edinburg-tx-unit-3/5qs66rp/')
link_list.remove('https://www.apartments.com/villas-escondidas-apartments-edinburg-tx-unit-3/ymn7xxs/')



data = pd.DataFrame(columns= ['name', 'rent', 'time', 'year', 'address', 'phone', 'hours', 'link'] )
for link in range(len(link_list)):

    print('Link ', link+1)
    #my_url = 'https://www.apartments.com/the-aster-by-cortland-dallas-tx/hceww83/'
    my_url = link_list[link]
    print(my_url)
    uClient = uReq(my_url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, 'html.parser')

    name = page_soup.find('h1', {'class':'propertyName'}).text.strip()

    try:
        year = page_soup.findAll(string={re.compile('Built in 1'), re.compile('Built in 2')})[0]
        year = year.replace('Built in ', '')
    except:
        print('check this')

    hours = []
    #days_hours = page_soup.findAll('div', {'class': 'officeHoursContainer'})
    days_hours = page_soup.findAll('div', {'class': 'daysHoursContainer'})
    for i in range(len(days_hours)):
        #print(re.sub('[\t\n\r]','',days_hours[i].text.strip()))
        hours.append(re.sub('[\t\n\r]','',days_hours[i].text.strip()))


    phone = page_soup.find('span', {'class':'contactPhone'}).text

    address = page_soup.find('div', {'class':'propertyAddress'}).text
    address = re.sub('[\t\n\r ]','',address.strip())

    #my_url = 'https://www.apartments.com/neo-midtown-apartments-dallas-tx/spkbyn6/'
    rent = page_soup.findAll('span', {'class':'rentRollup'})
    for x in rent:
        long = x.findAll('span', {'class':'shortText'})
        #print(long)
        if '2' in long[0].text:
            #print('yes')
            #print(x)
            #price = x.find(string=re.compile('$'))
            price = re.search('\$(.+?)\r',x.text).group(1)

    #rent_list0=[]
    time_list = []
    containers = page_soup.findAll('tr', {'class': 'rentalGridRow', 'data-beds' : '2'})
    for container in containers:
    #    rent =  container.find('td', {'class': 'rent'}).text
        #print(rent)
    #    rent_list0.append(rent)

        time = container.find('td', {'class': 'available'}).text
        #print(time)
        time_list.append(time)

    #rent_list = []
    #for i in range(len(rent_list0)):
        #print(rent_list0[i].strip())
    #    rent_list.append(rent_list0[i].strip())

    try:
        ava = time_list[0].strip()
        #ren = rent_list[0]
    except:
        print('check this')


    #data = data.append(pd.DataFrame([name, rent, time, year, address, phone, hours, my_url]), ignore_index =True)
    data = data.append({'name' : name, 'rent' : price, 'time' : ava, 'year' : year, 'address' : address, 'phone':phone, 'hours':hours, 'link':my_url}, ignore_index =True)


data['year'] = data['year'].astype(int)


'''
for link in soup.find_all('a'):
    print(link.get('href'))
# http://example.com/elsie
# http://example.com/lacie
# http://example.com/tillie
'''
