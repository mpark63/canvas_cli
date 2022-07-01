from helper import *
from pltHelper import *
import inquirer

headers = {}
course_num = 1234
course_names = []
menu = True 

def inputAuthorization(headers): 
    access_code = input("Canvas access code: ")
    headers['Authorization'] = 'Bearer ' + access_code
    courses = getCourses(headers)
    for course in courses: 
        course_names.append(str(course['id']) + ' ' + course['name'])

def welcomeMenu(): 
    answers = inquirer.prompt([
        inquirer.List(
            "index",
            message="Welcome, choose an option ",
            choices=["Select a course", "Enter course id"],
        ),
    ])
    if answers['index'] == "Select a course": 
        answers = inquirer.prompt([
            inquirer.List(
                "course",
                message="Select a course ",
                choices=course_names,
            ),
        ])
        selected_course = answers['course']
        course_num = selected_course.split()[0]
        course_name = selected_course.split()[1]
    else: 
        course_num = input('Course number:\t')
        print('\n')
    url = 'https://jhu.instructure.com/api/v1/courses/' + str(course_num)
    getResponse(url, headers)
    return course_num

def submenu(): 
    menu_choices = ['Show ALL assignments grading progress', 'Show an assignment group grading progress', 'Show recent quiz statistics', 'Show graded assignment statistics', 'Exit']
    answers = inquirer.prompt([
        inquirer.List(
            "menu",
            message="Choose one of these options ",
            choices=menu_choices,
        ),
    ])
    submenu = answers['menu']
    if submenu == menu_choices[0]: 
        assignments = getAllAssignmentsStats(course_num, headers)
        displayGradingProgress(course_num, assignments, headers)
    elif submenu == menu_choices[1]: 
        groupMenu()
    elif submenu == menu_choices[2]: 
        getQuizStats(course_num, headers)
    elif submenu == menu_choices[3]: 
        getRecentAssignmentsStats(course_num, headers)
    else: 
        sys.exit()

def groupMenu(): 
    group_choices = []
    groups = getAssignmentGroups(course_num, headers)
    for group in groups: 
        choice = str(group['id']) + ' ' + group['name']
        group_choices.append(choice)
    answers = inquirer.prompt([
        inquirer.List(
            "group",
            message="Choose one of these groups ",
            choices=group_choices,
        ),
    ])
    group_id = answers['group'].split()[0]
    assignments = getAssignmentsByGroup(course_num, group_id, headers)
    displayGradingProgress(course_num, assignments, headers)

inputAuthorization(headers)
course_num = welcomeMenu()
while (menu): 
    submenu()
    print('\n')