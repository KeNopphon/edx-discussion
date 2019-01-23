from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from six.moves import html_parser
from tqdm import tqdm

import pandas as pd
import traceback
import errno
import time
import webbrowser
import html
import string
import re
import json
import os
import getpass
import sys
import csv

#geckodriver.exe
#chromedriver.exe


chrome_options = Options()  
chrome_options.add_argument("--log-level=3")  # fatal 
chrome_options.add_argument('--disable-gpu')
#####  headless mode #####
'''
chrome_options.add_argument('--headless')
chrome_options.add_argument('--hide-scrollbars')
chrome_options.binary_location = 'C:/Users/lord_/AppData/Local/Google/Chrome SxS/Application/chrome.exe'  
#############################
'''
driver_loc = './chromedriver.exe'
#driver = webdriver.Chrome(executable_path=driver_loc)
driver = webdriver.Chrome(executable_path=driver_loc,chrome_options=chrome_options)
#driver = webdriver.Firefox(executable_path=driver_loc)

usr = input('username(email): ')
pwd = getpass.getpass(prompt='password: ',stream=sys.stderr)

def log_in(usr,pwd):
	sign_in_url="https://courses.edx.org/login?next=/dashboard"
	
	

	driver.get(sign_in_url)
	time.sleep(2)
	driver.find_element_by_id("login-email").send_keys(usr)
	driver.find_element_by_id("login-password").send_keys(pwd)

	signInButton = driver.find_element_by_class_name("login-button").click()





def load_thread():

	time.sleep(2)

	while(1):
		time.sleep(2)
		try:
			loadmore = driver.find_element_by_class_name('forum-nav-load-more').click()
		except StaleElementReferenceException:
			continue
		except (NoSuchElementException):
			#w_flag-=1
			#if w_flag <0:
			break
	return driver.find_elements_by_class_name("forum-nav-thread")


def load_response():
	
	while(1):
		try:
			loadmore = driver.find_element_by_class_name("loading-animation") 
		except NoSuchElementException:
			break  

def load_comment(cur_obj):
	load_comment_btns = cur_obj.find_elements_by_xpath('//*[@class="btn-link action-show-comments"]')
	for btn in load_comment_btns:
		try:
			btn.click()
		except ElementNotVisibleException:
			continue
		
def list_dash_course():
	WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "course-container")))
	print('successfully logged in')
	time.sleep(2)
	courses = driver.find_elements_by_class_name("course-container") 
	course_list = []
	print('extracted ',len(courses) ,  ' courses name and link in dashboard')
	for course in courses:
		c_name =course.find_element_by_class_name('course-title').text
		c_url = course.find_element_by_css_selector('a').get_attribute('href')
		course_list.append({'name':c_name, 'url':c_url}) 
	
	return course_list

def clean_filename(s, minimal_change=False):
	"""
	Sanitize a string to be used as a filename.
	If minimal_change is set to true, then we only strip the bare minimum of
	characters that are problematic for filesystems (namely, ':', '/' and
	'\x00', '\n').
	"""

	# First, deal with URL encoded strings
	h = html_parser.HTMLParser()
	s = html.unescape(s)

	# strip paren portions which contain trailing time length (...)
	s = (
		s.replace(':', '-')
		.replace('/', '-')
		.replace('\x00', '-')
		.replace('\n', '')
	)

	if minimal_change:
		return s

	s = s.replace('(', '').replace(')', '')
	s = s.rstrip('.')  # Remove excess of trailing dots

	s = s.strip().replace(' ', '_')
	valid_chars = '-_.()%s%s' % (string.ascii_letters, string.digits)
	return ''.join(c for c in s if c in valid_chars)


def find_response_user(response_obj):
	#res_list = response_obj.find_elements_by_xpath('//*[@class="response-header-content"]')
	#total_res.append(response_obj.find_element_by_xpath('//*[@class="response-header-content"]/*[@class="username"]').text)
	#comment_list= response_obj.find_elements_by_xpath('//*[@class="comments"]//*[@class="posted-details"]')
	#comment_list= response_obj.find_elements_by_xpath('//*[@class="comments"]//*[@class="posted-details"]//*[@class="username"]')
	total_res = []
	user_list = response_obj.find_elements_by_class_name("username")
	for user in user_list:
		total_res.append(user.text)
			
	return (total_res)

def find_response_timestamp(response_obj):
	total_res = []

	timestamp_list = response_obj.find_elements_by_class_name('timeago')
	for timestamp in timestamp_list:
		total_res.append(timestamp.get_attribute('title'))
			
	return total_res



