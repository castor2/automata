#
# python for shopping
# 20200228 
# Reference / guide
# https://m.blog.naver.com/PostView.nhn?blogId=nonamed0000&logNo=220977390647&proxyReferer=https%3A%2F%2Fwww.google.com%2F
# https://m.blog.naver.com/jsk6824/221741518308
# https://gencode.me/blogs/post/45/    javascrip?:check() login
# https://stackoverflow.com/questions/21213417/select-check-box-using-selenium-with-python for checkbox
# https://stackoverflow.com/questions/37879010/selenium-debugging-element-is-not-clickable-at-point-x-y for check box
# https://stackoverflow.com/questions/7867537/how-to-select-a-drop-down-menu-value-with-selenium-using-python for dropdown option
#
# prerequisitory
#
# 1. install python
# 2. $ python -m pip install --upgrade pip
# 3. chromedriver should get the same version with chrome 
#    download from https://chromedriver.chromium.org/downloads
# 4. $ pip install selenium   for chrome driver
# 5. $ pip install telepot    for telegram bot 
# 6. $ pip install discord    for discord bot
# 
# note that there needs enough time(5~15 seconds) for page loading between steps 

from selenium import webdriver
from selenium.webdriver.common.alert import Alert 
from selenium.webdriver.common.keys import Keys     # need to send keystrokes, checkbox
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select    # for drop downmenu
from selenium.webdriver.common.by import By

import time 
import sys            # for commnad argument 
import getopt         # for commnad argument 
import telepot
token = '1111:aaaa' # bot API token
mc = 'telegram_ID' # telegram_ID in number
bot = telepot.Bot(token) 
#driver = webdriver.Chrome('C:\\Util\\chromedriver_win32\\chromedriver.exe')
#driver = webdriver.Chrome('/opt/homebrew/bin/chromedriver')
driver = webdriver.Chrome()

# get arguments 
#total   = len(sys.argv)
#cmdargs = str(sys.argv)
#print ("The total numbers of args passed to the script: %d " % total)
#print ("Args list: %s " % cmdargs)
#if(total==1):
#    print("Usage: %s -m mode" % sys.argv[0])
#    print("mode=1 costco")
#    print("mode=2 welkeeps")
#    print("mode=3 sanggong")
#    print("mode=4 costco welcron")
#    print("mode=5 coupang")
#
#try:
#    args = getopt.getopt(sys.argv[1:],"m:")
#except getopt.GetoptError as e:
#    print (str(e))
#    print("Usage: %s -m mode" % sys.argv[0])
#    sys.exit(2)
#
# Pharsing args one by one 
#print ("Script name: %s" % str(sys.argv[0]))
#for i in range(total):
#    print ("Argument # %d : %s" % (i, str(sys.argv[i])))
#for o, a in args:
#    if o == '-m':
#        print("mode=",a)
#    else:
#        print("Usage: %s -m mode" % sys.argv[0])

# 0 do nothing
# 1 costco online welkeeps
# 2 welkeeps shopping mall 
# 3 sangong naver store
# 4 costco online WKRON
# 5 costco online KBY
# 6 coupang TMSA
mode = 5

if(mode==1 or mode==4 or mode==5):
    # step 1. login 
    my_id = 'costco_ID'        # replace your ID here
    my_pw = 'costco_password'  # replace your password here
    url_login = 'https://www.costco.co.kr/login' 
    driver.get(url_login)
    driver.implicitly_wait(5)
    driver.find_element("xpath", "//input[@name='j_username']").send_keys(my_id) # id 
    driver.find_element("xpath", "//input[@name='j_password']").send_keys(my_pw) # pw
    driver.find_element("xpath", "//button[@id='loginSubmit']").click() # click login button
    driver.implicitly_wait(5)
    # step 2. purchase
    # BudaeJjigae
    # url2 = 'https://www.costco.co.kr/Food/Processed-Food/PastaNoodles/Cooktam-Budae-Hot-Pot-545g-x-2-Min-order-qty-2/p/627480'
    if (mode==1): 
      # welkeeps mask 
      url2 = 'https://www.costco.co.kr/HealthSupplement/Home-Health-CareFirst-Aid/First-Aid/Maybreeze-KF80-Black-Mask-30ct-Large/p/618610-L'
    elif (mode==4): 
      # welcron mask
      url2 = 'https://www.costco.co.kr/HealthSupplement/Home-Health-CareFirst-Aid/First-Aid/Welcron-Free-Tech-KF94-Mask-30ct/p/630918'
    elif (mode==5): 
      # KBY mask 
      url2 = 'https://www.costco.co.kr/HealthSupplement/Home-Health-CareFirst-Aid/First-Aid/KIMBERLY-KF80-MASK-10CT-Large/p/631521-L'
    else: 
       print("unknown url:",url2)

    driver.get(url2)
    
    element = 1
    iter = 0 
    while( element ):
        try: 
            element = driver.find_element(By.CLASS_NAME, 'error-page-title')
            print("costco welkeeps mask sold out. refreshing:", iter)
            driver.refresh()
            time.sleep(5)
            iter +=1 
        except NoSuchElementException as e: 
            #print(driver.page_source)
            numStringFound = driver.page_source.find('buyNowButton')
            if( numStringFound==-1 or numStringFound==0 ): 
                print("buyNowButton not found:", numStringFound, ", continue refreshing:", iter)
                driver.refresh()
                time.sleep(5)
                iter +=1 
            else: # buyNowButton found 
                print("stock exist. buyNowButton")
                bot.sendMessage(mc, 'stock exist. buyNowButton') # send message to me
                element =0
            time.sleep(1)
    
    try: 
        driver.find_element_by_xpath("//button[@name='buyNowButton']").click() # click buyNowButton
    except NoSuchElementException as e: 
        bot.sendMessage(mc, 'page loading error. retry manually(costco)') # send message to me


    print('implicitly_wait: 10s')
    driver.implicitly_wait(10)

    # step 3. checkout page
    for i in range(10):
        try:
            # handle checkbox 
            # method 1 (not working) - find element by class name 
            #element = driver.find_element_by_class_name('costco-custom-checkbox__input sr-only ')
            #driver.execute_script("arguments[0].click();", element)
            # method 2 (works well) - find element by name and send key
            inputElement = driver.find_element_by_name('accept')
            #inputElement.send_keys("\n") #send enter for links, buttons
            inputElement.send_keys(Keys.SPACE) #for checkbox etc
            # method 3 (not working) - find element by xpath and click
            #driver.find_element_by_id("accept").click()                               # consent checkbox
            #driver.find_element_by_xpath("//input[@name='accept']").click()           # consent checkbox
            # checkbox status 
            #result = driver.find_element_by_xpath("//input[@name='accept']").get_attribute('checked')
            #print("checked:", result)
            break
        except NoSuchElementException as e:
            print('retry in 1s.')
            time.sleep(1)
    else:
        e=0
        # raise e

    # final payment. paymentbuttonsubmit 
    driver.find_element_by_xpath("//button[@id='paymentbuttonsubmit']").click() # payment button
    driver.implicitly_wait(5)
    bot.sendMessage(mc, 'Purchase completed.'+url2) # send message to me

