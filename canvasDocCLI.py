from helper import *
from pltHelper import *
import inquirer

headers = {}
course_name = ''
isPDF = False
course_num = 1234
menu = True 

courses = {
    "EN.500.109 What is Engineering?": {
        'sections': [1, 2, 3, 4, 5, 6, 11, 12, 21, 22, 23, 24, 25],
        'ids': {
            1: '13312',
            2: '13313',
            3: '13314',
            4: '13315',
            5: '13316',
            6: '13317',
            11: '13322',
            12: '13323',
            21: '13332',
            22: '13333',
            23: '13334',
            24: '13335',
            25: '13336',
        }
    },
    "EN.500.130 Biomedical Engineering Innovation": {
        'sections': [1, 2, 3, 4, 5],
        'ids': {
            1: '13232',
            2: '13233',
            3: '13234',
            4: '13235',
            5: '13236',
        }
    },
    "CO.EN.BMEI.100 Teacher Training": {
        'sections': [1],
        'ids': {
            1: '13697', 
        }
    },
    "CO.EN.EEI.100 Teacher Training": {
        'sections': [1],
        'ids': {
            1: '13698',
        }
    },
}
course_names = courses.keys()

def inputAuthorization(): 
    access_code = input("Canvas access code: ")
    headers['Authorization'] = 'Bearer ' + access_code
    print('\n')

def welcomeMenu(): 
    answers = inquirer.prompt([
        inquirer.List(
            "index",
            message="Welcome, choose an option ",
            choices=["Find your course", "Enter course id"],
        ),
    ])
    if answers['index'] == "Find your course": 
        answers = inquirer.prompt([
            inquirer.List(
                "course",
                message="Choose a course ",
                choices=course_names,
            ),
        ])
        course_name = answers['course']
        selected_course = courses[course_name]
        course_nums = list(selected_course['ids'].items())
        sections = selected_course['sections']
        sections.append("All sections")
        answers = inquirer.prompt([
            inquirer.List(
                "section",
                message="Choose a section ",
                choices=sections,
            ),
        ])
        section_num  = str(answers['section'])
        if section_num == 'All sections': 
            course_num = None
            course_name += ' - All Sections'
        else: 
            course_num = selected_course['ids'][answers['section']]
            course_name += ' Section ' + section_num
    else: 
        course_num = input('Course number:\t')
        course_num = course_num.strip()
        course_name = '' + course_num
    return course_name, course_nums, course_num, section_num

def formatMenu(): 
    answers = inquirer.prompt([
        inquirer.List(
            "format",
            message="Select a format for your course summary ",
            choices=['Text', 'PDF'],
        ),
    ])
    return answers['format'] == 'PDF'

inputAuthorization()
[course_name, course_nums, course_num, section_num] = welcomeMenu()
isPDF = formatMenu()
if (isPDF): 
    writeFile(course_nums, course_num, course_name, section_num, headers)
else: 
    textReport(course_name, course_num)
