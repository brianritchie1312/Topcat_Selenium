TopCat Selenium
===============

Summary
-------

This script is designed to automatically test the topcat interface by opening a browser and simulating a virtual user clicking on various elements. The script outputs a list of tests and their outcomes, this output can then be used by TravisCI or similar tool to pass/fail a build.

The basic steps of the script are:

1. Print large ASCII art letters spelling "TopCat Selenium", just because it looks nice.

2. Gather arguments and variables and prints them out for debugging help.

3. Checks if webdriver executable exists for browser, downloads and extracts if it doesn't and the script has been authorized to (see arguments).

4. Create time stamped download directory for browser, eg. `./Downloads/2018-01-16_10-34-15/Chrome/`.

5. Launches the browser and navigates to the specified URL.

6. Login as specified Data User and run data user tests and admin user tests if admin user unspecified. User tests listed under `test_browser()`.

7. Login as No-Data User if specified and run no-data user tests.

8. Login as Admin User if specified and run admin user tests.

9. Close Browser

10. Run steps 3-7 again for each enabled and supported browser.

11. Closes script.


How to Use
----------

1. Install dependencies below.

2. Download or Clone this repo.

3. Navigate into directory

4. Run the script like a normal python script. See arguments below to correctly configure.
    ```Shell
    python topcat_selenium_test.py --url http://localhost:8080 --user-data simple root admin
    ```


Dependencies
------------
*NOTE - The exact version compatibilities still need to be tested/documented but using the latest stable version of each should be fine)*

* Windows, Linux or OSX

* Python 2.7 (Should also work with 3.0+ but not tested)

