# -*- encoding:utf-8 -*-
# Dependencies
import os
import sys
import time
from collections import namedtuple

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

Locator = namedtuple('Locator', ['by', 'value'])

sys.path.append(os.getcwd())


def chromedriver_init():
    """
    This function returns a headless incognito chromedriver
    :return: chromedriver
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--incognito")
    browser = webdriver.Chrome(options=chrome_options)
    # # Use the line below if you want to specify your chromedriver path
    # browser = webdriver.Chrome(options=chrome_options,executable_path="FILL YOUR PATH HERE")
    browser.maximize_window()
    return browser


class InfoGatherer:
    """
    This class takes your SIS account name and psw to gather your account information
    """

    def __init__(self, username, password):
        """
        Initializes the InfoGatherer
        :param username: your SIS username
        :param password: your SIS password
        """
        self.driver = chromedriver_init()
        self.url = "http://sis.rpi.edu"
        self.username = username
        self.password = password

    def __goto_page(self):
        """
        Goto the self.url page
        :return: None
        """
        self.driver.get(self.url)

    def __wait_element(self, element_path, time_limit=30):
        """
        Wait for element to load
        :param element_path: XPATH of the element
        :param time_limit: default to 30s, can customize
        :return: True if element load in time limit
        """
        try:
            WebDriverWait(self.driver, time_limit).until(
                EC.element_to_be_clickable(locator=Locator(by=By.XPATH, value=element_path))
            )
            # print("Element found!")
            return True
        except TimeoutException:
            print("Cannot find the given element in {} time limit, returning false".format(time_limit))
            print("XPATH given: {}".format(element_path))
            return False

    def __click(self, element_path):
        """
        Find the element then click
        :param element_path: XPATH of the element
        :return: None
        """
        if self.__wait_element(element_path):
            self.driver.find_element_by_xpath(element_path).click()

    def __text_input(self, element_path, text_input):
        """
        Input the given text into the element
        :param element_path: XPATH of the element
        :param text_input: the actual text to be inputted
        :return:
        """
        if self.__wait_element(element_path):
            element = self.driver.find_element_by_xpath(element_path)
            element.click()
            element.send_keys(str(text_input))

    # def go_until_element_found(self, element_path):
    #     """
    #     Load the url, found the given element
    #     XPATH of loading box: '//*[@id="login"]'
    #     :param element_path: XPATH of the element to be found
    #     :return: None
    #     """
    #     self.goto_page()
    #     self.wait_element(element_path)

    def __go_until_login_page_loaded(self):
        """
        Load the SIS page, wait until it completes loading
        :return: None
        """
        self.__goto_page()
        self.__wait_element('//*[@id="login"]')

    def __try_to_login(self):
        self.__text_input('//*[@id="username"]', self.username)
        # time.sleep(1)
        self.__text_input('//*[@id="password"]', self.password)
        # time.sleep(1)
        self.__click('//*[@id="password"]/../../..//input[@name="submit"]')
        # time.sleep(1)
        self.__wait_element('//div[@class="headerlinksdiv"]//table[@class="plaintable"]//table//td[3]')

    # noinspection SpellCheckingInspection,SpellCheckingInspection
    def __try_to_fetch_learned_courses(self):
        self.__click('//div[@class="headerlinksdiv"]//table[@class="plaintable"]//table//td[3]')
        # time.sleep(1)
        self.__click('//table[@class="menuplaintable"]//td[contains(.,"Degree Works")]/a')
        # time.sleep(1)
        self.__click('//button[@title="More"]')
        # time.sleep(1)
        self.__click('//li[contains(.,"Class History")]')
        # time.sleep(1)

        # Try to read out the course name and print
        self.__wait_element('//div[@role="dialog"]//*[@id="TermDivider"]/..//div//tr/td[1]')
        course_list = self.driver.find_elements_by_xpath(
            '//div[@role="dialog"]//*[@id="TermDivider"]/..//div//tr/td[1]')
        course_str = [ele.text for ele in course_list if len(ele.text) > 0]

        # print(course_str)
        return course_str

    def quit(self):
        self.driver.quit()

    def get_learned_courses(self):
        """
        Get the learned courses of the SIS user provided in initialization
        :return:
        """
        self.__go_until_login_page_loaded()
        self.__try_to_login()
        return self.__try_to_fetch_learned_courses()


if __name__ == "__main__":
    Gatherer = InfoGatherer(input("Enter your SIS username: "), input("Enter your sis password: "))
    print(Gatherer.get_learned_courses())
    Gatherer.quit()
    time.sleep(5)
