from helper import *
import inquirer

courses = {
    "EN.500.109 What is Engineering?": {
        # 'sections': [1, 2, 3, 4, 5, 6, 11, 12, 21, 22, 23, 24, 25],
        'sections': [1,2],
        'ids': {
            1: '13312',
            2: '13313',
            # 3: '13314',
            # 4: '13315',
            # 5: '13316',
            # 6: '13317',
            # 11: '13322',
            # 12: '13323',
            # 21: '13332',
            # 22: '13333',
            # 23: '13334',
            # 24: '13335',
            # 25: '13336',
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
    sections = selected_course['sections']
    sections.append("Select all")
    answers = inquirer.prompt([
        inquirer.List(
            "section",
            message="Choose a section ",
            choices=sections,
        ),
    ])
    if answers['section'] != "Select all": 
        course_num = selected_course['ids'][answers['section']]
        url = 'https://jhu.instructure.com/api/v1/courses/' + str(course_num)
        getResponse(url)
    else: 
        course_num = answers['section']
else: 
    course_num = input('Course number:\t')
    url = 'https://jhu.instructure.com/api/v1/courses/' + str(course_num)
    getResponse(url)

if course_num == "Select all": 
    isStatistics = False
    answers = inquirer.prompt([
        inquirer.List(
            "cross-sections",
            message="Select an option ",
            choices=['View grading progress', "Show grades statistics"],
        ),
    ])
    if answers['cross-sections'] == 'Show grades statistics': 
        isStatistics = True
    assignment_choices = []
    assignments = getAllAssignments(courses[course_name]['ids'][1])
    for assignment in assignments: 
        assignment_choices.append(assignment['name'])
    answers = inquirer.prompt([
        inquirer.List(
            "assignment",
            message="Select an assignment ",
            choices=assignment_choices,
        ),
    ])
    selected_assignment_name = answers['assignment']
    assignments_by_section = []
    # quizzes_by_section = []
    for sect, id in courses[course_name]['ids'].items(): 
        assignments = getAllAssignments(id)
        for assignment in assignments: 
            assignment['section'] = sect
            assignment['course_id'] = id
            if assignment['name'] == selected_assignment_name:
                assignments_by_section.append(assignment)
            # if assignment['is_quiz_assignment']: 
            #     quizzes_by_section.append(assignment)
    if isStatistics: 
        getRecentAssignmentsStatsAcrossCourses(assignments_by_section)
        print('\n')
        # getQuizStatsAcrossSections(assignments_by_section)
    else: 
        displayGradingProgressAcrossSections(assignments_by_section)
else: 
    menu_choices = ['Show ALL assignments', 'Show an assignment group', 'Show recent quiz statistics', 'Show graded assignment statistics']
    group_choices = []

    answers = inquirer.prompt([
        inquirer.List(
            "menu",
            message="Choose one of these options ",
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
                message="Choose one of these groups ",
                choices=group_choices,
            ),
        ])
        group_id = answers['group'].split()[0]
        assignments = getAssignmentsByGroup(course_num, group_id)
        displayGradingProgress(course_num, assignments)
    elif submenu == menu_choices[2]: 
        getQuizStats(course_num)
    elif submenu == menu_choices[3]: 
        getRecentAssignmentsStats(course_num)