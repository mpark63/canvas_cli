import requests
import json
import time
import asyncio
from aiohttp import ClientSession
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import date
from datetime import timedelta
import sys
import os
from pathlib import Path
from pltHelper import *
plt.rcParams.update({'figure.max_open_warning': 0})

assignment_scores = {}
section_scores = {}
grading_progress = {}
s = requests.Session() 
url = "https://jhu.instructure.com/api/v1/courses/"

async def getCourses(headers): 
    return await getResponse(url, headers)

async def getResponse(url, headers): 
    async with ClientSession(trust_env=True) as session:
        async with session.get(url, headers = headers) as res:  
            if res.status == 401:
                print('401 unauthorized. Please check request headers.', url)
                sys.exit()
            elif res.status == 404:
                print('404 Not found. Please check your URL.\n', url)
                sys.exit()
            elif res.status != 200: 
                sys.exit()
            text = await res.text()
            parsed = json.loads(text)
    return parsed

async def getAssignmentGroups(course, headers): 
    groups_url = url+str(course)+'/assignment_groups'
    groups = await getResponse(groups_url, headers)
    res = []
    for assignment_group in groups: 
        res.append({
            "id": assignment_group['id'],
            "name": assignment_group['name']
        })
    return res 

async def getAllAssignmentsStats(course, headers):
    assignments = await getResponse(url+str(course)+'/analytics/assignments?per_page=100', headers)
    for assignment in assignments: 
        due_date = None
        if assignment['due_at'] != None: 
            due_date = datetime.strptime(assignment['due_at'], '%Y-%m-%dT%H:%M:%SZ')
            assignment['due_at'] = due_date
    # res.sort(key=lambda assignment: (assignment['due_at'] == None, assignment['due_at']))
    return assignments 

async def getGradingProgress(course, assignment, headers): 
    submissions_url = url+course+'/assignments/'+str(assignment)+'/submission_summary'
    grading = await getResponse(submissions_url, headers)
    return grading

async def getScores(course, assignment, headers): 
    submissions_url = url+course+'/assignments/'+str(assignment)+'/submissions?per_page=50'
    submissions = await getResponse(submissions_url, headers)
    return submissions

async def getSubmissions(course, headers): 
    assignments = await getAllAssignmentsStats(course, headers)
    tasks1 = [asyncio.create_task(storeGradingProgress(course, assignment['assignment_id'], assignment['title'], headers)) for assignment in assignments] 
    await asyncio.gather(*tasks1) 
    tasks2 = [asyncio.create_task(storeScores(course, assignment, headers)) for assignment in assignments] 
    await asyncio.gather(*tasks2) 

async def storeGradingProgress(course, id, name, headers): 
    status = await getGradingProgress(course, id, headers)
    grading_progress[course] = grading_progress.get(course, {})
    grading_progress[course][name] = list(status.values())

async def storeScores(course, assignment, headers): 
    name = assignment['title']
    if assignment['max_score'] != None: 
        submissions = await getScores(course, assignment['assignment_id'], headers)
        for submission in submissions:
            score = submission['score']
            if score == None: 
                continue
            assignment_scores[name] = assignment_scores.get(name, {})
            assignment_scores[name][score] = assignment_scores[name].get(score, 0) + 1
            section_scores[course] = section_scores.get(course, {})
            section_scores[course][name] = section_scores[course].get(name, {})
            section_scores[course][name][score] = section_scores[course][name].get(score, 0) + 1
    else: 
        assignment_scores[name] = {}

def setup(f, course_name): 
    f.write("\documentclass{article}\n")
    f.write(r"\usepackage[hidelinks]{hyperref}" + "\n")
    f.write(r"\usepackage{graphicx}" + "\n")
    f.write(r"\usepackage{ragged2e}" + "\n")
    f.write(r"\usepackage{booktabs}" + "\n")  # for df.to_latex()
    f.write(r"\usepackage{caption}" + "\n")
    f.write(r"\usepackage{subfig}" + "\n")
    f.write(r"\usepackage[top=1in, bottom=1in, left=1in, right=1in, "+
            "marginparsep=0.15in]{geometry}" + "\n")
    f.write(r"\title{" + course_name + r" Grading Report}" + "\n")
    f.write(r"\date{"+ datetime.now().strftime("%m/%d/%Y, %H:%M:%S EDT") + r"}" + "\n")
    f.write(r"\author{}" + "\n")
    f.write(r"\begin{document} \maketitle" + "\n")

def writeGradingProgress(f, course_num, section):
    # -- Set up figure data
    category_names = ['graded', 'ungraded', 'not_submitted']
    # -- Create figure
    surveyGradingProgress(grading_progress[course_num], category_names)
    # -- Save figure
    figname = "Grading Progress - " + str(section)
    plt.savefig('tex/fig/'+figname+'.png', bbox_inches='tight', dpi=300)
    plt.clf() 
    # -- Insert figure into LaTeX
    f.write(r"\subsection{Section " + str(section) + "}" + "\n")
    f.write(r"\includegraphics[width=6in]{fig/"+figname+r".png}" + "\n")

