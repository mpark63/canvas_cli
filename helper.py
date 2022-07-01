import requests
import json
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
headers = {'Authorization': "Bearer 13044~SGDZzzWSvytpvQXcIEhtzqCIdSq4I0CtUcbqVaI8mK1GBihXsD9sm2yJ8qjtYa6Y"}
url = "https://jhu.instructure.com/api/v1/courses/"

def getCourses(headers): 
    return getResponse("https://jhu.instructure.com/api/v1/courses", headers)

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

# def getQuizStatsAcrossSections(assignments): 
#     # TODO

def getRecentAssignmentsStats(course, headers): 
    assignments = getResponse(url+str(course)+'/analytics/assignments', headers)
    data = {}
    ids = []
    names = []
    due_dates = []
    first = []
    second = []
    third = []
    for assignment in assignments: 
        due_date = None
        if assignment['due_at'] != None: 
            due_date = datetime.strptime(assignment['due_at'], '%Y-%m-%dT%H:%M:%SZ')
        if assignment['min_score'] != None: 
            ids.append(assignment['assignment_id'])
            names.append(assignment['title'])
            due_dates.append(assignment['due_at'])
            first.append(assignment['first_quartile'])
            second.append(assignment['median'])
            third.append(assignment['third_quartile'])
    data["Id"] = ids
    data["Title"] = names
    data["Due"] = due_dates
    data["25%"] = first
    data["50%"] = second
    data["75%"] = third
    df = pd.DataFrame(data)
    print(tabulate(df, headers = 'keys', tablefmt = 'simple'))

def getRecentAssignmentsStatsAcrossCourses(assignments): 
    data = {}
    ids = []
    names = []
    due_dates = []
    first = []
    second = []
    third = []
    for assignment in assignments: 
        if assignment['min_score'] != None: 
            ids.append(assignment['id'])
            names.append(assignment['name'])
            due_dates.append(assignment['due_at'])
            first.append(assignment['first_quartile'])
            second.append(assignment['median'])
            third.append(assignment['third_quartile'])
    data["Id"] = ids
    data["Title"] = names
    data["Due"] = due_dates
    data["25%"] = first
    data["50%"] = second
    data["75%"] = third
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

def getAssignmentsByGroup(course, group, headers):
    assignments_url = url+str(course)+'/assignment_groups/'+str(group)+'/assignments?order_by=due_at'
    assignments = getResponse(assignments_url, headers)
    res = []
    for assignment in assignments: 
        due_date = None
        if assignment['due_at'] != None: 
            due_date = datetime.strptime(assignment['due_at'], '%Y-%m-%dT%H:%M:%SZ')
        res.append({
            "id": assignment['id'], 
            "due_at": due_date, 
            "name": assignment['name']
        })
    return res
    # print(json.dumps(parsed, indent=4, sort_keys=True))

def getGradingProgress(course, assignment, headers): 
    submissions_url = url+course+'/assignments/'+str(assignment)+'/submission_summary'
    grading = getResponse(submissions_url, headers)
    return grading

def getScores(course, assignment, headers): 
    submissions_url = url+course+'/assignments/'+str(assignment)+'/submissions?per_page=50'
    submissions = getResponse(submissions_url, headers)
    return submissions

def displayGradingProgress(course, assignments, headers): 
    results = {}
    category_names = ['graded', 'ungraded', 'not_submitted']
    for assignment in assignments:
        due_date = ''
        if assignment['due_at'] != None: 
            due_date = '\n' + assignment['due_at'].strftime("%m/%d/%Y, %H:%M:%S")
        name = assignment['name'] + due_date
        status = getGradingProgress(str(course), assignment['id'], headers)
        results[name] = list(status.values())
    surveyGradingProgress(results, category_names)
    plt.show()

def textReport(course_name, course_num): 
    print('---' + course_name + '---\n\n')
    print('\n')
    

def getSubmissions(course, course_num): 
    assignments = getAllAssignments(course, headers)
    results = {}
    for assignment in assignments:
        if assignment['has_submitted_submissions']: 
            name = assignment['name']
            submissions = getScores(course, assignment['id'], headers)
            for submission in submissions:
                score = submission['score']
                if score == None: 
                    continue
                assignment_scores[name] = assignment_scores.get(name, {})
                assignment_scores[name][score] = assignment_scores[name].get(score, 0) + 1
                if assignment['course_id'] == int(course_num): 
                    section_scores[name] = section_scores.get(name, {})
                    section_scores[name][score] = section_scores[name].get(score, 0) + 1

