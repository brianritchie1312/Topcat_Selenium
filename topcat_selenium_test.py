# Notes
 # Selenium Must be installed via pip
 # webdriver executables must be in system PATH or specified in arguments
 # Geckodriver excutable should be bash script with '/path/to/executable "$@" --marionette-port 2828' INSIDE
 # Python2.7 must be withn system PATH
 # pyvirtualdisplay and xvfb are needed for virtual displays
 # This script was written in atom which allows collapsing of indented blocks so it may be clogged without this feature

# TODO
    # If possible, no reliance on ansible (except args file)
      # Install chosen browsers
      # Install selenium, pyvirtualdisplay, etc.
    # Replace time.sleep with reliable wait_until
    # Add tests for everything in checklist
    # Add Upwards Browsing to browse tests
    # Add Tickbox checking for Search Test
    # Check for correct info in Infotab Test

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

# Print, this has been imported to allow 'print("string", end="")'
from __future__ import print_function

# Selenium
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

# PyVirtualDisplay
from easyprocess import EasyProcess
from pyvirtualdisplay import Display

# OS
import os
import os.path

# Platform
import platform

# Download
import urllib
import urllib2

# Check if zipfle exists
import tarfile
import zipfile

# Delay
import time

# Time
import datetime

# Argparse
import argparse

# Regexp
import re

# Firefox
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# Chrome
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options as ChromeOptions


#-------------------------------------------------------------------------------
# Arguments, options
#-------------------------------------------------------------------------------

parser = argparse.ArgumentParser(description='Gather variables from command line')
required = parser.add_argument_group('required arguments')

# ICAT URL
required.add_argument('--url',
                      action='store',
                      dest='icat_url',
                      help='The url of the icat build you wish to test, including port number.',
                      required=True)

parser.add_argument('--fac-short',
                    action='store',
                    dest='fac_short',
                    help='Short Name of Facility, used in URLs. (eg. --fac-short LILS) (default: LILS)',
                    required=False,
                    )

parser.add_argument('--fac-long',
                    action='store',
                    dest='fac_long',
                    help='Long Name of Facility, used in Login and footer. (eg. --fac-short Lorum Ipsum Light Source) (default: Lorum Ipsum Light Source)',
                    required=False,
                    )

# Priviillged user
required.add_argument('--user-data',
                      action='append',
                      nargs='+',
                      dest='user_data',
                      help='The user with rights to the testdata. (syntax: --user-data <mechanism> <username> <password>) (eg. --user-data simple root pass)',
                      required=True)

# Unprivillaged user
parser.add_argument('--user-nodata',
                    action='append',
                    nargs='+',
                    dest='user_nodata',
                    help='The user without rights to the testdata, used to ensure unprivileged users can not access data. If not used, No Data User Tests will not be performed. (syntax: --user-nodata <mechanism> <username> <password>) (eg. --user-nodata simple user1 pass)',
                    required=False)

# Unprivillaged user
parser.add_argument('--user-admin',
                    action='append',
                    nargs='+',
                    dest='user_admin',
                    help='The admin user, only needed if --user-data is not admin. If not used, Data User will perform admin tests. (syntax: --user-admin <mechanism> <username> <password>) (eg. --user-admin simple root pass)',
                    required=False)

# Create Virtual Display if GUI unavailiable
parser.add_argument('--virtual-display',
                     action='store_true',
                     dest='virtual_display',
                     help='Creates a pyvirtualdisplay, use if GUI is unavailiable',
                     required=False)

# Working directory if in alternative location
parser.add_argument('--path',
                    action='store',
                    dest='dir_test',
                    help='Absolute path to directory containing webdrivers and download folders (default: parent directory of this script)',
                    required=False)

# Browsers to test
parser.add_argument('--browsers',
                    action='append',
                    nargs='+',
                    dest='browsers',
                    help='List of browsers to test. eg. "--browsers firefox chrome" (default: firefox) (supported: firefox, chrome)',
                    required=False)

# Log level
parser.add_argument('--log-level',
                    action='store',
                    dest='log_level',
                    help='Log level of webdrivers (default: unchanged). Currently only firefox supported. eg. --log-level trace',
                    required=False)

# Geckodriver
parser.add_argument('--geckodriver',
                    action='store',
                    dest='geckodriver_version',
                    help='Download and extract specified geckodriver (firefox webdriver) version if not already present. eg. "--dwn-geckodriver 0.19.1". (default: nothing download)',
                    required=False)

# chromedriver
parser.add_argument('--chromedriver',
                    action='store',
                    dest='chromedriver_version',
                    help='Download and extract specified chromedriver (chrome webdriver) version if not already present. eg. "--dwn-chromedriver 2.35". (default: nothing download)',
                    required=False)

# OS name
parser.add_argument('--os',
                    action='append',
                    nargs='+',
                    dest='os_name',
                    help='If python is incorrectly guessing the os of the machine, you can overide it with this. (syntax: --os <os> <bits>) (eg. "--os windows 64" or "--os linux 32")',
                    required=False)

# Gather all arguments

# Example arguments, meant for testing within IDE (eg. Atom Runner)
args = parser.parse_args(['--url', 'http://vm1.nubes.stfc.ac.uk:8080',
                          # '--fac-short', 'LILS',
                          # '--fac-long', 'Lorum Ipsum Light Source',
                          '--user-data', 'simple', 'root', 'pass',
                          '--user-nodata', 'db', 'root', 'password',
                          # '--user-admin', 'simple', 'root', 'pass',
                          # '--path', '/home/user1/icatdownloads/Tests',
                          # '--virtual-display',
                          '--browsers', 'chrome', 'firefox',
                          # '--log-level', 'trace',
                          '--geckodriver', '0.19.1',
                          '--chromedriver', '2.35',
                          '--os', 'WiNdOwS', '64',
                          ])

# args = parser.parse_args(['--help'])

