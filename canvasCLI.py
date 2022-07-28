import asyncio
import inquirer
from helper import *
from pltHelper import *
from config import courses
from config import course_names

headers = {}            # for requests
course_name = ''
course_num = 1234

# prompt for canvas access code and set headers 
def inputAuthorization(): 
    access_code = input("Canvas access code: ")
    headers['Authorization'] = 'Bearer ' + access_code
    print('\n')

# print options to select one or multiple sections of a course  
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

# async function to open interactive menu
async def main():
    inputAuthorization()
    [course_name, course_nums, course_num, section_num] = welcomeMenu()
    await writeFile(course_nums, course_num, course_name, section_num, headers)

# call async main function as asyncio event 
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