* [Selenium](http://www.seleniumhq.org/)
  ```Shell
  pip install selenium
  ```

* At least one or more of these browsers installed:
  * [Mozilla Firefox](https://www.mozilla.org/en-GB/firefox/new/)
    * Requires [Geckodriver](https://github.com/mozilla/geckodriver/releases) executable in test directory (installed by script if argument used, see Arguments below)
  * [Google Chrome](https://www.google.co.uk/search?q=chrome&ie=utf-8&oe=utf-8&client=firefox-b&gfe_rd=cr&dcr=0&ei=lB5eWtaeJKbS8AeC06-AAQ)
    * Requires [Chromedriver](https://sites.google.com/a/chromium.org/chromedriver/) executable in test directory (installed by script if argument used, see Arguments below)
  * [Chromium](https://www.chromium.org/Home)
    * Also requires [Chromedriver](https://sites.google.com/a/chromium.org/chromedriver/) executable in test directory (installed by script if argument used, see Arguments below)

*Note: As of 24th Jan 2018, the current versions of chrome/chromium seem incompatible with most recent chromedriver 2.3x version (2.35). If 2.36 has not yet been released, use older versions of chrome/chromium*


* If a standard GUI is unavailable:
  * xvfb
    ```Shell
    sudo apt-get install xvfb
    OR
    sudo yum install xorg-x11-server-Xvfb
    ```
  * [pyvirtualdisplay](https://pypi.python.org/pypi/PyVirtualDisplay)
    ```Shell
    pip install pyvirtualdisplay
    ```


* A working TopCat/ICAT *(see [icat.ansible](https://github.com/JHaydock-Pro/icat.ansible))* with:
    * A URL accessible by the machine this script is running on
    * At least one Facility
    * At least one authentication plugin
    * At least one user with access to data containing:
      * At least one investigation/visit
      * At least two datasets in the same investigation/visit
      * At least one datafile in each of those datasets named 'Datafile1' (name can be changed under `test_download_action()` if need)
      * Those datafiles must exist in the location specified in the icat database



Arguments
---------

This script has a few command line arguments.

| Option                                          | Required? | Example                             | If Not Used                           | Function                                                                                  |
|:-----------------------------------------------:|:---------:|:-----------------------------------:|:-------------------------------------:|:-----------------------------------------------------------------------------------------:|
| --url {url}                                     | Yes       | --url http://localhost:8080         | Throws Error                          | The url and port number of the topcat interface.                                          |
| --fac-short {facility}                          | No        | --fac-short LILS                    | 'LILS' used                           | The short name of the facility, used in URLs.                                             |
| --fac-long {facility}                           | No        | --fac-long Lorum Ipsum Light Source | 'Lorum Ipsum Light Source' used       | The long name of the facilty, used in text elements.                                      |
| --user-data {mechanism} {username} {password}   | Yes       | --user-data simple root pass        | Throws Error                          | The plugin, username and password of the user with access to the testdata.                |
| --user-nodata {mechanism} {username} {password} | No        | --user-nodata db root password      | No-Data User Tests Ignored            | The plugin, username and password of the user without access to the testdata.             |
| --user-admin {mechanism} {username} {password}  | No        | --user-admin simple root pass       | Data User assumed to be admin         | The plugin, username and password of the admin user.                                      |
| --virtual-display			                          | No        | --virtual-display                   | Standard GUI used                     | Creates a virtual display with pyvirtualdisplay. Use if standard GUI is unavailiable.     |
| --path {path}                                   | No        | --path /home/user1/tests            | Script's current directory used       | Directory where webdriver excutables are and files will be downloaded to.                 |
| --browsers {browser1} {browser2} ...            | No        | --browsers firefox chrome           | Only firefox tested                   | List of browsers to test. (Supported: firefox, chrome, chromium)                                    |
| --log-level {loglevel}                          | No        | --log-level trace                   | Default log level used                | Log level of webdrivers. Currently only geckodriver.log (firefox webdriver) is modified.  |
| --geckodriver {version number}                  |Recommended| --geckodriver 0.19.1                | Assumes geckodriver already present   | Downloads and extract specified version of geckodriver (firefox webdriver) if not present.|
| --chromedriver {version number}                 |Recommended| --chromedriver 0.19.1               | Assumes chromedriver already present  | Downloads and extract specified version of chromedriver if not present.                   |
| --os {name} {bits}                              | No        | --os linux 64                       | Script attempts to gather info itself | Sometimes the script incorrectly assumes the OS and architecture, if this happens the wrong webdriver could be downloaded. Using this, the script ignores what python thinks it's running on and downloads the version specified by the argument. |
| --on-fail {action}                              | No        | --on-fail print                     | Print is used                         | If a task fails it will either PRINT (print 'Failed' and move on) or EXIT (close browser and return exit code 1) |
| --no-ansi                                       | No        | --no-ansi                           | ANSI escaping is used to colour output| Some consoles/terminals don't support ANSI escaping, using this will remove ANSI to clean up ouput |

Notes
-----

* There is currently a [bug](https://bugzilla.mozilla.org/show_bug.cgi?id=1421766) with geckodriver that making it impossible to specify the marionette port within the script itself. The workaround for this is to port the script towards an executable shell script containing the path to geckodriver and the marionette port argument. The script currently creates this script automatically on Linux systems but this will likely be fixed in future so a version check to skip this step should be implemented.
* If the scripts fails or is killed, you may need to close/kill the browser and it's webdriver manually before re-launching.
* If the script downloads the wrong webdriver (eg. 32bit instead of 64bit) then you should delete the executable add the `--os {name} {bits}` argument and run again or manually download and extract the correct version.
* There is no 64bit windows version of chromedriver so the script downloads 32bit version for windows regardless of the system or user override.
* Only some versions of chromedriver have 32bit linux versions, so double check versions.
* For use in IDEs or environments without CLI arguments, there is a block at the end of the arguments section with example arguments, uncomment it (and comment out `args = parser.parse_args()`), modify the arguments as you wish then run.
* Chrome (64.0.3282.119) does not work with chromedriver 2.35 or any version (as of 26/01/18) so you will have to use an older version of chrome or skip chrome


Organization of script
----------------------

The script is organized in a particular way for ease of reading.

#### Notes
Contains comments and a todo list.
#### Imports
Contains all the imported modules the script needs.
#### Arguments
Contains all the command line arguments
#### Variables
Gathers arguments and other variables and declares them here. Most global variables are here.
#### Shortcuts
Methods/functions used in multiple places in the code, using returning another variable or performing basic task
#### Tests
These are the tests run by each user. There split into several categories:
* URL
* Login
* Navigation
* Data
* Data Navigation
* Cart
* Download
* Browsers
* Other
* Master

All tests not under browser, other or master should be found and run in `test_browser()` which itself is under master

#### Runtime
Initiate Tests.

Common Errors
-------------

If the script keeps returning errors, the first that might be worth trying is killing all instances of:
* pyvirtualdisplay
* Xvfb
* firefox
* geckodriver
* marionette
* google-chrome
* chromedriver

Sometimes failures leave these processes running in the background, this sometimes causes problems.

Try using this system.
```Shell
pstree -Aaup | grep firefox
kill <process ID>
```
You can use something like `killall firefox` but this can be dangerous.

With GUI just use task manager or OS equivalent.


#### Something about 'marionette' or " Web element reference not seen before:"

Something is probably using port 2828, often the webdriver is still running in the background from a prior, failed test so kill it with task manager or try using:
```Shell
netstat -tulpn | grep 2828
```
If the process using port 2828 is firefox/marionette/geckodriver, kill it then run the script again.

If you need port 2828 for something else, change the port number in `gecko.sh` or under `test_firefox()`.


#### "Unable to find a matching set of capabilities"
You probably have the wrong version of geckodriver/chromedriver for your system architecture.

  1. Delete the geckodriver/chromedriver executables
  2. Check if you are on 32bit or 64bit
  3. Add `--os {name} {bits}` to command line. OR download and extract the correct version into the testing directory, the script will then use that one.

*NOTE: There are no Windows 64bit versions of chromedriver, use 32bit.*

If this still persists, check your browser version against webdriver version and notes on webdriver page.


#### "geckodriver/gecko.sh/chromediver needs to be in system PATH"

It doesn't but you are probably missing either the executable or the `executable_path=exc_firefox` argument from the `brower = webdriver.Firefox()` line under `test_firefox()` or the chrome version under `test_chrome()`. The 'exc_firefox/exc_chrome' variables should be declared a few lines above this.


#### Test says 'Failed' even when the element/file it's searching for actually does exist
Open the script, find `base_sleep_time` and incease it's value. This is the number of seconds most tests will wait before checking if the element has loaded. Slow machines or slow networks may need more time to load the elements or download the file.

If problem still occurs, double check the element selector/filename strings.

#### Browser hangs after opening and does nothing
This one annoyed me for a while. A new update for chrome didn't work with any version of chromedriver. So if you experience a similar problem, check version numbers of both drivers and browsers against each other in the notes of webdriver download page. Check when the most recent update of the browser was released, if it's less than a week or two, you may have to reinstall an older browser or just wait for the driver to be updated.

A Chrome/Chromium Update some time just before 24th Jan 2018 broke version 2.35 of Chromedriver, so if 2.36 hasn't been released yet, try installing older versions of chrome/chromium.

#### Something about 'Exec'
The executable for your chosen browser might not be in PATH or the binary_location option is pointing to wrong location or missing.
Look in `test_firefox()` ot `test_chrome()`, the line will be something like:
```
chrome_options.binary_location = "PATH"
```
If it's missing or has an incorrect PATH, correct it.


TODO
----

* Tests
  * Upwards browsing (eg. datafile -> dataset -> investigation) to Data Navigation tests
  * More detail in `test_datanav_infotab()` (eg. check each tab, compare displayed meta data)
  * More detail in `test_datanav_search()` (eg. test tickboxes)
  * Unzip cart download and check contents
  * Check metadata of downloaded file instead of just it's existence
* Support
  * Android
  * Improve OS and Architecture detection
  * Conditional skip geckodriver workaround when fix released
  * Python3
* Technical Improvements
  * Use Appropriate wait_until() instead of time.sleep(x)
  * Wait until file exists (with timeout) instead of time.sleep(x) on `test_download_action()`
  * If possible, install dependencies within script
* User Improvements
  * Progress bars
  * Optional verbose output (eg. include def names)
  * Log files
  * Single letter arguments
  * Use quotes on CLI arguments to support items with whitespaces.



Version Numbering
-----------------

This could well be a temporary measure to be replaced by a more standardized system when the script is ready for proper use.

Version number format:

`Year.Month.Day.Number`

`YY.MM.DD.XX`

For example:

`18.01.22.00` is the first version of 22/01/2018.

`18.01.22.01` is the second.

`18.01.22.02` and so on.

`18.01.23.00` is the first of 23/01/2018.

This should ensure the newest version is always at the top of the tag list.


Missing Tests
-------------

These are tests that are not included within the current version and are unlikely to be added anytime soon

* Support for IE, Edge, Safari and other OS specific browsers
* Globus testing due to need for extra setup
* Maximum filesize/file limits for carts due to limited space and bandwidth in VMs and travis
* Email notifications due to need to setup up email that can be read by script (especially when many email services are designed to prevent bots using them)

Changelog
---------

##### 18.02.02.00
* Fixed Chromium output saying 'Closing Chrome'

##### 18.01.29.03
* Fixed Chromium not showing in printed variable list
* All time.sleep(x) lines now use time.sleep(base_sleep_time + x) allowing users to slow down test if needed with one change. Eg. slow machines or networks.

##### 18.01.29.02
* Improved os_name and browsers if statments with arrays and .lower attributes to allow more options on fewer lines. For example lists of possible strings users (or platform.system()) could use to identify the OS are checked against actual entered/returned string with .lower() attribute applied. So if the user enters "WiNdOwS", it will still store as "win" for later in script. This is better than an OR for every possible string.
* Improved README

##### 18.01.29.01
* Add Chromium support
* Minor fixes to auto detecting mac systems

##### 18.01.29.00
* Corrected os_name error for windows
* Corrected extracting web driver when compressed file exists but has not been extracted

##### 18.01.26.04
* Fixed --no-ansi to prevent it always being in effect

##### 18.01.26.03
* Added -no-ansi argument for consoles/terminals without ANSI escaping

##### 18.01.26.02
* Replaced CTRL/CMD+A with .clear()

##### 18.01.26.01
* Added MAC support
* CTRL+A replaced with variable to allow using CMD+A on mac or custom key binding

##### 18.01.26.00
* Added txt.BASIC to end of final print to prevent entire terminal turning green

##### 18.01.25.00
* Added foundations of Mac support

##### 18.01.24.01
* Slight modification to download_webdriver() output

##### 18.01.24.00
* Improved README
* Added fail counter

##### 18.01.22.03
* Script now closes webdrivers after tests complete or Failed return. This should reduce errors.

##### 18.01.22.00
* Corrected missing success output on toolbar test

##### 18.01.19.04
* Corrected version numbering

##### 18.01.19.00
* Minor corrections

##### 18.01.18.00
* Fixed on_fail being undefined if argument not used

##### 18.01.17.00
* Added fail argument, users can choose what happens when a task fails. PRINT will print 'Failed' then carry on, EXIT will stop the script
* Add version numbering

##### 16/01/2018(2)
* Moved `test_nav_search()` to `test_datanav_search()`
* Moved OS variable print to `print_variables()`
* Added geckodriver/chromedriver print to `print_variables()`

##### 16/01/2018
* Separated from ICAT-Ansible
* Created Readme                                                              
