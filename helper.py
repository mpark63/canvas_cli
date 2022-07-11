import requests
import json
import time
from pprint import pprint
import pandas as pd
from tabulate import tabulate
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import date
from datetime import timedelta
import sys
import os
from pathlib import Path
from pltHelper import *

assignment_scores = {}
section_scores = {}
s = requests.Session() 
url = "https://jhu.instructure.com/api/v1/courses/"

def getCourses(headers): 
    return getResponse(url, headers)

def getResponse(url, headers): 
    res = s.get(url, headers = headers)
    if res.status_code == 401:
        print('401 unauthorized. Please check request headers.', url)
        sys.exit()
    elif res.status_code == 404:
        print('404 Not found. Please check your URL.\n', url)
        sys.exit()
    elif res.status_code != 200: 
        print(res.status_code, url)
        sys.exit()
    parsed = json.loads(res.content)
    return parsed

def getAssignmentGroups(course, headers): 
    groups_url = url+str(course)+'/assignment_groups'
    groups = getResponse(groups_url, headers)
    res = []
    for assignment_group in groups: 
        res.append({
            "id": assignment_group['id'],
            "name": assignment_group['name']
        })
    return res 

def getQuizStats(course, headers): 
    quizzes_url = url+str(course)+'/quizzes'
    quizzes = getResponse(quizzes_url, headers)
    quizzes.sort(key=lambda quiz: (quiz['due_at'] == None, quiz['due_at']))
    data = {}
    ids = []
    names = []
    due_dates = []
    averages = []
    stdevs = []

    for quiz in quizzes: 
        if quiz['due_at'] == None: 
            break
        due_date = datetime.strptime(quiz['due_at'], '%Y-%m-%dT%H:%M:%SZ')
        if due_date > datetime.now() + timedelta(days=3): 
            break
        ids.append(quiz['id'])
        names.append(quiz['title'])
        due_dates.append(quiz['due_at'])
        stats = getResponse(quiz['quiz_statistics_url'], headers)
        average = stats['quiz_statistics'][0]['submission_statistics']['score_average']
        averages.append(average)
        stdev = stats['quiz_statistics'][0]['submission_statistics']['score_stdev']
        stdevs.append(stdev)
    data["Id"] = ids
    data["Title"] = names
    data["Due"] = due_dates
    data["Mean"] = averages
    data["StDev"] = stdevs
    df = pd.DataFrame(data)
    print(tabulate(df, headers = 'keys', tablefmt = 'simple'))

def getAllAssignments(course, headers):
    assignments = getResponse(url+str(course)+'/assignments?per_page=100', headers)
    assignments.sort(key=lambda assignment: (assignment['due_at'] == None, assignment['due_at']))
    return assignments 

def getAllAssignmentsStats(course, headers):
    assignments = getResponse(url+str(course)+'/analytics/assignments?per_page=100', headers)
    for assignment in assignments: 
        due_date = None
        if assignment['due_at'] != None: 
            due_date = datetime.strptime(assignment['due_at'], '%Y-%m-%dT%H:%M:%SZ')
            assignment['due_at'] = due_date
    # res.sort(key=lambda assignment: (assignment['due_at'] == None, assignment['due_at']))
    return assignments 

def getGradingProgress(course, assignment, headers): 
    submissions_url = url+course+'/assignments/'+str(assignment)+'/submission_summary'
    grading = getResponse(submissions_url, headers)
    return grading

def getScores(course, assignment, headers): 
    submissions_url = url+course+'/assignments/'+str(assignment)+'/submissions?per_page=50'
    submissions = getResponse(submissions_url, headers)
    return submissions

def textReport(course_name, course_num): 
    print('---' + course_name + '---\n\n')
    print('\n')
    

def getSubmissions(course, headers): 
    assignments = getAllAssignments(course, headers)
    for assignment in assignments:
        name = assignment['name']
        if assignment['has_submitted_submissions']: 
            submissions = getScores(course, assignment['id'], headers)
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

def writeGradingProgress(f, course_num, section, headers):
    f.write(r"\subsection{Section " + str(section) + "}" + "\n")
    # -- Set up figure data
    assignments = getAllAssignmentsStats(course_num, headers)
    results = {}
    toReturn = []
    for assignment in assignments:
        toReturn.append(assignment)
        if assignment['min_score'] != None: 
            name = assignment['title']
            status = getGradingProgress(course_num, assignment['assignment_id'], headers)
            results[name] = list(status.values())
    category_names = ['graded', 'ungraded', 'not_submitted']
    # -- Create figure
    surveyGradingProgress(results, category_names)
    # -- Save figure
    figname = "Grading Progress - " + str(section)
    plt.savefig('tex/fig/'+figname+'.png', bbox_inches='tight', dpi=300)
    plt.clf() 
    # -- Insert figure into LaTeX
    f.write(r"\includegraphics[width=6in]{fig/"+figname+r".png}" + "\n")
    return toReturn

