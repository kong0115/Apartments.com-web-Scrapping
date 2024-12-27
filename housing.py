# Web Scrapping for Apartments.com

from bs4 import BeautifulSoup as soup
import re
import pandas as pd
import sys
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import json
import os
import traceback


def initializeSelenium(proxy=None):
    # Configure options for Chrome
    chrome_options = Options()
    ## chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Prevent detection of automation
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("window-size=1920,1080")
    user_agent = UserAgent(
        browsers=["chrome"], platforms=["pc"], min_version=120.0
    ).random
    print(user_agent)
    chrome_options.add_argument(f"user-agent={user_agent}")

    if proxy is not None:
        chrome_options.add_argument(f"--proxy-server={proxy}")

    # Path to the ChromeDriver executable
    chrome_driver_path = "C:\\chromedriver.exe"

    # Create a new instance of the Chrome driver
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def getPageHtmlContent(web_driver, website_url, wait_time):
    web_driver.get(website_url)
    time.sleep(wait_time)
    page_html = web_driver.page_source
    page_soup = soup(page_html, "html.parser")
    return page_soup


def getApartmentListHtmlContent(web_driver, website_url, x, wait_time):
    regex = re.search(".*/\?", website_url)
    index = regex.span()
    new_url = website_url[: index[1] - 1] + str(x) + "/" + website_url[index[1] - 1 :]
    return getPageHtmlContent(web_driver, new_url, wait_time)


def getApartmentPageNum(web_driver, websiteURL, wait_time=5):
    page_soup = getApartmentListHtmlContent(web_driver, websiteURL, 1, wait_time)
    page_range = page_soup.find("span", {"class": "pageRange"}).text
    match = re.search(r"Page \d+ of (\d+)", page_range)
    if match:
        return int(match.group(1))
    else:
        raise Exception("Page range not found!")


def getApartmentList(web_driver, websiteURL, page, wait_time=10):
    page_soup = getApartmentListHtmlContent(web_driver, websiteURL, page, wait_time)
    containers = page_soup.find_all("article", {"class": "placard"})
    print("\nPage ", page)
    count = 0
    apartment_list = []
    for container in containers:
        link = container.get("data-url")
        if link:
            count += 1
            apartment_list.append(link)
            #print(count, " ", link)
        else:
            print("apartment link not found!")
    return apartment_list