async def writeAssignment(f, course_num, assignment_name, assignment_num, due_date, headers):
    status = await getGradingProgress(course_num, assignment_num, headers)
    f.write(r'\section{' + assignment_name + '}\n')
    f.write(r'\linebreak' + "\n")
    if due_date != None: 
        f.write(r"Due:  " + due_date + "\n")
    f.write(r'\linebreak' + "\n")
    f.write(r'' + str(status['graded']) + ' graded' + "\n")
    f.write(r'' + str(status['ungraded']) + ' ungraded' + "\n")
    f.write(r'' + str(status['not_submitted']) + ' unsumbitted' + "\n")

async def writeOneGradingProgress(f, course_num, assignment_num, headers):
    status = await getGradingProgress(course_num, assignment_num, headers)
    f.write(r'' + str(status['graded']) + ' graded' + "\n")
    f.write(r'' + str(status['ungraded']) + ' ungraded' + "\n")
    f.write(r'' + str(status['not_submitted']) + ' unsumbitted' + "\n")

def writeDistribution(f, course_num, assignment_name, section_num, max): 
    st = 1
    if max < 10: 
        st = 1
    elif max < 20: 
        st = 2
    elif max < 50: 
        st = 5
    else: 
        st = 10

    fig, axes = plt.subplots(1,2,figsize=(8,3))

    plt.sca(axes[0])
    plt.xlim(-1, max + 1)
    plt.xticks(np.arange(0, max+1, st))
    plt.xlabel('Score')
    plt.ylabel('Frequency')
    data = assignment_scores[assignment_name]
    axes[0].set_title("All sections")
    axes[0].bar(data.keys(), data.values())
    axes[0].yaxis.get_major_locator().set_params(integer=True)

    plt.sca(axes[1])
    plt.xlim(-1, max + 1)
    plt.xticks(np.arange(0, max+1, st))
    plt.xlabel('Score')
    plt.ylabel('Frequency')
    data = section_scores[course_num][assignment_name]
    axes[1].set_title("Section" + section_num)
    axes[1].bar(data.keys(), data.values())
    axes[1].yaxis.get_major_locator().set_params(integer=True)
    fig.savefig('tex/fig/'+assignment_name + '.png', bbox_inches='tight', dpi=300)
    f.write(r"\includegraphics[width=6in]{fig/"+assignment_name+r".png}" + "\n")
    plt.clf()

    # write mean and standard deviation 
    f.write(r"\begin{FlushLeft}" + "\n")
    mean_all = mean(assignment_scores[assignment_name])
    mean_spec = mean(section_scores[course_num][assignment_name])
    std_all = std(assignment_scores[assignment_name], mean_all) ** .5
    std_spec = std(section_scores[course_num][assignment_name], mean_spec) ** .5
    f.write(r'Course average: ' + str("{:.2f}".format(mean_all)) + "\n")
    f.write(r'\linebreak' + "\n")
    f.write(r'Section average: ' + str("{:.2f}".format(mean_spec)) + "\n")
    f.write(r'\linebreak' + "\n")
    f.write(r'Course standard deviation: ' + str("{:.2f}".format(std_all)) + "\n")
    f.write(r'\linebreak' + "\n")
    f.write(r'Section standard deviation: ' + str("{:.2f}".format(std_spec)) + "\n")
    f.write(r'\linebreak' + "\n")
    f.write(r"\end{FlushLeft}" + "\n")

def writeOneDistribution(f, fig, course_num, section, assignment_name, max, index): 
    st = 1
    if max < 10: 
        st = 1
    elif max < 20: 
        st = 2
    elif max < 50: 
        st = 5
    else: 
        st = 10

    ax = fig.add_subplot(3, 2, index)
    ax.yaxis.get_major_locator().set_params(integer=True)

    plt.sca(ax)
    plt.xlim(-1, max + 1)
    plt.xticks(np.arange(0, max+1, st))
    ax.set_ylabel('Frequency')
    figname = assignment_name
    if index == 1: 
        data = assignment_scores[assignment_name]
    else: 
        data = section_scores[course_num][assignment_name]
    ax.bar(data.keys(), data.values())
    ax.set_title(section)

    mean_spec = mean(data)
    std_spec = std(data, mean_spec) ** .5
    f.write(r'\linebreak' + "\n")
    f.write(r'' + section + "\n")
    f.write(r'\linebreak' + "\n")
    f.write(r'Average: ' + str("{:.2f}".format(mean_spec)) + "\n")
    f.write(r'\linebreak' + "\n")
    f.write(r'Standard deviation: ' + str("{:.2f}".format(std_spec)) + "\n")
    f.write(r'\linebreak' + "\n")

def mean(dict): 
    sum = 0
    count = 0
    for k, v in dict.items(): 
        sum += k * v
        count += v
    if count == 0: return -1 
    return sum / count

def std(dict, mean): 
    sum = 0
    count = 0
    for k, v in dict.items(): 
        sum += v * k**2
        count += v
    if count == 0 or count == 1: return -1
    return (sum - count * mean**2) / (count - 1)

def closeFile(f, latexFileName): 
    f.write(r"\end{document}")
    f.close()
    os.system("pdflatex -output-directory=tex --interaction=batchmode "+latexFileName)

