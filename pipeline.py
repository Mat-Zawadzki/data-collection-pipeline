#%%
import json
import requests
import os
import os.path
from bs4 import BeautifulSoup
from selenium import webdriver
from time import time, gmtime, strftime, sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options



class Scraper():
    def __init__(self,):
        self.start_time = time()
        self.starting_page = "https://www.lego.com/en-gb"
        self.starting_page_got = requests.get(self.starting_page)
        self.starting_html = self.starting_page_got.text
        self.soup = BeautifulSoup(self.starting_html, 'html.parser', on_duplicate_attribute='ignore') 
        self.links_to_themes_list = []
        self.links_to_products_list = []
        self.picture_sources_list = []
        self.theme_directory = "first_theme_directory"
        self.product_directory = "first_product_directory"



    def get_links_to_themes_list(self):
        '''finds all links in html code, and saves the themes in a list'''
        for links_to_themes in self.soup.find_all('a'):
            links_to_themes = links_to_themes.get('href')
            if "/en-gb/themes" in links_to_themes:
                self.links_to_themes_list.append(links_to_themes)
        self.links_to_themes_list = self.links_to_themes_list[:41]

        '''adds www.lego in front of links so they're correct'''
        for links_to_themes in range(len(self.links_to_themes_list)):
            self.links_to_themes_list[links_to_themes] = ("https://www.lego.com" + self.links_to_themes_list[links_to_themes])


    
    def press_continue_and_cookies_and_load_more_buttons(self, driver):
        '''presses continue button and accepts cookies'''
        sleep(1)
        continue_onto_shop_button = driver.find_element(by=By.XPATH, value='//button[text()="Continue"]')
        continue_onto_shop_button.click()
        sleep(1)
        accept_cookies_button = driver.find_element(by=By.XPATH, value='//button[text()="Accept All"]')
        accept_cookies_button.click()
        sleep(1)

        '''scrolls to bottom of page, checks if load more button exists, and loads it up if it does'''
        driver.execute_script("window.scrollTo(0, 3200);")
        try:
            sleep(1)
            press_all_button = driver.find_element(by=By.LINK_TEXT, value='Show All')
            press_all_button.click()
            sleep(1)
            driver.execute_script("window.scrollTo(0, 3200);")
            sleep(2)
            driver.execute_script("window.scrollTo(0, 6400);")
            sleep(2)
            driver.execute_script("window.scrollTo(0, 9800);")
            sleep(2)
            driver.execute_script("window.scrollTo(0, 13000);")
            sleep(2)
            driver.execute_script("window.scrollTo(0, 16000);")
            sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")

        except NoSuchElementException:
            print("There's no load more button")



    def scrape_theme_page_for_products_list(self):
        '''Scrapes each product on each theme page'''
        for link_to_themes in self.links_to_themes_list:  

            self.theme_name = link_to_themes[34:]
            self.theme_directory = self.starting_directory + self.theme_name

            os.mkdir(self.theme_directory)

            theme_file_list = []
            theme_file_list.append(link_to_themes)

            options = Options()
            options.headless = True 
            driver = webdriver.Firefox(options=options)
            driver.get(link_to_themes)
            
            self.press_continue_and_cookies_and_load_more_buttons(driver)
            self.get_products_list(driver)

            driver.close()



    def get_products_list(self, driver):
        '''gets products list'''
        links_to_current_products_list = []

        for product_link in driver.find_elements(By.TAG_NAME, "a"):
                product_link = product_link.get_attribute("href")

                if "/en-gb/product" in product_link and product_link not in links_to_current_products_list:
                    links_to_current_products_list.append(product_link)
                    
                    if product_link not in self.links_to_products_list:
                        self.links_to_products_list.append(product_link)

        self.links_to_products_list = self.links_to_products_list[1:]
        links_to_current_products_list = links_to_current_products_list[1:]
        
        for product_link in links_to_current_products_list:
            self.get_product_data(product_link)



    def create_starting_directory(self):
        self.starting_directory = "C://lego_scraped//"
        os.mkdir(self.starting_directory)



    def get_product_data(self, product_link):
        '''gets all the data for each product into its own file'''
        self.product_links_into_product_link_soup(product_link)
        self.create_and_check_product_name_is_correct()
        self.create_and_check_product_directory_is_correct()
        self.download_all_images_for_product(product_link)
        self.save_product_data_as_json()
        print(self.product_name + " is scraped")



    def save_product_data_as_json(self):
        product_number = "a"
        price_of_product_html = self.soup.find('h3')
        price_of_product = price_of_product_html
        time_scraped = (strftime("%a, %d %b %Y %H:%M:%S", gmtime()))

        self.product_data = {
            "Name":self.product_name,
            "Product number":product_number,
            #"Price":price_of_product,
            "Time_scraped":time_scraped,
            "Number_of_images":len(self.picture_sources_list),
            "Picture_links":self.picture_sources_list,
        }

        json_product_directory = self.product_directory + "//" + self.product_name + ".json"
        with open(json_product_directory, "w") as write_file:
            json.dump(self.product_data, write_file)



    def create_and_check_product_directory_is_correct(self):
        '''creates product directory and checks for any unorthodox characters the computer might struggle with'''
        self.product_directory = self.theme_directory + "//" + self.product_name

        if os.path.exists(self.product_directory) == True:
            self.product_directory = self.product_directory + "1"

        self.product_directory = self.product_directory.replace(' ', '_')
        os.mkdir(self.product_directory)



    def create_and_check_product_name_is_correct(self):
        '''finds name of product and checks for any unorthodox characters the computer might struggle with'''
        name_of_product_html = self.soup.find('h1')
        self.product_name = name_of_product_html.string

        if ":" in list(self.product_name[3:]):
            self.product_name = self.product_name.replace(":","") 

        if "™" in list(self.product_name):
            self.product_name = self.product_name.replace("™","")

        if "®" in list(self.product_name):
            self.product_name = self.product_name.replace("®","")

        if os.path.exists(self.product_name) == True:
            self.product_name = self.product_name + "1"

        self.product_name = self.product_name.replace(' ', '_')



    def download_all_images_for_product(self, product_link):
        self.get_product_image_links(product_link)
        for picture_source in self.picture_sources_list:
            image_number = self.picture_sources_list.index(picture_source)+1
            self.download_single_image(picture_source, self.product_directory + "//" + self.product_name + "_" +  str(image_number) + ".jpg")



    def get_product_image_links(self, product_link):
        self.product_links_into_product_link_soup(product_link)
        self.picture_sources_list = []
        for picture_source in self.soup.find_all('img'):
            picture_source = picture_source.get('src')
            picture_source = picture_source[:(picture_source.find("?"))]
            if "/set/assets/" in picture_source and picture_source not in self.picture_sources_list:
                self.picture_sources_list.append(picture_source)
        self.picture_sources_list = self.picture_sources_list[:-1]



    def product_links_into_product_link_soup(self, product_link):   #takes html webpage and breaks it down into reusable code form
        product_page = requests.get(product_link)
        product_page_html = product_page.text
        self.soup = BeautifulSoup(product_page_html, 'html.parser')



    def download_single_image(self, picture_source, file_path):
        img_data = requests.get(picture_source).content
        with open(file_path, "wb") as handler:
            handler.write(img_data)



def main():
    scrape = Scraper()
    scrape.create_starting_directory()
    scrape.get_links_to_themes_list()
    scrape.scrape_theme_page_for_products_list()



if __name__ == "__main__":
    main()
#%%