# Uncomment the line below line when using actual CLI arguments

# args = parser.parse_args()

#-------------------------------------------------------------------------------
# Variables
#-------------------------------------------------------------------------------

class txt:
    BASIC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    HEADING = YELLOW + BOLD
    SUBHEADING = BOLD
    Success = GREEN + 'Success' + BASIC
    Failed = RED + 'Failed' + BASIC
#-END-

# --fac-short
if (args.fac_short != None):
    facilty_short_name = args.fac_short
else:
    facilty_short_name = "LILS"
#-END-

# --fac-long
if (args.fac_long != None):
    facilty_long_name = arg.fac_long
else:
    facilty_long_name = "Lorum Ipsum Light Source"
#-END-

# --url
icat_url = args.icat_url
icat_home = icat_url + "/#/my-data/" + facilty_short_name
#-END-

# --user-data
user_data_mech = args.user_data[0][0]
user_data_name = args.user_data[0][1]
user_data_pass = args.user_data[0][2]
#-END-


# --user-nodata
if (args.user_nodata != None):
    user_nodata_mech = args.user_nodata[0][0]
    user_nodata_name = args.user_nodata[0][1]
    user_nodata_pass = args.user_nodata[0][2]
#-END-

# --user-admin
if (args.user_admin != None):
    user_admin_mech = args.user_admin[0][0]
    user_admin_name = args.user_admin[0][1]
    user_admin_pass = args.user_admin[0][2]
    data_is_admin = False
else:
    data_is_admin = True
#-END-

# --path
if (args.dir_test != None):
    dir_test = args.dir_test
else:
    dir_test = os.path.dirname(os.path.abspath(__file__))
#-END-

# --browsers
# TODO - find way to test case insentive strings within list
if (args.browsers != None):
    # Firefox
    if ('firefox' in args.browsers[0]) or ('Firefox' in args.browsers[0]):      # if --browser is used and firefox is in list
        firefox = True
    else:                   # if --browser is used and firefox is not in list
        firefox = False
    # Chrome
    if ('chrome' in args.browsers[0]) or ('Chrome' in args.browsers[0]):
        chrome = True
    else:
        chrome = False
else:                       # if --browser is not used
    firefox = True
    chrome = False
#-END-

# --log-level
if (args.log_level != None):
    log_level = args.log_level
else:
    log_level = 'default'
#-END-

# --dwn-geckodriver
if (args.geckodriver_version != None):
    geckodriver_dwn = True
    geckodriver_version = args.geckodriver_version
else:
    geckodriver_dwn = False
    geckodriver_version = "None"
#-END-

# --dwn-chromedriver
if (args.geckodriver_version != None):
    chromedriver_dwn = True
    chromedriver_version = args.chromedriver_version
else:
    chromedriver_dwn = False
    chromedriver_version = "None"
#-END-

# --os
global os_name
global os_bit
if (args.os_name != None):
    # os_name
    if (args.os_name[0][0].lower() == "linux"):
        os_name = "linux"
    elif (args.os_name[0][0].lower() == "windows"):
        os_name = "win"
    else:
        print(os_name[0][0] + " is either not recognised or not supported.")

    # os_bit
    if (args.os_name[0][1] == "32"):
        os_bit = "32"
    elif (args.os_name[0][1] == "64"):
        os_bit = "64"
    else:
        print(os_name[0][1] + "bit system not recognised or supported")
else:
    # os_name
    if (platform.system() == "Linux"):
            os_name = "linux"
    elif (platform.system() == "Windows"):
            os_name = "win"

    # os_bit
    if (platform.machine()[-2:] == "32") or (platform.machine()[-2:] == "86"):
        os_bit = "32"
    elif (platform.machine()[-2:] == "64"):
        os_bit = "64"
    else:
        print(platform.machine()[-2:] + "bit not recognised or not supported. Value taken from platform.machine() = " + platform.machine())
#-END-

# CSS_SELECTOR of Frequently Used Elements
obj_cart_icon = '.glyphicon.glyphicon-shopping-cart'
obj_downloads_icon = '.glyphicon.glyphicon-download-alt'
obj_row_link = 'a[ng-click="grid.appScope.browse(row.entity)"]'


#-------------------------------------------------------------------------------
# Alliases/Shortcuts
#-------------------------------------------------------------------------------

# Donwload and Extract chosen webdriver
def download_webdriver(driver, version, allow_download):
    # Set variables

    # Geckodriver
    if (driver == "geckodriver"):

        if (os_name == "linux"):
            archive_extension = ".tar.gz"
            exc_file = "geckodriver"
        elif (os_name == "win"):
            archive_extension = ".zip"
            exc_file = "geckodriver.exe"

        archive_file = "geckodriver-v" + version + "-" + os_name + os_bit + archive_extension
        url_file = "https://github.com/mozilla/geckodriver/releases/download/v" + version + "/" + archive_file

    # Chromedriver
    elif (driver == "chromedriver"):

        if (os_name == "linux"):
            exc_file = "chromedriver"
            os_bit_chromedriver = os_bit
        elif (os_name == "win"):
            exc_file = "chromedriver.exe"
            os_bit_chromedriver = "32"  # There is no 64bit version of chromedriver

        archive_file = "chromedriver_" + os_name + os_bit_chromedriver + ".zip"
        url_file = "https://chromedriver.storage.googleapis.com/" + version + "/" + archive_file

    archive_path = os.path.join(dir_test, archive_file)

    # Check if executable exists
    print("Checking if " + driver + " executable is present in " + dir_test + ": ", end='')
    if os.path.isfile(os.path.join(dir_test, exc_file)):
        print("Present")
    else:
        print("NOT Present")

        if (allow_download == True):

            # Check if archive file exists
            print("Checking if " + archive_file + " is present in " + dir_test + ": ", end='')
            if (archive_exists(archive_path)):
                print("Present")
            else:
                print("NOT Present")

                # Download archive if not present
                print("Downloading " + url_file + ": ", end='')
                urllib.urlretrieve(url_file, archive_file)
                time.sleep(3)
                print("Done")

                # Extract archived file
                print("Extracting " + archive_file + ": ", end='')
                archive_extract(archive_file)
                print("Done")

        else: # If executable is absent but downloads are disabled
            print("Please Download and extract the " + driver + " excutable to '" + dir_test + "' or add '--" + driver + " VERSION_NUM' to command line.")