def find_response_user_role(response_obj):
	
	total_res_role = []
	res_nameroletypedate = response_obj.find_element_by_class_name("response-header-content").text
	cmt_nameroletypedate = response_obj.find_elements_by_class_name("posted-details")
	response_role = find_role(res_nameroletypedate)
	total_res_role.append(response_role)
	if len(cmt_nameroletypedate) > 1:
		comments_obj = response_obj.find_elements_by_class_name("posted-details")[1:]
		for comment_nameroletypedate in comments_obj:
			comment_role = find_role(comment_nameroletypedate.text)
			total_res_role.append(comment_role)
			
	return (total_res_role)    

def find_role(string):
	set_role = ['Community TA','Staff']
	for role in set_role:
		if re.search(role,string):
			return(role)
	return('n/a')

def crawl_discussion(cat_name,total_cat,cat_index,prev_idx):
	
	thread_list = load_thread()
	tmp_post_dict = dict()
	if not thread_list:
		print('no thread in this category')

	for idx in tqdm(range(len(thread_list))):
		thread = thread_list[idx]
		WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "forum-nav-thread-list-wrapper")))    
		#thread_no = thread.get_attribute('data-id')
		#thread_located=WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@class="forum-nav-thread" and @data-id ="'+thread_no+'"]')))
		handling_click_cat(thread)      
		load_response()

		post_obj = driver.find_element_by_class_name("discussion-post")  
		try:
			post_user = driver.find_element_by_xpath('//*[@class="posted-details"]/a[@class="username"]').text
			nameroletypedate = driver.find_element_by_xpath('//*[@class="posted-details"]').text
			post_user = driver.find_element_by_xpath('//*[@class="posted-details"]/a[@class="username"]').text
			post_user_role = find_role(nameroletypedate)
		except:
			post_user = 'anonymous'
			post_user_role = 'n/a'
		

		post_timestamp = driver.find_element_by_xpath('//*[@class="post-header-content"]/p[@class="posted-details"]/span[@class="timeago"]').get_attribute('title')
		post_type = driver.find_element_by_xpath('//*[@class="posted-details"]').text.split(' ')[0]
		post_title = post_obj.find_element_by_class_name("post-title").text
		post_body = post_obj.find_element_by_class_name("post-body").text


		res_obj_list = driver.find_elements_by_xpath('//*[@class="responses js-marked-answer-list" or @class="responses js-response-list"]/li')
		res_timestamp =  dict()
		res_user_role = dict()
		res_content = dict()
		res_user = dict()

		no_res = 0
		for r_idx, res_obj in enumerate(res_obj_list):
			tmp_res = []
			load_comment(res_obj)
			tmp_text_obj = res_obj.find_elements_by_class_name("response-body")
			for tmp_text in tmp_text_obj:
				tmp_res.append(tmp_text.text)
				no_res+=1
			
			tmp_res_user = find_response_user(res_obj)
			tmp_res_timestamp = find_response_timestamp(res_obj)   
			tmp_res_user_role = find_response_user_role(res_obj)

			res_content.update({"responses_"+str(r_idx+1).zfill(2):tmp_res})
			res_user.update({"responses_"+str(r_idx+1).zfill(2):tmp_res_user})
			res_user_role.update({"responses_"+str(r_idx+1).zfill(2):tmp_res_user_role})
			res_timestamp.update({"responses_"+str(r_idx+1).zfill(2):tmp_res_timestamp})
		thread_index = prev_idx+idx+1
		post_content = {'post_category':cat_name,'post_timestamp':post_timestamp,'type':post_type,'title':post_title,'post_content':post_body,'post_user':post_user,'post_user_role':post_user_role,'response':res_content,'response_user':res_user,'response_user_role':res_user_role,'response_timestamp':res_timestamp,'No_response':no_res} 
		tmp_post_dict.update({str(thread_index).zfill(4):post_content})
		#print('crawling at thread NO. {} of discussion category NO: {} / {} \r'.format(thread_index,cat_index+1,total_cat),end='')

		
	return tmp_post_dict

def handling_click_cat(webdriver_obj):
	while(1):
		try:
			webdriver_obj.click()
			break
		except WebDriverException:
			time.sleep(2)
		except Exception as e:
			print(e)


