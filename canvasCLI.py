import asyncio
import inquirer
from helper import *
from pltHelper import *
from config import courses
from config import course_names

headers = {}
course_name = ''
isPDF = False
course_num = 1234
menu = True 

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

async def main():
    inputAuthorization()
    [course_name, course_nums, course_num, section_num] = welcomeMenu()
    await writeFile(course_nums, course_num, course_name, section_num, headers)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