#-END-


# Uncompress zip/tarfiles
def archive_extract(filename):
    if (filename.endswith("tar.gz")):
        archive = tarfile.open(filename, "r:gz")
        archive.extractall(dir_test)
        archive.close()
    elif (filename.endswith("tar")):
        archive = tarfile.open(filename, "r:")
        archive.extractall(dir_test)
        archive.close()
    elif (filename.endswith("zip")):
        archive = zipfile.ZipFile(filename, "r")
        archive.extractall(dir_test)
        archive.close()
#-END-

def archive_exists(filename):
    if (filename.endswith("tar.gz") or (filename.endswith("tar"))):
        try:
            if (tarfile.is_tarfile(filename)):
                return True
            else:
                return False
        except:
            return False
    elif (filename.endswith("zip")):
        try:
            if (zipfile.is_zipfile(filename)):
                return True
            else:
                return False
        except:
            return False


# Login as specific user
  # mechanism = String, mnemonic of desired plugin
  # username = String, username of user
  # password = String, password of user
def login(mechanism, username, password):
    logout()

    # Fix case of plugins for drop down on login page
    if (mechanism == "simple"):
        mechanism = (mechanism[:1].upper() + mechanism[1:])
    else:
        mechanism = mechanism.upper()

    element_wait((By.ID, "username"))

    # Select Facility if multiple exist
    if (element_exists('select[id="facilityName"]') == True):
        Select(browser.find_element(By.ID, 'facilityName')).select_by_visible_text(facilty_long_name)

    # Select Plugin if multiple exist
    if (element_exists('select[id="plugin"]') == True):
        Select(browser.find_element(By.ID, 'plugin')).select_by_visible_text(mechanism)

    browser.find_element(By.ID, 'username').send_keys(username)
    browser.find_element(By.ID, 'password').send_keys(password)
    browser.find_element(By.ID, 'login').click()
#-END-

# Logout
def logout():
        browser.get(icat_url + "/#/")   # Return to Home, Topcat saves browse path across multiple users, this should reset it
        time.sleep(1)
        browser.get(icat_url + "/#/logout")
#-END-

def current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#-END-

# Find element by CSS_SELECTOR
  # element = String, CSS_SELECTOR of element
    # non CSS_SELECTOR need full command
def element_find(element):
    return browser.find_element(By.CSS_SELECTOR, (element))
#-END-

# Click element by CSS_SELECTOR
  # element = String, CSS_SELECTOR of element you wish to click on
    # non CSS_SELECTOR need full command
def element_click(element):
    element_find(element).click()
#-END-

# Wait until element exists
  # element = Two arguments, selector and string for selector
    # eg. element_wait((By.ID, 'plugin')) would wait until it found element with 'plugin' as it's id
    # eg. element_wait((By.CSS_SELECTOR, '.glyphicon.glyphicon-shopping-cart')) will wait until cart icon shows
def element_wait(element):
    WebDriverWait(browser, 10).until(EC.presence_of_element_located(element))
#-END-

# Check if element exists, element found by CSS_SELECTOR
  # element = CSS_SELECTOR of element
    # non CSS_SELECTOR need full command
def element_exists(element):
    try:
        element_find(element)
        return True
    except NoSuchElementException:
        return False
#-END-

# Get no. of items in cart
def cart_items():
    return int(re.findall(r'\d+', element_find('span[ng-click="indexController.showCart()"]').text)[0])
#-END-

# Add first element to cart and check it has been added
def cart_add():
    # Get number of items in cart
    if (element_exists(obj_cart_icon)):
        pre_items = cart_items()
    else:
        pre_items = 0

    element_wait((By.CSS_SELECTOR, 'div[ng-click="selectButtonClick(row, $event)"]'))
    element_click('div[ng-click="selectButtonClick(row, $event)"]')

    # Compare no. of items in cart to previous
    try:
        element_wait((By.CSS_SELECTOR, obj_cart_icon))
        time.sleep(1)
        post_items = cart_items()
        if (post_items == (pre_items + 1)):
            return post_items           # If 1 item has been added to cart)
        else:
            return pre_items            # If 1 item has not been added to cart
    except NoSuchElementException as ex:
        print(ex)
#-END-

# Delete first entry in cart
  # Will fail if cart is empty
def cart_rm():
    try:
        pre_items = cart_items()

        if (element_exists('div[class="modal-dialog modal-lg"]') == False):
            element_click(obj_cart_icon)

        element_wait((By.CSS_SELECTOR, 'a[translate="CART.ACTIONS.LINK.REMOVE.TEXT"]'))
        element_click('a[translate="CART.ACTIONS.LINK.REMOVE.TEXT"]')

        time.sleep(1)
        post_items = cart_items()

        if (post_items == pre_items - 1):
            return post_items
        else:
            return pre_items

    except NoSuchElementException as ex:
        print(ex)
#-END-

# Empty Cart
def cart_clear():
    try:
        if (element_exists('div[class="modal-dialog modal-lg"]') == False):
            element_click(obj_cart_icon)

        element_wait((By.CSS_SELECTOR, 'button[translate="CART.REMOVE_ALL_BUTTON.TEXT"]'))
        time.sleep(1)
        element_click('button[translate="CART.REMOVE_ALL_BUTTON.TEXT"]')
        time.sleep(1)
    except NoSuchElementException as ex:
        print("Cart already non-existent")
        print(ex)
