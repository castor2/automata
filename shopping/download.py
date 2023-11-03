from selenium import webdriver
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import subprocess
import os

chrome_command_macos = [
    "open",
    "-a",
    "Google Chrome",
    "--args",
    "--remote-debugging-port=9089",
    "--user-data-dir=" + os.getcwd() + "/chromeProfile",
]

driverPath = ChromeDriverManager().install()
# for windows
#subprocess.Popen(["start","chrome","--remote-debugging-port=9089","--user-data-dir=" + os.getcwd() + "/chromeProfile",],shell=True)
subprocess.Popen(chrome_command_macos)
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("debuggerAddress", "localhost:9089")
service = Service(executable_path=driverPath)
driver = webdriver.Chrome(service=service,options=options)

import os
import yaml

conf = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)
username = conf['site_info']['username']
password = conf['site_info']['password']
inputurl = conf['site_info']['url2']


def startBot(username, password, url):
    # opening the website  in chrome.
    driver.get(url)
    driver.implicitly_wait(3)

    # find the id or name or class of
    # username by inspecting on username input
    #driver.find_element(By.ID, "login_username").send_keys(username)
    #driver.findElement(By.ID("login_username")).send_keys(username)
    driver.find_element(By.XPATH, "//input[@name='login_username']").send_keys(username) # id 

    # find the password by inspecting on password input
    driver.find_element(By.ID, "login_password").send_keys(password)

    # click on submit
    #driver.find_element(By.ID, "login_click").click()
    #driver.find_element(By.ID, "Login-form-button").click()
    #driver.find_element_by_css_selector("login_click").click()
    #driver.find_element_by_css_selector("submit").click()
    #driver.find_element_by_css_selector("Login-form-button").click()
    login.click()

# Call the function
print(username, password, inputurl)
startBot(username, password, inputurl)

#login.click();
#String actualUrl="https://live.browserstack.com/dashboard";
#String expectedUrl= driver.getCurrentUrl();
#Assert.assertEquals(expectedUrl,actualUrl);


