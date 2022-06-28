from helper import *
import inquirer

courses = {
    "What is Engineering?": {
        'number': 'EN.500.109',
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
    "Biomedical Engineering Innovation": {
        'number': 'EN.500.130',
        'sections': [1, 2, 3, 4, 5],
        'ids': {
            1: '13232',
            2: '13233',
            3: '13234',
            4: '13235',
            5: '13236',
        }
    },
    "Teacher Training": {
        'number': 'CO.EN.BMEI.100',
        'sections': [1, 2],
        'ids': {
            1: '13697', 
            2: '13698',
        }
    },
}
course_names = courses.keys()

answers = inquirer.prompt([
    inquirer.List(
        "index",
        message="Welcome, choose an option: ",
        choices=["Find your course", "Enter course id"],
    ),
])

if answers['index'] == "Find your course": 
    answers = inquirer.prompt([
        inquirer.List(
            "course",
            message="Choose a course: ",
            choices=course_names,
        ),
    ])
    selected_course = courses[answers['course']]
    sections = selected_course['sections']
    answers = inquirer.prompt([
        inquirer.List(
            "section",
            message="Choose a section: ",
            choices=sections,
        ),
    ])
    course_num = selected_course['ids'][answers['section']]
else: 
    course_num = input('Course number:\t')

menu_choices = ['Show ALL assignments', 'Show an assignment group', 'Show quiz statistics']
group_choices = []

answers = inquirer.prompt([
    inquirer.List(
        "menu",
        message="Choose one of these options: ",
        choices=menu_choices,
    ),
])
submenu = answers['menu']
if submenu == menu_choices[0]: 
    assignments = getAllAssignments(course_num)
    displayGradingProgress(course_num, assignments)
elif submenu == menu_choices[1]: 
    groups = getAssignmentGroups(course_num)
    for group in groups: 
        choice = str(group['id']) + ' ' + group['name']
        group_choices.append(choice)
    answers = inquirer.prompt([
        inquirer.List(
            "group",
            message="Choose one of these groups: ",
            choices=group_choices,
        ),
    ])
    group_id = answers['group'].split()[0]
    assignments = getAssignmentsByGroup(course_num, group_id)
    displayGradingProgress(course_num, assignments)
elif submenu == menu_choices[2]: 
    getQuizStats(course_num)