#-END-

# Clear downloads
def downloads_clear():
    try:
        # If downloads not already open click downloads icon
        if (element_exists('div[class="modal-content ng-scope"]') == False):
            element_click(obj_downloads_icon)
        time.sleep(1)

        while (element_exists('a[translate="DOWNLOAD.ACTIONS.LINK.REMOVE.TEXT"]') == True):
            element_click('a[translate="DOWNLOAD.ACTIONS.LINK.REMOVE.TEXT"]')
            time.sleep(1)

    except NoSuchElementException as ex:
        print("Downloads already non-existent")
        print(ex)
#-END-

# Click a link and check if directed to correct url
  # element = String, CSS_SELECTOR of element to click
  # target = String, Url the element should take user to (appended after baseurl, eg. '/#/my-data' not 'http://localhost:8080/#/my-data')
def link_check(element, target):
    try:
        element_wait((By.CSS_SELECTOR, element))
        element_click(element)
        time.sleep(1)

        if (browser.current_url == icat_url + target):
            return (txt.Success)
        else:
            return (txt.Failed + " (current url: " + browser.current_url + ")")

    except NoSuchElementException as ex:
        return (txt.Failed + " (link element does not exist)")
        print(ex)
#-END-

# Search for string and check each tab
  # search = String to search for
  # visit = Bool, should the item have results in Visit
  # dataset = Bool, should the item have results in Dataset
  # datafile = Bool, should the item have results in Datafile
def search_test(search, visit, dataset, datafile):

    element_wait((By.ID, "searchText"))
    browser.find_element(By.ID, 'searchText').send_keys(Keys.CONTROL + "a")
    browser.find_element(By.ID, 'searchText').send_keys(search)
    element_click('button[type="submit"]')
    time.sleep(2)

    search_results(search, "Visit", visit)
    time.sleep(1)
    search_results(search, "Dataset", dataset)
    time.sleep(1)
    search_results(search, "Datafile", datafile)
    time.sleep(1)
#-END-

# Check results of search and output results
  # search = String, sting to be searched
  # tab = String, which tabs are you looking in (eg. Visit, Dataset, Datafile)
  # target = Bool,should there be results in the respective tab?
def search_results(search, tab, target):
    print("Search Results for '" + search + "' in " + tab + ": ", end='')

    # element clicked below is not named visit but is named investigation, despite visible text saying visit, so quick name change is declared here
    if (tab == "Visit"):
        tab = "investigation"

    element_click('a[ng-click="searchResultsController.currentTab = \'' + tab.lower() + '\'"]')
    time.sleep(1)

    if (target == True): # If results should exist
        if (element_exists('div[class="ui-grid-cell-contents ng-scope"]') == True): # IF results DO exist
            print(txt.Success + " (Results Exist)")
        else:
            print(txt.Failed + " (Results Do Not Exist)")

    else:        # If results shouldn't exist
        if (element_exists('div[class="ui-grid-cell-contents ng-scope"]') == False):
            print(txt.Success + " (No Results, None Expected)")
        else:
            print(txt.Failed + " (Results Exist, None Expected)")
#-END-

# Click on first item and check if naviagate to correct location
  # level = String, current level of browsing (eg. proposal, investigation, dataset, datafile)
  # target = String, level to navigate to
  # element = String, CSS_SELECTOR of element to click
def browse_click(level, target, element):
    print("Browse " + level + " to " + target + ": ", end='')

    element_wait((By.CSS_SELECTOR, obj_row_link))
    element_click(obj_row_link)
    time.sleep(3)

    if (element_exists('i[translate="ENTITIES.' + target.upper() + '.NAME"]') == True):
        print(txt.Success)
    else:
        print(txt.Failed + " ( Can't find 'ENTITIES." + target.upper() + ".NAME' | on page: " + browser.current_url + ")")
#-END-

# Click non-active section of row and check if info tab appears
  # level = String, current level (eg. Visit, Dataset, Datafile)
  # url = String, url to naviagte to before checking for infotab
def datanav_infotab(level, url):
    print("Info Tab " + level + " Level: ", end='')
    browser.get(url)
    time.sleep(1)

    # Click empty space on row, not link text
        # WARNING this does not guarantee child element (hyperlink) will not be clicked, especially on smaller resolutions
    element_click('div[class="ui-grid-cell-contents ng-binding ng-scope"]')
    time.sleep(1)

    if (element_exists('div[class="ui-grid-row ng-scope"]') == True):
        print(txt.Success)
    else:
        print(txt.Failed + " (Info Tab Not Present)")
#-END-


#-------------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------------

# Test Orginisation
  # These catagories are mainly for organisation and do not affect the code itself, except in naming conventions
    #--URL--
        # Open browser and navigate to url
    #--Login--
        # Attempt to login as specific user
    #--Navigation--
        # Check Interface elements exist and work (eg. browse, search etc.)
    #--Data--
        # Check Data Exists and environment is as expected (eg. url, details popup works)
    #--Data Navigation--
        # Check all data links redirect correctly (eg. clicking visit directs to correct path)
    #--Cart--
        # Check adding to, removing from and clearing cart works as expected
    #--Download--
        # Download via action, https cart and globus. Check everything works as expected (eg. zip rename, download method)
    #--Browsers--
        # Configure and Load each individual browser
    #--Other--
        # Other tests that may need to be added, check silvia's checklist
    #--Master--
        # The function that calls all the others

#---URL---------------------------------------------------------------------

#-Navigate to Topcat home page and check if redirected to login
def test_url():
    print("Load Login Page: ", end='')
    try:
        browser.get(icat_url)
        time.sleep(2)
        if (browser.current_url == icat_url + '/#/login'):
            print(txt.Success + " (" + browser.current_url + ")")
        else:
            print(txt.Failed + " (" + browser.current_url + ")")
    except NoSuchElementException as ex:
        print(txt.Failed)
        print(ex)