def setup(f, course_name): 
    f.write("\documentclass{article}\n")
    f.write(r"\usepackage[hidelinks]{hyperref}" + "\n")
    f.write(r"\usepackage{graphicx}" + "\n")
    f.write(r"\usepackage{booktabs}" + "\n")  # for df.to_latex()
    f.write(r"\usepackage{caption}" + "\n")
    f.write(r"\usepackage{subfig}" + "\n")
    f.write(r"\usepackage[top=1in, bottom=1in, left=1in, right=1in, "+
            "marginparsep=0.15in]{geometry}" + "\n")
    f.write(r"\title{" + course_name + r" Grading Report}" + "\n")
    f.write(r"\date{"+ date.today().strftime("%m/%d/%Y") + r"}" + "\n")
    f.write(r"\author{}" + "\n")
    f.write(r"\begin{document} \maketitle" + "\n")

def writeGradingProgress(f, course_num, headers):
    f.write(r"\section{Grading Progress}" + "\n")
    # -- Set up figure data
    assignments = getAllAssignmentsStats(course_num, headers)
    results = {}
    toReturn = []
    for assignment in assignments:
        if assignment['min_score'] != None: 
            toReturn.append(assignment)
            name = assignment['title']
            status = getGradingProgress(course_num, assignment['assignment_id'], headers)
            results[name] = list(status.values())
    category_names = ['graded', 'ungraded', 'not_submitted']
    # -- Create figure
    surveyGradingProgress(results, category_names)
    # -- Save figure
    figname = "Grading Progress"
    plt.savefig('tex/fig/'+figname+'.png', bbox_inches='tight', dpi=300)
    # -- Insert figure into LaTeX
    fwidth = 6   # figure width in inches
    f.write(r"\includegraphics[width="+str(fwidth)+"in]{fig/"+figname+r".png}\\"+"\n")
    plt.clf() 
    return toReturn

def writeAssignment(f, course_num, assignment_name, assignment_num):
    f.write(r"\section{" + assignment_name + "}" + "\n")
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
    data = section_scores[assignment_name]
    axes[1].bar(data.keys(), data.values())
    fig.savefig('tex/fig/'+figname + '.png', bbox_inches='tight', dpi=300)
    fwidth = 6   # figure width in inches
    f.write(r"\includegraphics[width="+str(fwidth)+"in]{fig/"+figname+r".png}\\")
    # surveyDistribution(f, data, max, figname)
    plt.clf() 
    mean_all = mean(assignment_scores[assignment_name])
    mean_spec = mean(section_scores[assignment_name])
    std_all = std(assignment_scores[assignment_name], mean_all) ** .5
    std_spec = std(assignment_scores[assignment_name], mean_spec) ** .5
    f.write(r'Average: ' + str("{:.2f}".format(mean_all)) + "\n")
    f.write(r'Average: ' + str("{:.2f}".format(mean_spec)) + "\n")
    f.write(r'\linebreak' + "\n")
    f.write(r'Standard deviation: ' + str("{:.2f}".format(std_all)) + "\n")
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
    f.write("\end{document}")
    f.close()
    os.system("pdflatex -output-directory=tex "+latexFileName)

def writeFile(courses, course_num, course_name, headers): 
    for course in courses: 
        getSubmissions(course, course_num)
    Path("./tex/fig").mkdir(parents=True, exist_ok=True)
    latexFileName = "tex/" + course_num + ".tex"
    f = open(latexFileName, "w")
    setup(f, course_name)
    assignments = writeGradingProgress(f, course_num, headers)
    for assignment in assignments: 
        if assignment['title'] in section_scores: 
            max = int(assignment['points_possible'])
            if max == 0: 
                continue
            writeAssignment(f, course_num, assignment['title'], assignment['assignment_id'])
            writeDistribution(f, course_num, assignment['title'], max)
    closeFile(f, latexFileName)