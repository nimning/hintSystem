#!/usr/bin/env python

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.common.exceptions import NoSuchElementException
import yaml
from random import random
from time import sleep
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Script to simulate a student on WebWork')
    parser.add_argument('--username', '-u', default='student1')
    parser.add_argument('--password', '-p', default='50001')
    parser.add_argument('--course', '-c', default='UCSD_CSE103')
    parser.add_argument('--theta', '-t', type=float, default=0.1, help='The probability with which the student gets the correct answer')
    parser.add_argument('--filename', '-f', default='hw.yaml', help='A YAML file describing the homework')
    parser.add_argument('--domain', '-d', default='192.168.33.10', help='Domain running webwork (can be an IP address)')
    args = parser.parse_args()
    return args


def simulate_student(hw_file, domain, course, p_correct, username, password):
    with open(hw_file) as f:
        hw_def = yaml.load(f)

    hw_name = hw_def['name']
    homepage = "http://{0}/webwork2/{1}".format(domain, course)
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

    # Now we're logged in
    # driver.save_screenshot("{0}_{1}.png".format(username, 'logged_in'))
    driver.get("{0}/{1}".format(homepage, hw_name))
    # driver.save_screenshot("{0}_{1}.png".format(username, hw_name))
    for problem in hw_def['problems']:
        problem_url = "{0}/{1}/{2}".format(homepage, hw_name, problem['number'])
        driver.get(problem_url)
        print driver.title
        # driver.save_screenshot("{0}_p{1}.png".format(username, problem['number']))
        for part, answer in problem['parts'].iteritems():
            answered = False
            tries = 0

            while not answered:
                part_el = driver.find_element_by_id(part)
                submit = driver.find_element_by_id("submitAnswers_id")
                if random() < p_correct:
                    part_el.clear()
                    part_el.send_keys(answer)
                    sleep(0.5)
                    submit.click()

                    print tries
                    answered = True
                else:
                    part_el.clear()
                    part_el.send_keys("gibberish")
                    sleep(0.5)
                    submit.click()
                    tries = tries + 1
                    print driver.title

if __name__ == '__main__':
    args = parse_args()
    simulate_student(args.filename, args.domain, args.course, args.theta,
                     args.username, args.password)