#-END-

#---Login-----------------------------------------------------------------------

#-Check that user can login as specific user without error
  # mechanism = String, mnemonic of plugin (lowercase)
  # username = String, username
  # password = String, password
def test_login(mechanism, username, password):
    print("Login Test: ", end='')
    login(mechanism, username, password)

    time.sleep(2)
    if (browser.current_url == icat_home):
        print(txt.Success)
    else:
        print(txt.Failed + " (On page '" + browser.current_url + "')")
#-END-

#---Navigation------------------------------------------------------------------

# Check Nav buttons in top toolbar
def test_nav_toolbar():
    browser.get(icat_home)
    time.sleep(1)

    print("Toolbar About Page Link Test: ", end='')
    print(link_check('a[ui-sref="about"]', '/#/about'))

    print("Toolbar Contact Page Link Test: ", end='')
    print(link_check('a[ui-sref="contact"]', '/#/contact'))

    print("Toolbar Help Page Link Test: ", end='')
    print(link_check('a[ui-sref="help"]', '/#/help'))

    print("Toolbar Home Page Link Test: ", end='')
    print(link_check('a[ui-sref="homeRoute"]', '/#/my-data/' + facilty_short_name))
#-END-

# Check if admin link is present for admin user and is hidden for non-admin user(s)
  # admin = Boolean, is current user admin?
def test_nav_toolbar_admin(admin):
    browser.get(icat_home)
    time.sleep(1)

    if (admin == True):
        print("Toolbar Admin Page Link: ", end='')
        print(link_check('a[ui-sref="admin.downloads"]', '/#/admin/downloads/' + facilty_short_name))
    else:
        print("Toolbar Admin Page Link Hidden: ", end='')
        if (element_find('li[ng-show="indexController.adminFacilities.length > 0"]').get_attribute("class") == "ng-hide"):
            print(txt.Success)
        else:
            print(txt.Failed)
#-END-

# Check footer elements exist
def test_nav_footer():
    print("Footer Existence: ", end='')
    if (element_exists('footer[class="footer"]') == True):
        print(txt.Success)
    else:
        print(txt.Failed)

    # TODO see if it can specified that these must be children of footer element

    print("Footer Facility Link Existence: ", end='')
    try:
        browser.find_element(By.LINK_TEXT, facilty_long_name)
        print(txt.Success)
    except NoSuchElementException:
        print(txt.Failed + " (trying to find: " + facilty_long_name + ")")

    print("Footer Privacy Policy Link Existence: ", end='')
    try:
        browser.find_element(By.LINK_TEXT, 'Privacy Policy')
        print(txt.Success)
    except NoSuchElementException:
        print(txt.Failed)

    print("Footer Cookie Policy Link Existence: ", end='')
    try:
        browser.find_element(By.LINK_TEXT, 'Cookie Policy')
        print(txt.Success)
    except NoSuchElementException:
        print(txt.Failed)

    print("Footer About Us Link Existence: ", end='')
    try:
        browser.find_element(By.LINK_TEXT, 'About Us')
        print(txt.Success)
    except NoSuchElementException:
        print(txt.Failed)
#-END-

# Find and click 'My Data', 'Browse' and 'Search' tabs
def test_nav_tabs():
    browser.get(icat_home)
    time.sleep(1)

    print("Tabs Browse Link Test: ", end='')
    print(link_check('a[translate="MAIN_NAVIGATION.MAIN_TAB.BROWSE"]', '/#/browse/facility/' + facilty_short_name +'/proposal'))

    print("Tabs Search Link Test: ", end='')
    print(link_check('a[translate="MAIN_NAVIGATION.MAIN_TAB.SEARCH"]', '/#/search/start'))

    print("Tabs My Data Link Test: ", end='')
    print(link_check('a[translate="MAIN_NAVIGATION.MAIN_TAB.MY_DATA"]', '/#/my-data/' + facilty_short_name))
#-END-



#---Data------------------------------------------------------------------------

#-Check if Data exists within the datbase
  # data = Boolean, true if user is supposed to have access to testdata
def test_data_exists(data):
    browser.get(icat_home)
    time.sleep(1)

    if (data == True):
        print("Data Existence Test: ", end='')
        if (element_exists(obj_row_link) == True):
            print(txt.Success)
        else:
            print(txt.Failed)
    else:
        print("Data Absence Test: ", end='')
        if (element_exists(obj_row_link) == True):
            print(txt.Failed)
        else:
            print(txt.Success)
#-END-

#-Check that cart does not exist when first logging in
def test_data_cart():
    print("Initial Cart Empty Test: ", end='')
    if (element_exists(obj_cart_icon) == True):
        print(txt.Failed + " (" + element_find('span[ng-click="indexController.showCart()"]').text + ")", end='')

        while (element_exists(obj_cart_icon) == True):
            cart_clear()
            time.sleep(1)

        if (element_exists(obj_cart_icon) == False):
            print(" - Cart Now Empty")
        else:
            print(" - Cart Still Exists")
    else:
        print(txt.Success)
#-END-

#-Check that downloads does not exist when first logging in
def test_data_downloads():
    print("Initial Downloads Empty Test: ", end='')
    if (element_exists(obj_downloads_icon) == True):
        print(txt.Failed, end='')
        downloads_clear()
        time.sleep(1)
        if (element_exists(obj_downloads_icon) == False):
            print(" - Downloads Now Empty")
        else:
            print(" - Downloads still exist")
    else:
        print(txt.Success)
#-END-

#---Data Navigation-------------------------------------------------------------

