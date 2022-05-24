#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Deepkumar Patel
Created on Feburary 27, 2021, ‏‎10:58:31 AM
Semester: Spring 1, 2021
Course name: Artificial Intelligence
Assignment: Machine Problem 3
Course planning using a Constraint Satisfaction problem formulation
Description:
Program checks if there are possible schedules for students for a given
start and finish term, given all constraints.
This works by mapping a term number to each course, given all constraints.
It assigns a negative term number if course is not taken (e.g. elective that is not needed)

ASSUMPTION: term numbers start with 1
"""
import pandas as pd
import numpy as np
from constraint import *

def create_term_list(terms, years=4):
    '''Create a list of term indexes for years in the future'''
    all_terms = []
    for year in range(years):
        for term in terms:    
            all_terms.append(year*6+term)
    return all_terms
    
def map_to_term_label(term_num):
    '''Returns the label of a term, given its number'''
    term_num_to_label_map = {
            0: 'Fall 1',
            1: 'Fall 2',
            2: 'Spring 1',
            3: 'Spring 2',
            4: 'Summer 1',
            5: 'Summer 2',
    }
    if (term_num < 1):
        return 'Not Taken'
    else:
        return 'Year ' + str((term_num - 1) // 6 + 1) + ' ' + term_num_to_label_map[(term_num - 1) % 6]

def prereq(a, b):
    '''Used for encoding prerequisite constraints, a is a prerequisite for b'''
    if a > 0 and b > 0: # Taking both prereq a and course b
        return a < b
    elif a > 0 and b < 0: # Taking prereq a, but not course b
        return True
    elif a < 0 and b > 0: #  Taking course b, but not prereq a
        return False
    else:
        return True # Not taking prereq a or course b

def get_possible_course_list(start, finish):
    '''Returns a possible course schedule, assuming student starts in start term
       finishes in finish term'''
    problem = Problem()
    
    # Read course_offerings file
    course_offerings = pd.read_excel('csp_course_rotations.xls', sheet_name='course_rotations')
    course_prereqs = pd.read_excel('csp_course_rotations.xls', sheet_name='prereqs')

    # Foundation course terms
    foundation_courses = course_offerings[course_offerings.Type == 'foundation']
    for r,row in foundation_courses.iterrows():
        terms = create_term_list(list(row[row==1].index))
        # Control start and finish term
        terms[:] = [x for x in terms if x >= start and x <= finish]
        problem.addVariable(row.Course, terms)

    """ TODO FROM HERE... """    
    #Core course terms
    core_courses = course_offerings[course_offerings.Type == 'core']
    for r,row in core_courses.iterrows():
        terms = create_term_list(list(row[row==1].index))
        # Control start and finish term
        terms[:] = [x for x in terms if x >= start and x <= finish]
        problem.addVariable(row.Course, terms)

    #CS Electives course terms (-x = elective not taken)
    elective_not_taken = -1
    elective_courses = course_offerings[course_offerings.Type == 'elective']
    for r, row in elective_courses.iterrows():
        terms = create_term_list(list(row[row==1].index))
        # Control start and finish term
        terms[:] = [x for x in terms if x >= start and x <= finish]
        terms.append(elective_not_taken)
        elective_not_taken -= 1
        problem.addVariable(row.Course, terms)

    # Capstone
    capstone_courses = course_offerings[course_offerings.Type=='capstone']
    for r,row in capstone_courses.iterrows():
        terms = create_term_list(list(row[row==1].index))
        # Control start and finish term
        terms[:] = [x for x in terms if x >= start and x <= finish]
        problem.addVariable(row.Course, terms)
    
    # Guarantee no repeats of courses
    problem.addConstraint(AllDifferentConstraint())
    
    # Control start and finish terms
    # Done above

    # Control electives - exactly 3 courses must be chosen
    problem.addConstraint(SomeInSetConstraint([-1, -2, -3, -4, -5, -6, -7, -8], n = 5, exact = True))

    # Prereqs
    count = 0
    for preq in course_prereqs.prereq:
        problem.addConstraint(FunctionConstraint(prereq), [course_prereqs.prereq.iloc[count], course_prereqs.course.iloc[count]])
        count+=1

    """ ...TO HERE """
    # Generate a possible solution
    sol = problem.getSolutions()

    print('Number of Possible Degree Plans is',len(sol))
    print('START TERM = ' + map_to_term_label(start), '\n')

    s = pd.Series(sol[0])
    return s.sort_values().map(map_to_term_label)

# Print heading
print("CLASS: Artificial Intelligence, Lewis University")
print("NAME: Deepkumar Patel", '\n')

# Check for possible schedules for all start terms
for start in [1]:
    s = get_possible_course_list(start,start+13)
    if s.empty:
        print('NO POSSIBLE SCHEDULE!')
    else:
        s2 = pd.Series(s.index.values, index=s)
        print(s2.to_string())
    print()

