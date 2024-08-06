# -*- coding: utf-8 -*-
"""
Created on Sat Jul 15 09:36:52 2023

@author: marianne.bezaire
More general API for use with Tufts as well...
"""


import requests
import time

import re
import pickle

import json

import csv
import datetime

import sys

import random
from requests.structures import CaseInsensitiveDict

custom_list = False
liststudents = []
my_courses = []
"""
https://submit.cs50.io/api/courses: student_of, teacher_of

Inside those, for ex: teacher_of: ['description', 'id', 'name', 'slugs']


https://submit.cs50.io/api/courses/id/submissions: key for each slug
Each of those is a list of dictionaries (one dict per submission) with
keys of: ['commit_hash', 'org', 'pushed_at', 'repo', 'results', 'slug', 'user']

user: ['avatar_url', 'email', 'id', 'login', 'name']
results: ['check50', 'n_comments', 'received_at', 'style50', 'tag_hash']
All the rest are strings

In results, n_comments is an int, all the rest are strings except 
style50 and check50.
check50:
It has keys of: ['results', 'slug', 'version'] which are strings except:
    results, a list of dictionaries which have keys of:
    ['cause', 'data', 'dependency', 'description', 'log', 'name', 'passed']
    passed is a bool
    log is a list of strings
    cause can be None or a dictionary of expected, actual, help, rationale
    data can be a dictionary (often not used - empty)
    name may be the name of the function. It is a string
    description is the docstring, also a string, and dependency is a string
        that maps to some other function check
        

style50: has keys of: ['files', 'score', 'version']
    score is a float or int (numeric)
    files is a list where each item is a dictionary with keys:
        ['comments', 'diff', 'loc', 'name', 'score', 'warn_chars']
        all strings except comments is a boolean, loc and score are numeric,
        warn_chars is a list


It only seems to be the most recent submission per student

https://submit.cs50.io/api/courses/1772/members: has keys students and teachers
teachers is a list of dictionaries with keys:
    ['avatar_url', 'email', 'id', 'login', 'name']
    
students is a list of dictionaries with keys:
    ['avatar_url', 'email', 'id', 'login', 'name']
    
    
    
"""
    
def main(cs50_id = '1772', block='D'):
    global driver, my_courses
    
    my_courses = get_teacher_of()
    
    """
    try:
        from selenium import webdriver
        driver = webdriver.Chrome() 
        time.sleep(30)
        print("ok times up for " + cs50_id + " " + str(type(cs50_id)))
        course_subs = update_cs50(cs50_id)
        with open(f'cs50_{block}_20230201.pickle', 'wb') as handle:
            pickle.dump(course_subs, handle, protocol=pickle.HIGHEST_PROTOCOL)
    except:
        print("no selenium available")
        with open(f'cs50_{block}_20230201.pickle', 'rb') as handle:
            course_subs = pickle.load(handle)
    """

def get_cs50(json_url = 'https://submit.cs50.io/api/courses'):
    # "https://submit.cs50.io/api/courses/" + courseId + "/submissions/export";
    # https://submit.cs50.io/api/courses
    token = "ea4429f5f67a43599c6cadd49a594f76"
    # Relative URL of external json file   
    from requests.structures import CaseInsensitiveDict
    headers = CaseInsensitiveDict()
    headers["method"]= "get"
    headers["Access-Control-Allow-Origin"]= "*"
    headers["Access-Control-Allow-Methods"]="DELETE, POST, GET, OPTIONS"
    headers["Access-Control-Allow-Headers"]="Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
    # headers["Accept"]="application/json"
    headers["Authorization"]="token " + token
    headers["Content-type"]="application/x-www-form-urlencoded"
    response = requests.get(json_url,headers=headers)
    return response

def get_teacher_of(json_url = 'https://submit.cs50.io/api/courses'):
    """
    

    Parameters
    ----------
    json_url : string, optional
        The API URL to access. The default is 'https://submit.cs50.io/api/courses'.

    Returns
    -------
    courses50 : list of dictionaries - one per course
        Dictionaries contain keys: ['description', 'id', 'name', 'slugs']
        The 'slugs' key is a list of strings, the others are strings,
        except 'id' which is an int

    """
    course_tmp = get_cs50(json_url)
    courses50 = course_tmp.json()['teacher_of']
    return courses50

def update_cs50(cs50_id = None):
    courses50 = get_teacher_of()
    course_subs = {}
    for course in courses50:
        if (type(cs50_id) == list and str(course['id']) not in cs50_id) or (type(cs50_id) != list and cs50_id != str(course['id'])):
            continue
        slugs = {}
        if custom_list:
            for slug in course['slugs']:
                students = {}
                for student in liststudents:
                    driver.get('https://submit.cs50.io/users/'+ student +'/' + slug)
                    html = driver.page_source
                    patt = re.compile("React.createElement\([\s]*Submission,[\s]*([\s\S]*?)(?=,[\s]*index: [0-9]+[\s]*},[\s]*null[\s]*\),[\s]*document.get)")
                    match = re.findall(patt, html)
                    subs = []
                    for m in match:
                        subs.append(json.loads(m.replace("\n","")[65:]))
                    students[student] = subs
                slugs[slug] = students
        course_subs[str(course['id'])] = slugs
    return course_subs


class eastern(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=-5)
        

    def fromutc(self, dt):
        # Follow same validations as in datetime.tzinfo
        if not isinstance(dt, datetime.datetime):
            raise TypeError("fromutc() requires a datetime argument")
        if dt.tzinfo is not self:
            raise ValueError("dt.tzinfo is not self")

        return dt - datetime.timedelta(hours=5)

    def dst(self, dt):
        # Kabul does not observe daylight saving time.
        return datetime.timedelta(1)

    def tzname(self, dt):
        return "-05"
    
    def __str__(self):
        return "Eastern"
    
    def __repr__(self):
        return "Eastern"

if __name__ == "__main__":
    main()