# Test browse tabs
def test_datanav_browse():
    browser.get(icat_url + '/#/browse/facility/' + facilty_short_name + '/proposal')

    time.sleep(1)
    browse_click("Proposal", "Investigation", obj_row_link)
    # global visit_url
    # visit_url = browser.current_url

    time.sleep(1)
    browse_click("Investigation", "Dataset", obj_row_link)
    global dataset_url
    dataset_url = browser.current_url

    time.sleep(1)
    browse_click("Dataset", "Datafile", obj_row_link)
    global datafile_url
    datafile_url = browser.current_url

    # TODO - Add upwards browsing (eg. click breadcrumb links)
#-END-

def test_datanav_search():
    browser.get(icat_url + "/#/search/start")
    search_visit = "Proposal"
    search_dataset = "Dataset"
    search_datafile = "Datafile"

    # Search that should only have results in Visit
    search_test(search_visit, True, False, False)

    # Search that should only have results in Dataset
    search_test(search_dataset, False, True, False)

    # Search that should only have results in Datafile
    search_test(search_datafile, False, False, True)
#-END-

# Check if info tab show when clicking non active area of items
def test_datanav_infotab():
    datanav_infotab("Visit", icat_home)

    datanav_infotab("Dataset", dataset_url)

    datanav_infotab("Datafile", datafile_url)
#-END-



#---Cart------------------------------------------------------------------------

# Add Dataset and Datafile to cart then clear-
def test_cart_add():

    browser.get(dataset_url)
    time.sleep(2)

    print("Add Dataset to Cart: ", end='')
    if (cart_add() == 1):
        print (txt.Success + " (" + element_find('span[ng-click="indexController.showCart()"]').text + ")" )
    else:
        print (txt.Failed + " (" + element_find('span[ng-click="indexController.showCart()"]').text + ")" )

    time.sleep(3)
    # Click 2nd Dataset, Entire Dataset 1 is already in cart
    browser.find_element(By.LINK_TEXT, 'Dataset 2').click()
    time.sleep(1)

    print("Add Datafile to Cart: ", end='')
    if (cart_add() == 2):
        print (txt.Success + " (" + element_find('span[ng-click="indexController.showCart()"]').text + ")" )
    else:
        print (txt.Failed + " (" + element_find('span[ng-click="indexController.showCart()"]').text + ")" )
#-END-

# Remove 1 item from cart
def test_cart_rm():
    print("Remove Single Item from Cart: ", end='')
    cart_rm()
    time.sleep(1)
    if (cart_items() == 1):
        print(txt.Success + " (" + element_find('span[ng-click="indexController.showCart()"]').text + ")")
    else:
        print(txt.Failed + " (" + element_find('span[ng-click="indexController.showCart()"]').text + ")")
#-END-

# CLear the cart
def test_cart_clear():
    print("Clear Cart: ", end='')
    cart_clear()
    time.sleep(1)

    if (element_exists(obj_cart_icon) == False):
        print(txt.Success)
    else:
        print(txt.Failed + " (" + element_find('span[ng-click="indexController.showCart()"]').text + ")")
#-END-

#---Download--------------------------------------------------------------------

# Download Datafile via action button
# TODO - Add varaible for which file gets selected (By name if possible)
def test_download_action():

    datafile_name = "Datafile 1"

    print("Download By Action: ", end='')
    browser.get(datafile_url)
    time.sleep(1)

    try:
        element_wait((By.CSS_SELECTOR, 'a[translate="DOWNLOAD_ENTITY_ACTION_BUTTON.TEXT"]'))
        element_click('a[translate="DOWNLOAD_ENTITY_ACTION_BUTTON.TEXT"]')

        print(txt.Success)
    except NoSuchElementException as ex:
        print(txt.Failed)
        print(ex)

    print("Downloaded Datafile Exists: ", end='')
    file_datafile = os.path.join(dir_dwn_browser, datafile_name)

    # TODO - Replace with wait-until/timeout
    time.sleep(3)

    if os.path.isfile(file_datafile):
        print(txt.Success + " ('" + datafile_name + "' exists in browser's download directory)")

    else:
        print(txt.Failed + " (" + datafile_name + " does not exist in browser's download directory)")
#-END-

# Download via cart
# TODO check if file exists
# TODO check if download properly added to downloads (eg. download action exists)
def test_download_cart():

    cart_add()
    time.sleep(1)

    # Open Cart
    if (element_exists('div[class="modal-dialog modal-lg"]') == False):
        element_click(obj_cart_icon)

    try:
        # Click 'Downlaod Cart'
        element_wait((By.CSS_SELECTOR, 'button[translate="CART.DOWNLOAD_CART_BUTTON.TEXT"]'))
        time.sleep(1)
        element_click('button[translate="CART.DOWNLOAD_CART_BUTTON.TEXT"]')
    except NoSuchElementException as ex:
        print(ex)

    # Change Download Name
    print("Cart Rename Zip Test: ", end='')
    try:

        zipfile_name = "RENAME_TEST-" + current_time()

        element_wait((By.CSS_SELECTOR, 'input[ng-model="download.fileName"]'))
        browser.find_element(By.CSS_SELECTOR, 'input[ng-model="download.fileName"]').send_keys(Keys.CONTROL + "a")
        browser.find_element(By.CSS_SELECTOR, 'input[ng-model="download.fileName"]').send_keys(zipfile_name)
        print(txt.Success)
    except NoSuchElementException as ex:
        print (txt.Failed)


    # Check https method option availiable
    print("Cart Transport/Access Method 'https' Option Exists: ", end='')
    if (element_exists('option[label="https"]') == True):
        print(txt.Success)
    else:
        print(txt.Failed + " (https method not an option)")

    # Check Globus method option availiable
    print("Cart Transport/Access Method 'globus' Option Exists: ", end='')
    if (element_exists('option[label="globus"]') == True):
        print(txt.Success + " (Note: Download Via Globus not tested)")
    else:
        print(txt.Failed + " (globus method not an option)")


    # Download
    print("Cart Download Via https: ", end='')

    # Select https if not already selected
    Select(element_find('select[ng-model="download.transportType"]')).select_by_visible_text('https')

    # Click 'OK'
    element_wait((By.CSS_SELECTOR, 'button[translate="CART.DOWNLOAD.MODAL.BUTTON.OK.TEXT"]'))
    time.sleep(1)
    element_click('button[translate="CART.DOWNLOAD.MODAL.BUTTON.OK.TEXT"]')
    time.sleep(1)

    # Check if cart hidden
    if (element_exists(obj_cart_icon) == False):
        # Check if downloads has appeared
        if (element_exists(obj_downloads_icon) == True):
            print(txt.Success)
        else:    # Downloads has not appeared
            print(txt.Failed + " (Download icon does not exist)")
    else:    # Cart has not been removed
            print(txt.Failed + " (Cart still exists)")

    # Check If Zip file exists where expected
    print("Downloaded Zip Exists: ", end='')
    file_zip = os.path.join(dir_dwn_browser, zipfile_name)

    # TODO - Replace with wait-until/timeout
    time.sleep(3)

    # It be worth moving this to a repeatable function/method
    if zipfile.is_zipfile(file_zip + ".zip"):
        print(txt.Success + " ('" + zipfile_name + ".zip' exists in browser's download directory)")
    else:
        print(txt.Failed + " ('" + zipfile_name + ".zip' does not exist in browser's download directory)")