def access_discussion(course_name,course_url): 
	post_dict = dict()
	driver.get(course_url)
	WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "navbar-nav")))
	driver.find_element_by_xpath('//*[@class="nav-item " or @class="nav-item active"]//*[contains(text(), "Discussion")]').click()
	discuss_cat_list,cat_name_list = fileter_duolicate_category()
	print('begin crawling course: {}'.format(course_name))
	prev_idx = 0
	total_cat = len(cat_name_list)
	for cat_index,(cat,cat_name) in enumerate(zip(discuss_cat_list,cat_name_list)):

		handling_click_cat(cat)
		print('crawling {}/{} categories'.format(cat_index+1,len(discuss_cat_list)))
		tmp_post_dict= crawl_discussion(cat_name,total_cat,cat_index,prev_idx)
		post_dict.update(tmp_post_dict)
		prev_idx = len(post_dict)
		

		driver.find_element_by_xpath('//*[@class="btn-link all-topics"]').click()
		WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@class="forum-nav-browse-menu-item"]//*[@class="forum-nav-browse-title"]')))


	print('finished crawling')
	course_path = os.path.join('HTMLs',clean_filename(course_name))
	mkdir_p(course_path)
	dict2json = json.dumps(post_dict, sort_keys=True, indent=4, separators=(',', ': '))

	with open(os.path.join(course_path,'all_dis.json'),'w',encoding='utf-8') as f:
		f.write(dict2json)
	print('write discussion to file:',os.path.join(course_path,'all_dis.json') )

def fileter_duolicate_category():
	WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "discussion-body")))
	while(True):
		discuss_cat_list = driver.find_elements_by_xpath('//*[@class="forum-nav-browse-menu-item"]//*[@class="forum-nav-browse-title"]')
		cat_name_list = [cat.text.split(',\n') for cat in discuss_cat_list]

		if [''] not in cat_name_list:
			break

	print('number of categories before filter: ',len(cat_name_list))
	outer_layer_cat = [i[0] for i in cat_name_list if len(i) > 1]
	filter_out_list = []
	for idx,cat_name in enumerate(cat_name_list):
		if len(cat_name) == 1 and cat_name[0] in outer_layer_cat:
			filter_out_list.append(cat_name_list[idx])
			del discuss_cat_list[idx]
			del cat_name_list[idx]
			
		
		
	print('number of categories after filter: ', len(cat_name_list))
	print('list of crawled categories')
	print(*cat_name_list,sep='\n') 
	return discuss_cat_list,cat_name_list

	

		
def mkdir_p(path, mode=0o777):
	"""
	Create subdirectory hierarchy given in the paths argument.
	"""
	try:
		os.makedirs(path, mode)
	except OSError as exc:
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else:
			raise

def course_selection(course_list):
	
	
	chosen_no = int(input('enter number of courses (type 9999 for crawling every course)'))
	chosen_idx =[]
	if chosen_no == 9999:
		return course_list
 
	print ('list of courses in dashboard')
	
	df = pd.DataFrame(course_list).sort_values('name')

	for course,idx in zip(df.name,df.index):
		print (str(idx).ljust(5) +' : ' + course)
	array_c = [i for i in range(0,len(course_list)) ]
	
	while True:
		if chosen_no == 0:
			break
			
		chosen_course_id = int(input('enter course number '))
		if chosen_course_id in array_c:
			chosen_idx.append(chosen_course_id)
			print (df.name[chosen_course_id] , ' : ', df.url[chosen_course_id])
			chosen_no-=1
		else:
			print ('wrong course id. Try again!!!!!!!!')
	return df.loc[chosen_idx]
	
def discussion_process(selected_course):
	filename = time.strftime("%Y%m%d-%H%M%S")+ "_logfile_discussion.csv"
	write_log(filename,["Course title","URL","status"])
	
	for tmp_name,tmp_url in zip(selected_course.name,selected_course.url):
		try:
			access_discussion(tmp_name,tmp_url)
			write_log(filename,[tmp_name,tmp_url, 'success' ])
		except Exception as e:

			write_log(filename,[ tmp_name,tmp_url, 'error '+ traceback.format_exc()])
			print(traceback.format_exc())

	driver.quit()

	
def write_log(filename,data):
	with open(filename,"a+",newline='',encoding='utf-8') as f:
		write_obj = csv.writer(f)
		write_obj.writerow(data)

def selected_course_2_csv(selected_course):
	filename = time.strftime("%Y%m%d-%H%M%S")+ "_selected_file.csv"
	write_log(filename,["Course title","URL"])
	for tmp_name,tmp_url in zip(selected_course.name,selected_course.url):
		write_log(filename,[ tmp_name, tmp_url ])


	
if __name__== "__main__":
	log_in(usr,pwd)
	course_list = list_dash_course()
	chosen_course = course_selection(course_list)
	selected_course_2_csv(chosen_course)
	discussion_process(chosen_course)
	