async def assignmentBySection(f, course_num, courses, assignment): 
    fig = plt.figure(figsize=(8,12))
    f.write(r"\section{" + assignment['title'] + "}" + "\n")
    f.write(r"\begin{FlushLeft}" + "\n")
    if assignment['due_at'] != None:
        due_date = '\n' + assignment['due_at'].strftime("%m/%d/%Y, %H:%M:%S")
        f.write(r'\linebreak' + "\n")
        f.write(r"" + due_date + "\n")
    if assignment['title'] in assignment_scores: 
        if int(assignment['points_possible']) == 0: 
            f.write(r"Current max score set to null." + "\n")
            return
        elif assignment_scores[assignment['title']] == {}: 
            f.write(r"No grade data." + "\n")
            return
        else: 
            writeOneDistribution(f, fig, course_num, 'All sections', assignment['title'], assignment['points_possible'], 1)
    else: 
        return
    fn = 1
    index = 2
    for section, course in courses: 
        if index == 7: 
            figname = str(assignment['assignment_id']) + "_" + str(fn)
            fig.savefig('tex/fig/'+figname + '.png', bbox_inches='tight', dpi=300)
            plt.clf() 
            fig = plt.figure(figsize=(8,12))
            index = 1
            fn += 1
        if assignment['title'] in section_scores[course]: 
            writeOneDistribution(f, fig, course, 'Section ' + str(section), assignment['title'], assignment['points_possible'], index)
            index += 1
    if index != 1: 
        figname = str(assignment['assignment_id']) + "_" + str(fn)
        fig.savefig('tex/fig/'+figname + '.png', bbox_inches='tight', dpi=300)
    plt.clf() 
    mean_all = mean(assignment_scores[assignment['title']])
    std_all = std(assignment_scores[assignment['title']], mean_all) ** .5
    f.write(r"\end{FlushLeft}" + "\n")
    for i in range(1, fn + 1): 
        f.write(r"\includegraphics[width=6in]{fig/"+str(assignment['assignment_id']) + "_" + str(i) + r".png}" + "\n")
        f.write(r'\linebreak' + "\n")
    plt.close(fig)

async def sectionByAssignment(f, course_num, assignment, section_num, headers): 
    if assignment['title'] in section_scores[course_num]: 
        due_date = None
        if assignment['due_at'] != None:
            due_date = '\n' + assignment['due_at'].strftime("%m/%d/%Y, %H:%M:%S")
        f.write(r"\begin{FlushLeft}" + "\n")
        f.write(r'\linebreak' + "\n")
        await writeAssignment(f, course_num, assignment['title'], assignment['assignment_id'], due_date, headers)
        f.write(r'\linebreak' + "\n")
        if int(assignment['points_possible']) == 0: 
            f.write(r"Current max score set to null." + "\n")
            return
        if assignment_scores[assignment['title']] == {}: 
            f.write(r"No grade data." + "\n")
            return
        max = assignment['points_possible']
        writeDistribution(f, course_num, assignment['title'], section_num, max)
        f.write(r"\end{FlushLeft}" + "\n")

async def writeFile(courses, course_num, course_name, section_num, headers): 
    start = time.perf_counter()
    print("Pulling submission data from Canvas API... ")
    tasks = [asyncio.create_task(getSubmissions(course, headers)) for section, course in courses] 
    await asyncio.gather(*tasks)  
    end = time.perf_counter()
    print(end - start, "s\n")
    Path("./tex/fig").mkdir(parents=True, exist_ok=True)
    latexFileName = "tex/" + course_name.replace(' ', '_') + ".tex"
    f = open(latexFileName, "w")
    setup(f, course_name)
    f.write(r"\section{Grading Progress}" + "\n")
    if course_num != None: 
        start = time.perf_counter()
        print("Surveying grading progress from Canvas API... ")
        writeGradingProgress(f, course_num, section_num)
        assignments = await getAllAssignmentsStats(course_num, headers)
        end = time.perf_counter()
        print(end - start, "s\n")
        start = time.perf_counter()
        print("Creating grade distribution bar charts... ")
        tasks = [asyncio.create_task(sectionByAssignment(f, course_num, assignment, section_num, headers)) for assignment in assignments] 
        await asyncio.gather(*tasks)  
        end = time.perf_counter()
        print(end - start, "s\n")
    else: 
        start = time.perf_counter()
        print("Surveying grading progress from Canvas API... ")
        for section, course in courses: 
            writeGradingProgress(f, course, section)
        course_num = courses[0][1]
        assignments = await getAllAssignmentsStats(course_num, headers)
        end = time.perf_counter()
        print(end - start, "s\n")
        start = time.perf_counter()
        print("Creating grade distribution bar charts... ")
        tasks = [asyncio.create_task(assignmentBySection(f, course_num, courses, assignment)) for assignment in assignments] 
        await asyncio.gather(*tasks)  
        end = time.perf_counter()
        print(end - start, "s\n")
    closeFile(f, latexFileName)
    print("\nSuccessfully generated\t" + latexFileName + "!")