#-END-

# Check if download is marked as 'Availiable' is downloads window
def test_download_available():
    print("Download marked as 'Available' in Downloads: ", end='')
    if (element_exists(obj_downloads_icon)):

        # If downloads not already open
        if (element_exists('div[class="modal-content ng-scope"]') == False):
            element_click(obj_downloads_icon)

        time.sleep(1)

        # If Status text Says Availiable
        if (element_find('span[class="ng-binding ng-scope"]').text == "Available"):
            print(txt.Success)
        else:
            print(txt.Failed + "(Download is '" + element_find('span[class="ng-binding ng-scope"]').text + "')")

        # If Download Button exists
        print("Download Button Exists in Downloads: ", end='')
        if (element_exists('a[translate="DOWNLOAD.ACTIONS.LINK.HTTP_DOWNLOAD.TEXT"]') == True) or (element_exists('a[translate="DOWNLOAD.ACTIONS.LINK.GLOBUS_DOWNLOAD.TEXT"]') == True):
            print(txt.Success)
        else:
            print(txt.Failed + " (Download button does not exist)")

    else:
        print(txt.Failed + " (Downloads does not exist)")
#-END-

# Remove all items from downloads
def test_download_clear():
    print("Clear Downloads: ", end='')
    downloads_clear()
    if (element_exists(obj_downloads_icon) == True):
        print(txt.Failed + " (Downloads still exists)")
    else:
        print(txt.Success)
#-END-

#---Browsers--------------------------------------------------------------------

# Setup and run tests fo Firefox
def test_firefox():
    print("")
    print(txt.HEADING + "[ Firefox Test ]" + txt.BASIC)

    download_webdriver("geckodriver", geckodriver_version, geckodriver_dwn)

    # Create Download Directory Under dir_test/Downloads/Timestamp/Browser
    global dir_dwn_browser
    dir_dwn_browser = os.path.join(dir_dwn, "Firefox")
    os.makedirs(dir_dwn_browser)
    print("Firefox Download Directory: " + dir_dwn_browser)

    # Force Firefox to download without prompting user
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.dir', dir_dwn_browser)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/octet-stream')

    # caps = webdriver.DesiredCapabilities.FIREFOX
    # caps["marionette"] = False

    ff_options = FirefoxOptions()
    if (log_level != 'default'):
        ff_options.log.level = log_level
        ff_options.log.path = dir_test + 'geckodriver.log'

    # Create Geckodriver executable workaround if absent - See Notes
    if (os_name == "linux"):
        exc_firefox = os.path.join(dir_test, "gecko.sh")

        print("Checking for geckodriver workaround: ", end='')
        if os.path.isfile(exc_firefox) == False:
            print("NOT present")
            print("Making Geckodriver Workaround (" + exc_firefox + "): ", end='')
            gecko_workaround = open(exc_firefox, "w")
            gecko_workaround.write("#!/bin/bash")
            gecko_workaround.write('\n./geckodriver "$@" --marionette-port 2828')
            gecko_workaround.close()
            os.chmod(exc_firefox, 0777)
            print("Done")
        else:
            print("Present")

    elif (os_name == "win"):
        exc_firefox = os.path.join(dir_test, 'geckodriver.exe')

    # Start Tests
    global browser
    browser = webdriver.Firefox(profile, firefox_options=ff_options, executable_path=exc_firefox)
    test_browser()
    print("Closing Firefox")
    browser.close()
    print(txt.BOLD + "[ Firefox Test Complete ]" + txt.BASIC)
#-END-

# Setup and run tests for Chrome
def test_chrome():
    print("")
    print(txt.HEADING + "[ Chrome Test ]" + txt.BASIC)

    download_webdriver("chromedriver", chromedriver_version, chromedriver_dwn)

    # Create Download Directory Under dir_test/Downloads/Timestamp/Browser
    global dir_dwn_browser
    dir_dwn_browser = os.path.join(dir_dwn, "Chrome")
    os.makedirs(dir_dwn_browser)
    print("Chrome Download Directory: " + dir_dwn_browser)

    chrome_options = ChromeOptions()
    # if (log_level != 'default'):
    #     chrome_options.log.level = log_level

    chrome_prefs = {"download.default_directory" : dir_dwn_browser}
    chrome_options.add_experimental_option("prefs", chrome_prefs)

    if (os_name == "linux"):
        exc_chrome = os.path.join(dir_test, "chromedriver")
    elif (os_name == "win"):
        exc_chrome = os.path.join(dir_test, 'chromedriver.exe')

    os.chmod(exc_chrome, 0777) # Sometimes chromedriver isn't automatically executable, this fixes that

    #Start Tests
    global browser
    browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=exc_chrome)
    test_browser()
    print("Closing Chrome")
    browser.close()
    print(txt.BOLD + "[ Chrome Test Complete ]" + txt.BASIC)
