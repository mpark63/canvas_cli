import os
from pathlib import Path
from helper import *

# Create directory tex/fig
# Final PDF will be in the tex directory
Path("./tex/fig").mkdir(parents=True, exist_ok=True)
Path("./pdf").mkdir(parents=True, exist_ok=True)

# Create and/or Open LaTex file
assignment = "ExampleCourse"
latexFileName = "tex/"+assignment+".tex"
f = open(latexFileName, "w")

# Build the LaTex preamble: https://www.overleaf.com/learn/latex/Learn_LaTeX_in_30_minutes#The_preamble_of_a_document
# Use r before the string to preserve the brackets, which should be written to the text file.
# \n moves to the next line in the text file
### It might be worth writing a wrapper function for f.write that will automatically add the r in front of the text string and the +"\n" at the end 
f.write("\documentclass{article}\n")
f.write(r"\usepackage[hidelinks]{hyperref}" + "\n")
f.write(r"\usepackage{graphicx}" + "\n")
f.write(r"\usepackage{booktabs}" + "\n")  # for df.to_latex()
f.write(r"\usepackage{caption}" + "\n")
f.write(r"\usepackage[top=1in, bottom=1in, left=1in, right=1in, "+
        "marginparsep=0.15in]{geometry}" + "\n")
f.write(r"\title{" + assignment + r" Report}" + "\n")
f.write(r"\date{}" + "\n")
f.write(r"\author{}" + "\n")
f.write(r"\begin{document} \maketitle" + "\n")

###############################################################################
# Write the body of the document
f.write(r"\section{This is a section heading}" + "\n")
f.write(r"This is some text at the beginning of a section." + "\n")
f.write(r"\subsection{This is a subsection}" + "\n")
f.write(r"\subsection{This is another subsection}" + "\n")

#=====================================================================
# This code would conveniently write a dataframe to a LaTeX table
# https://www.tutorialspoint.com/python_pandas/python_pandas_dataframe.htm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# -- Data
course_num = '13697'
assignments = getAssignmentIds(course_num)
results = {}
for assignment in assignments:
    name = getAssignmentName(course_num, assignment)
    status = getGradingProgress(course_num, assignment)
    results[name] = list(status.values())
category_names = ['graded', 'ungraded', 'not_submitted']

print(results)

def survey(results, category_names):
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.get_cmap('RdYlGn')(
        np.linspace(0.15, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(9.2, 5))
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
            ax.text(x, y, str(int(c)), ha='center', va='center',
                    color=text_color)
    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')
    return fig, ax

survey(results, category_names)
# -- Save figure
figname = "Grading Progress"
plt.savefig('tex/fig/'+figname+'.png', bbox_inches='tight', dpi=300)
# -- Insert figure into LaTeX
fwidth = 6   # figure width in inches
f.write(r"\includegraphics[width="+str(fwidth)+"in]{fig/"+figname+r".png}\\"+"\n")

#======================================================================
# Finalize and close the LaTex document
f.write("\end{document}")
f.close()
###############################################################################

# Compile the LaTeX text file into a pdf
os.system("pdflatex -output-directory=tex "+latexFileName)
#os.system("pdflatex -output-directory=tex "+latexFileName) # run 2nd time for table of contents