def getApartmentDetail(web_driver, apartment_link):
    print(apartment_link)
    page_soup = getPageHtmlContent(web_driver, apartment_link, random.randint(5, 8))
    divs_to_remove = page_soup.find_all(
        "div", {"class": "jsAvailableModels hideModelCardOnCollapsed"}
    )
    for div in divs_to_remove:
        div.decompose()
    name = page_soup.find("h1", {"class": "propertyName"}).text.strip()

    bedroom2B2B_html_list = []
    floor_plan_list = []
    all_prices = []
    bedroom2B_section = page_soup.find(
        "div", {"class": "tab-section", "data-tab-content-id": "bed2"}
    )
    if bedroom2B_section == None:
        print("2 Beds floor plans not found")
        return None
    bedroom2B_plans = bedroom2B_section.find_all("div", {"class": "pricingGridItem"})
    for bedroom2B_plan in bedroom2B_plans:
        inner_span = bedroom2B_plan.find("span", {"class": "detailsTextWrapper"})
        if (
            inner_span
            and "2 Beds" in inner_span.get_text()
            and "2 Baths" in inner_span.get_text()
        ):
            bedroom2B2B_html_list.append(bedroom2B_plan)
    if len(bedroom2B2B_html_list) == 0:
        print("2 Beds 2 Baths floor plans not found")
        return None
    for bedroom_plan in bedroom2B2B_html_list:
        is_valid_rent = True
        rent = re.sub(
            "[$, ]", "", bedroom_plan.find("span", {"class": "rentLabel"}).text.strip()
        )
        if "–" in rent:
            all_prices.extend(rent.split("–"))
        elif rent.isdigit():
            all_prices.append(rent)
        elif rent.lower() == "callforrent":
            is_valid_rent = False
        else:
            print(f"invalid format found for rent: {rent}")
            is_valid_rent = False
        if is_valid_rent:
            floor_plan_name = bedroom_plan.find(
                "span", {"class": "modelName"}
            ).text.strip()
            size = (
                bedroom_plan.find("span", {"class": "detailsTextWrapper"})
                .find("span", string=lambda text: text and "Sq Ft" in text)
                .get_text(strip=True)
            )

            availability = bedroom_plan.find("span", {"class": "availabilityInfo"})
            if availability:
                availability = [availability.text.replace("Available", "").strip()]
            else:
                availability_list = bedroom_plan.find_all(
                    "span", {"class": "dateAvailable"}
                )
                availability = list(
                    set(
                        [
                            dateAvailable.find_all(string=True, recursive=True)[
                                -1
                            ].strip()
                            for dateAvailable in availability_list
                        ]
                    )
                )
            floor_plan = {
                "name": floor_plan_name,
                "size": size,
                "rent": rent,
                "availability": availability,
            }
            # print(floor_plan)
            floor_plan_list.append(floor_plan)

    all_prices = list(map(int, all_prices))
    min_price = 9999
    max_price = -9999
    if len(all_prices) > 0:
        for price in all_prices:
            if price < min_price:
                min_price = price
            if price > max_price:
                max_price = price
    else:
        print("No rent is found for this property")
        return None

    # print(min_price)
    # print(max_price)

    year = None
    details_section = page_soup.find_all(
        "div", {"class": "mortar-wrapper feesPoliciesCard twoCols with-bullets-card"}
    )
    for div in details_section:
        match = re.search(r"Built in (\d+)", div.get_text())
        if match:
            year = match.group(1)
    if year is None:
        year = ""
        print("built year not found for the property")
    # print(year)

    address = page_soup.find("div", {"class": "propertyAddress"}).text.strip()
    address = " ".join(address.split()).replace("Property Address:", "").strip()
    # print(address)

    phone = page_soup.find("div", {"class": "phoneNumber"}) or page_soup.find(
        "span", {"class": "phoneNumber"}
    )
    if phone:
        phone = phone.text.strip()
    # print(phone)

    office_hours = page_soup.find_all("span", {"class": "daysHoursContainer"})
    office_hours = [office_hour.get_text(strip=True) for office_hour in office_hours]
    # print(office_hours)

    review_rating = page_soup.find("span", {"class": "reviewRating"})
    if review_rating:
        review_rating = review_rating.text.strip()
    else:
        review_rating = ""
    review_count = page_soup.find("a", {"class": "reviewCount"}).text.strip()
    review_count = re.sub(
        r"[^0-9]", "", review_count
    )  # Remove everything except digits

    monthly_fees = []
    one_time_fees = []
    required_fees_section = page_soup.find("div", {"aria-labelledby": "required-fees"})
    if required_fees_section:
        required_fees = required_fees_section.find_all("div", {"class": "feespolicies"})
        for required_fee in required_fees:
            fee_sections = required_fee.find_all(
                "li", {"class": "no-bullets horizontal-line"}
            )
            fees = []
            for fee_section in fee_sections:
                if (
                    fee_section.find("span", {"class": "component-row header-column"})
                    is not None
                ):
                    continue
                fee_name = fee_section.find("div", {"class": "feeName ellipsis"})
                fee_value = fee_section.find("div", {"class": "column-right"})
                fee_comments = fee_section.find("div", {"class": "comments truncated"})
                if fee_name and fee_value:
                    fee_name_text = fee_name.text.strip()
                    fee_value_text = fee_value.text.strip()
                    if fee_comments:
                        fee_comments_text = fee_comments.text.strip()
                        fees.append(
                            {
                                fee_name_text: {
                                    "value": fee_value_text,
                                    "comments": fee_comments_text,
                                }
                            }
                        )
                    else:
                        fees.append({fee_name_text: fee_value_text})
                else:
                    print(
                        f"fee name or fee value not found. fee_name: {fee_name}, fee_value: {fee_value}"
                    )
                    print(f"fee_section: {fee_section}")
            fee_type = required_fee.find(
                "span", {"class": "component-row header-column"}
            ).text.strip()
            if "month" in fee_type.lower():
                monthly_fees = fees
            elif "one-time" in fee_type.lower():
                one_time_fees = fees

    # print(monthly_fees)
    # print(one_time_fees)

    return {
        "name": name,
        "link": apartment_link,
        "minPrice": min_price,
        "maxPrice": max_price,
        "monthlyFees": monthly_fees,
        "oneTimeFees": one_time_fees,
        "floorPlanList": floor_plan_list,
        "year": year,
        "address": address,
        "reviewRating": review_rating,
        "reviewCount": review_count,
        "phone": phone,
        "hours": office_hours,
    }


def main():
    web_driver = None
    try:
        file_name = "Apartment.csv"
        apartment_list = []
        if os.path.exists(file_name):
            apartment_list = pd.read_csv(file_name).to_dict(orient="records")
        apartment_list_dict = {
            apartment["link"]: apartment for apartment in apartment_list
        }
        web_driver = initializeSelenium()
        num_pages = getApartmentPageNum(
            web_driver,
            sys.argv[1],
        )
        print(f"Total number of pages: {num_pages}")
        for x in range(1, num_pages + 1):
            apartment_links = getApartmentList(web_driver, sys.argv[1], x)
            # apartment_links = [
            #   ""
            # ]
            for link in apartment_links:
                if apartment_list_dict.get(link) is None:
                    apartment_detail = getApartmentDetail(web_driver, link)
                    if apartment_detail is not None:
                        apartment_list.append(apartment_detail)
        # json_data = json.dumps(apartment_detail, indent=4, ensure_ascii=False)
        # print(json_data)
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

    if web_driver is not None:
        web_driver.quit()
    pd.DataFrame(apartment_list).to_csv(file_name, index=False)


if __name__ == "__main__":
    main()
