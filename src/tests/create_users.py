#!/usr/bin/env python

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.common.exceptions import NoSuchElementException
import yaml
from random import random
from time import sleep

COURSE_NAME = "UCSD_CSE103"
DOMAIN = "192.168.33.10"
username = "admin"
password = "admin"
homepage = "http://{0}/webwork2/{1}".format(DOMAIN, COURSE_NAME)
start_user = 50
user_count = 50
driver = webdriver.PhantomJS()
driver.get(homepage)

# Try to log in
try:
    form = driver.find_element_by_id("login_form")
    userfld = driver.find_element_by_id("uname")
    passwdfld = driver.find_element_by_id("pswd")
    userfld.send_keys(username)
    passwdfld.send_keys(password)
    form.submit()
except NoSuchElementException: # We're probably already logged in
    pass

print driver.title
# Now we're logged in, go to users page
driver.get("{0}/instructor/add_users/".format(homepage))

print driver.title

add_ct = driver.find_element_by_name("number_of_students")
add_ct.clear()
add_ct.send_keys("{0}".format(user_count))
add_ct.submit()

for i in range(1, user_count+1):
    print i
    lname = driver.find_element_by_name("last_name_{0}".format(i))
    fname = driver.find_element_by_name("first_name_{0}".format(i))
    sid = driver.find_element_by_name("student_id_{0}".format(i))
    user_id = driver.find_element_by_name("new_user_id_{0}".format(i))
    email = driver.find_element_by_name("email_address_{0}".format(i))
    lname.send_keys("Student")
    fname.send_keys("Number {0}".format(i+start_user))
    sid.send_keys("{0}".format(50000+i+start_user))
    user_id.send_keys("student{0}".format(i+start_user))
    email.send_keys("student{0}@example.com".format(i+start_user))

# Assign all homeworks to new students
for hw in driver.find_elements_by_css_selector("select[name='assignSets'] > option"):
    hw.click()

driver.find_element_by_name("addStudents").click()

print driver.title
driver.save_screenshot("addusers.png")
