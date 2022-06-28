from helper import *
import inquirer






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