def writeAssignment(f, course_num, assignment_name, assignment_num, headers):
    f.write(r"\section{" + assignment_name + "}" + "\n")
    status = getGradingProgress(course_num, assignment_num, headers)
    f.write(r'' + str(status['graded']) + ' graded' + "\n")
    f.write(r'' + str(status['ungraded']) + ' ungraded' + "\n")
    f.write(r'' + str(status['not_submitted']) + ' unsumbitted' + "\n")

def writeOneGradingProgress(f, course_num, assignment_num, headers):
    status = getGradingProgress(course_num, assignment_num, headers)
    f.write(r'' + str(status['graded']) + ' graded' + "\n")
    f.write(r'' + str(status['ungraded']) + ' ungraded' + "\n")
    f.write(r'' + str(status['not_submitted']) + ' unsumbitted' + "\n")

def writeDistribution(f, course_num, assignment_name, max): 
    f.write(r"\subsection{Grading Distribution}" + "\n")
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
    figname = assignment_name+'_all'
    data = assignment_scores[assignment_name]
    axes[0].bar(data.keys(), data.values())
    fig.savefig('tex/fig/'+figname + '.png', bbox_inches='tight', dpi=300)
    # surveyDistribution(f, data, max, figname)

    plt.sca(axes[1])
    plt.xlim(-1, max + 1)
    plt.xticks(np.arange(0, max+1, st))
    plt.xlabel('Score')
    plt.ylabel('Frequency')
    figname = assignment_name+'_specific'
    data = section_scores[course_num][assignment_name]
    axes[1].bar(data.keys(), data.values())
    fig.savefig('tex/fig/'+figname + '.png', bbox_inches='tight', dpi=300)
    f.write(r"\includegraphics[width=6in]{fig/"+figname+r".png}" + "\n")
    # surveyDistribution(f, data, max, figname)
    plt.clf() 
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
    os.system("pdflatex -output-directory=tex "+latexFileName)

def writeFile(courses, course_num, course_name, section_num, headers): 
    start = time.perf_counter()
    print("Pulling submission data from Canvas API... ")
    for section, course in courses: 
        getSubmissions(course, headers)
    end = time.perf_counter()
    print(end - start, "s\n")
    Path("./tex/fig").mkdir(parents=True, exist_ok=True)
    latexFileName = "tex/" + course_name.replace(' ', '_') + ".tex"
    f = open(latexFileName, "w")
    setup(f, course_name)
    if course_num != None: 
        assignments = writeGradingProgress(f, course_num, section_num, headers)
        # if None, write all in one doc 
        for assignment in assignments: 
            if assignment['title'] in section_scores[course_num]: 
                if assignment['due_at'] != None:
                    due_date = '\n' + assignment['due_at'].strftime("%m/%d/%Y, %H:%M:%S")
                f.write(r'\linebreak' + "\n")
                f.write(r"" + due_date + "\n")
                writeAssignment(f, course_num, assignment['title'], assignment['assignment_id'], headers)
                if int(assignment['points_possible']) == 0: 
                    f.write(r"Current max score set to null." + "\n")
                    continue
                if assignment_scores[assignment['title']] == {}: 
                    f.write(r"No grade data." + "\n")
                    continue
                writeDistribution(f, course_num, assignment['title'], max)
    else: 
        f.write(r"\section{Grading Progress}" + "\n")
        start = time.perf_counter()
        print("Surveying grading progress from Canvas API... ")
        for section, course in courses: 
            assignments = writeGradingProgress(f, course, section, headers)
            course_num = course
        end = time.perf_counter()
        print(end - start, "s\n")
        start = time.perf_counter()
        print("Creating grade distribution bar charts... ")
        for assignment in assignments: 
            fig = plt.figure(figsize=(8,12))
            max = int(assignment['points_possible'])
            if max == 0: 
                continue
            f.write(r"\section{" + assignment['title'] + "}" + "\n")
            f.write(r"\begin{FlushLeft}" + "\n")
            if assignment['due_at'] != None:
                due_date = '\n' + assignment['due_at'].strftime("%m/%d/%Y, %H:%M:%S")
                f.write(r'\linebreak' + "\n")
                f.write(r"" + due_date + "\n")
            if assignment['title'] in assignment_scores: 
                if int(assignment['points_possible']) == 0: 
                    f.write(r"Current max score set to null." + "\n")
                    continue
                elif assignment_scores[assignment['title']] == {}: 
                    f.write(r"No grade data." + "\n")
                    continue
                else: 
                    writeOneDistribution(f, fig, course_num, 'All sections', assignment['title'], max, 1)
            else: 
                continue
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
                    writeOneDistribution(f, fig, course, 'Section ' + str(section), assignment['title'], max, index)
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
        end = time.perf_counter()
        print(end - start, "s\n")
    closeFile(f, latexFileName)