#-END-

# TODO - Add support for more browsers (eg. Chromium, Edge, Safari)

#---Other-----------------------------------------------------------------------

# Output useful variables for debuging
def print_variables():
    print("")
    print(txt.HEADING + "[ Gathering Variables ]" + txt.BASIC)

    # OS
    print("OS: " + os_name + os_bit + " (If this is incorrect, you can overide it, see '--help')")

    # URL
    print("URL: " + icat_url)

    # Facilty
    print("Facility: " + facilty_short_name + "(" + facilty_long_name + ")")

    # Root User
    print("Data User: " + user_data_mech + "/" + user_data_name)
    print("Data User Password: " + user_data_pass)

    # Non Root User
    print("No Data User: ", end='')
    if (args.user_nodata != None):
        print(user_nodata_mech + "/" + user_nodata_name)
        print("No Data User Password: " + user_nodata_pass)
    else:
        print("NULL")

    # Admin User
    print("Admin User: ", end='')
    if (args.user_admin != None):
        print(user_admin_mech + "/" + user_admin_name)
        print("Admin Password: " + user_admin_pass)
    else:
        print("Same as Data User")

    # Virtual Display
    if (args.virtual_display == True):
        w = 1920
        h = 1080
        display = Display(visible=0, size=(w, h))
        display.start()
        print("Virtual Display Used (" + str(w) + "x" + str(h) + ")")
    else:
        print("Virtual Display Not Used")

    # Directory
    print("Testing Directory: " + dir_test)
    print("Download Directory: " + dir_dwn)

    # Browsers
    print("Browsers: ", end="")
    if (firefox == True):
        print("Firefox ", end="")
    if (chrome == True):
        print("Chrome ", end="")
    print("")

    # Log Level
    print("Log Level: " + log_level)

    # Geckodriver
    if (firefox == True):
        print("Geckodriver: ", end='')
        if (args.geckodriver_version != None):
            print(geckodriver_version)
        else:
            print("Already present (version unknown)")
    #-END-

    # Chromedriver
    if (firefox == True):
        print("Chromedriver: ", end='')
        if (args.chromedriver_version != None):
            print(chromedriver_version)
        else:
            print("Already present (version unknown)")


    # Newline
    print(txt.BOLD + "[ Gathering Variables Complete ]" + txt.BASIC)
    #---
#-END-
#-END-

#---Master----------------------------------------------------------------------

# List of tests to run for each user
def test_browser():
    #--Browser--
    test_url()
    print("")

    # User with access to testdata
    print(txt.SUBHEADING + '[ Data User Test ]' + txt.BASIC)
    #---Login--
    test_login(user_data_mech, user_data_name, user_data_pass)
    #--Navigation--
    test_nav_toolbar()
    test_nav_toolbar_admin(data_is_admin)   # data_is_admin = Boolean defined in arguments above
    test_nav_footer()
    test_nav_tabs()

    #--Data--
    test_data_exists(True)
    test_data_cart()
    test_data_downloads()
    #--Data Navigation--
    test_datanav_browse()
    test_datanav_search()
    test_datanav_infotab()
    #--Cart--
    test_cart_add()
    test_cart_rm()
    test_cart_clear()
    #--Download--
    test_download_action()
    test_download_cart()
    test_download_available()
    test_download_clear()
    #--Other--
    #--Finish--
    logout()
    print("Logging Out")

    # User without access to test date (if included in CLI args)
    if (args.user_nodata != None):
        print("")
        print(txt.SUBHEADING + '[ No-Data User Test ]' + txt.BASIC)
        test_login(user_nodata_mech, user_nodata_name, user_nodata_pass)
        #---Nav---
        test_nav_toolbar_admin(False)
        #--Data--
        test_data_exists(False)
        test_data_cart()
        test_data_downloads()
        #--Finish--
        logout()
        print ("Logging Out")
        print("")

    # User with admin access (if not same as User with data)
    if (args.user_admin != None):
        print("")
        print(txt.SUBHEADING + '[ Admin User Test ]' + txt.BASIC)
        test_login(user_admin_mech, user_admin_name, user_admin_pass)
        test_nav_toolbar_admin(True)
        logout()
        print ("Logging Out")
        print("")
#-END-

# Master function
def test_master():
    global dir_dwn
    dir_dwn = os.path.join(dir_test, "Downloads", current_time())

    print_variables()

    if (firefox == True):
        test_firefox()

    if (chrome == True):
        test_chrome()

    print("")
    # TODO - count errors and exit if failed
    print( txt.GREEN + "Test Complete" + txt.BASIC)
#-END-

#-------------------------------------------------------------------------------
# Runtime
#-------------------------------------------------------------------------------

# Made with (http://patorjk.com/software/taag/#p=display&f=Big&t=TopCat%20Selenium)
print("---------------------------------------------------------------------------------")
print("  _______           _____      _      _____      _            _                  ")
print(" |__   __|         / ____|    | |    / ____|    | |          (_)                 ")
print("    | | ___  _ __ | |     __ _| |_  | (___   ___| | ___ _ __  _ _   _ _ __ ___   ")
print("    | |/ _ \| '_ \| |    / _` | __|  \___ \ / _ \ |/ _ \ '_ \| | | | | '_ ` _ \  ")
print("    | | (_) | |_) | |___| (_| | |_   ____) |  __/ |  __/ | | | | |_| | | | | | | ")
print("    |_|\___/| .__/ \_____\__,_|\__| |_____/ \___|_|\___|_| |_|_|\__,_|_| |_| |_| ")
print("            | |                                                                  ")
print("            |_|                                                                  ")
print("---------------------------------------------------------------------------------")

test_master()
