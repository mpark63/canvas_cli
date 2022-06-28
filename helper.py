import requests
import json
from pprint import pprint
import pandas as pd
from tabulate import tabulate
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

url = "https://jhu.instructure.com/api/v1/courses/"

headers = {'Authorization': 'Bearer 13044~SGDZzzWSvytpvQXcIEhtzqCIdSq4I0CtUcbqVaI8mK1GBihXsD9sm2yJ8qjtYa6Y'}

def getResponse(url): 
    s = requests.Session() 
    res = s.get(url, headers = headers)
    parsed = json.loads(res.content)
    return parsed

def getAssignmentGroups(course): 
    groups_url = url+str(course)+'/assignment_groups'
    groups = getResponse(groups_url)
    res = []
    for assignment_group in groups: 
        res.append({
            "id": assignment_group['id'],
            "name": assignment_group['name']
        })
    return res 

def getQuizStats(course): 
    quizzes_url = url+str(course)+'/quizzes'
    quizzes = getResponse(quizzes_url)
    data = {}
    ids = []
    names = []
    averages = []
    stdevs = []

    for quiz in quizzes: 
        ids.append(quiz['id'])
        names.append(quiz['title'])
        stats = getResponse(quiz['quiz_statistics_url'])
        average = stats['quiz_statistics'][0]['submission_statistics']['score_average']
        averages.append(average)
        stdev = stats['quiz_statistics'][0]['submission_statistics']['score_stdev']
        stdevs.append(stdev)
    data["Id"] = ids
    data["Title"] = names
    data["Mean"] = averages
    data["StDev"] = stdevs
    df = pd.DataFrame(data)
    print(tabulate(df, headers = 'keys', tablefmt = 'simple'))

def getAllAssignments(course):
    assignment_groups = getAssignmentGroups(course)
    res = []
    for group in assignment_groups: 
        assignments = getAssignmentsByGroup(course, group[id])
        for assignment in assignments: 
            res.append(assignment)
    res.sort(key=lambda assignment: (assignment['due_at'] == None, assignment['due_at']))
    return res 

def getAllAssignmentsByGroup(course):
    assignment_groups = getAssignmentGroups(course)
    res = []
    for group_id in assignment_groups: 
        assignments = getAssignmentsByGroup(course, group_id)
        assignments.sort(key=lambda assignment: (assignment['due_at'] == None, assignment['due_at']))
        res.append(assignments)
    return res 

def getAssignmentsByGroup(course, group):
    assignments_url = url+str(course)+'/assignment_groups/'+str(group)+'/assignments'
    assignments = getResponse(assignments_url)
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

def getGradingProgress(course, assignment): 
    submissions_url = url+course+'/assignments/'+str(assignment)+'/submission_summary'
    grading = getResponse(submissions_url)
    return grading

def displayGradingProgress(course, assignments): 
    results = {}
    category_names = ['graded', 'ungraded', 'not_submitted']
    for assignment in assignments:
        name = assignment['name'] + '\n' + assignment['due_at'].strftime("%m/%d/%Y, %H:%M:%S")
        status = getGradingProgress(course, assignment['id'])
        results[name] = list(status.values())
    surveyGradingProgress(results, category_names)
    plt.show()

def surveyGradingProgress(results, category_names):
    # https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/horizontal_barchart_distribution.html
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.get_cmap('RdYlGn')(
        np.linspace(0.3, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        ax.barh(labels, widths, left=starts, height=0.5,
                label=colname, color=color)
        xcenters = starts + widths / 2

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        for y, (x, c) in enumerate(zip(xcenters, widths)):
            if c == 0:  
                continue
            ax.text(x, y, str(int(c)), ha='center', va='center',
                    color=text_color)
    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')
    return fig, ax