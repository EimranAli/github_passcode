# datbase related
import pymysql

# selenium related
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# connection parameters
endpoint = ''
username = ''
password = ''
database_name = ''

# connect to the database using connection parameters above.
# note : below syntax is for pymysql version 1.0.2. If this doesnt work in your code , check pymysql version you are using.
connection = pymysql.connect(host=endpoint, user=username, password=password, db=database_name)

def lambda_handler(event, context):

    # create a cursor to the database
    cursor = connection.cursor()
    cursor.execute('select code from Github where id=1')

    # fetch all the rows from the above query execution
    verification_code = cursor.fetchall()

    # if lambda is invoked via api-gateway passing a query parameter 'mode' mapping with 'poll' value in the url
    # example : if <api-arn> is arn of api-gatway , then we can pass the query parameter 
    # as "<api-arn>?mode=poll" in the browser search bar
    if event['queryStringParameters']['mode'] == 'poll' :
        # close the cursor,connection and return the verification code present in the database
        cursor.close()
        connection.close()
        return "Your latest GitHub verification code is : " + verification_code[0][0]

    # ----------------------------------web driver setup---------------------------------------------------
    # path to chromedriver. while testing locally, 'var/task/' is the temporary path where files and dependencies of the function are mounted.
    # 'var/task/' path stays the same for files and dependencies in aws lambda environment, when you upload the function as a zip file.
    driver_path = '/var/task/chromedriver'
    
    # path to headless-chromium
    binary_path = '/var/task/headless-chromium'

    # we'll use an instance of Options to specify certain things, while initializing the driver
    # https://www.selenium.dev/selenium/docs/api/rb/Selenium/WebDriver/Chrome/Options.html
    options = Options()

    # location(path) of headless-chromium binary file
    options.binary_location = binary_path

    # will start chromium in headless-mode
    options.add_argument('--headless')

    # below argument is for testing only;not recommended to be used in production.
    # https://chromium.googlesource.com/chromium/src/+/HEAD/docs/linux/sandboxing.md
    options.add_argument('--no-sandbox')

    # not using the below argument can limit resources.
    # https://www.semicolonandsons.com/code_diary/unix/what-is-the-usecase-of-dev-shm
    options.add_argument('--disable-dev-shm-usage')

    # "unable to discover open window in chrome" error pops up if u dont add the below argument
    # https://www.techbout.com/disable-multiple-chrome-processes-in-windows-10-26897/
    options.add_argument('--single-process')

    # initialize the driver
    driver = Chrome(executable_path=driver_path, options=options)

    # if code reaches this point, then driver is initialized and ready to use.
    print("driver initialized successfully.Begin coding your specific task (or) complete the boilerplate code below according to your email provider.")

    # ----------------------------------web driver setup done----------------------------------------------------

    # -----------------------automation logic for getting the verification code ---------------------------------
    email_url = ""
    # open email page
    driver.get(email_url)


    # store identifiers to locate web elements.
    # abs_xpath is absolute xpath, rel_xpath is relative xpath. use other identifiers of the elements(NAME, CLASSNAME, ID, LINK_TEXT, PARTIAL_LINK_TEXT etc..) when rel or abs xpaths dont work 
    signin_button_abs_xpath = ""
    email_box_abs_xpath = ""
    email_box_rel_xpath = ""
    email_next_button_rel_xpath = ""
    password_box_abs_xpath = ""
    password_next_abs_xpath = ""
    stay_signedin_abs_xpath = ""
    stay_signedin_no_button = ""
    add_recovery_email_page = ""
    add_recovery_email_page_skip_button = ""

    # create an instance of WebDriverWait, which is set for 10 seconds. This instance will be used while waiting for the web elements to be loaded on the webpage
    wait_for_ten = WebDriverWait(driver, 10)

    # use the instance here to wait for the signin button to be loaded on the webpage for a max of 10 seconds 
    wait_for_ten.until(
        EC.presence_of_element_located(
            (  
                By.XPATH,
                signin_button_abs_xpath
            )))

    # find and click signin
    driver.find_element(By.XPATH, signin_button_abs_xpath).click()

    # store email account creds in a variable for testing
    # use your outlook username
    email = ""
    # use your outlook password
    password = ""

    # wait for email box to appear . reusing the wait created earlier which is set
    # to wait for a max of 10 seconds
    wait_for_ten.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                email_box_abs_xpath
            )))

    # find the email box and pass the email in the box
    driver.find_element(By.XPATH, email_box_rel_xpath).send_keys(email)

    # click next button
    driver.find_element(By.XPATH, email_next_button_rel_xpath).click()

    # wait for password box to appear
    wait_for_ten.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                password_box_abs_xpath
            )))

    # pass the password in the box
    driver.find_element(By.XPATH, password_box_abs_xpath).send_keys(password)

    # click next button to login
    driver.find_element(By.XPATH, password_next_abs_xpath).click()

    print("logged in into your email")

    # if page appears asking if u want to stay signed in, then click "No" and proceed further, else
    # just display a mssg saying it didnt appear
    try:
        wait_for_ten.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    stay_signedin_abs_xpath
                )))

        driver.find_element(By.XPATH, stay_signedin_no_button).click()
    except:
        print("page, asking to stay signed-in didn't appear")

    # sometimes, pages asking to add recovery emails appear.Trying to skip them, if they do.
    try:
        wait_for_ten.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    add_recovery_email_page
                )))

        # click on "Skip" button         
        driver.find_element(By.XPATH, add_recovery_email_page_skip_button).click()
    except:
        print("page, asking to add recovery email didn't appear")

    # find the message containing the code using the subject of the email
    email_subject_sub_text = "[GitHub] Please verify"
    print("trying to find the email with verification code")
    wait_for_ten.until(
        EC.presence_of_element_located(
            (
                By.PARTIAL_LINK_TEXT,
                email_subject_sub_text
            )))

    print("opening the email with verification code")
    # click on that mail to open it
    driver.find_element(
                By.PARTIAL_LINK_TEXT,
                email_subject_sub_text).click()

    # store the key used to search the code (prefix of the code). Text in the email before the 6 digit code
    code_search_key = 'Verification code: '

    print("searching for verification code")
    # get the div with code
    code_div = driver.find_element(By.XPATH,"//*[contains(text(), search_key)]")

    # store the index of first occurrence of code_search_key
    index = code_div.text.find("Verification code: ")

    # otp sent by Github Team is of  6 digits
    code_length = 6

    # extract the substring starting from the end of search key to the end of the 6 digit code
    code = code_div.text[index + len(code_search_key):index + len(code_search_key) + code_length]
    final_message = "Your GitHub Verification Code is " + code
    # close the driver
    driver.quit()

    # create the query to update
    update_query = 'update Github set code=%s where id=%s'
    update_values = (code, 1)

    # execute the query
    cursor.execute(update_query, update_values)
    # commit the change
    connection.commit()

    # close the cursor and connection
    cursor.close()
    connection.close()

    # the below message won't be returned when calling lambda using api-gateway.
    # api-gateway's max limit to getting a response from any service is 30 seconds 
    # and the code won't reach this point in 30 seconds.

    # when we invoke this function using api-gateway without passing 'mode' 
    # parameter(which is used to poll for the latest code present in the database), time taken 
    # is around 23 seconds(db connection) + 1 min 1 second (selenium logic in fetching the code)
    
    # when 'mode' is passed with 'poll', then it only takes around 23 seconds for db connection 
    # and returns the latest verification code
    return final_message
