# edx-discussion board crawler

**edx-discussion board crawler** is a Python-based cross-platform tool for mining text data from discussion threads of the enrolled [edX](www.edx.org) courses available on a user's dashboard. THe edx discussion board is a dynamic page, thus we utilize the webdriver and selenium API to scrape the content. It was developed by teaching assistants at Tokyo Tech Online Education Development Office.

## Prerequisites
Python libraries and modules:

* [Python](https://www.python.org/downloads/) - version 3.5+
* [Selenium with Python](https://selenium-python.readthedocs.io/) - API to access webdriver
* [Chrome webdriver](http://chromedriver.chromium.org/downloads) - Chrome webdriver which requires the installation of official Chrome brower.  
## How to run

1) Run a python script `edx-discussion.py` 

	python edx-discussion.py 

2) input your edX user and password at terminal, and press enter.
3) The chromedriver will be opened and attempt to log-in into edX dashboard
4) You will be asked how many courses you want to crawl, enter number and press enter
5) The terminal will return list of courses in your dashboard together with respective course index, enter course index and press enter
6) the crawler starts
	
The output is a JSON file ('all_dis.json'), which is stored by default in "HTMLs\[COURSE_NAME]" folder .


## Extra files and folders
[DATETIME]_selected_file.csv contain the list of selected courses for crawling 
[DATETIME]_logfile_discussion.csv is the log file

