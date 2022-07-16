# Canvas CLI

Command line tool that creates seamless reports on course data from the Canvas LMS API.

### Features

- Select from your courses and sections
- Generate summary LaTeX PDF reports on individual or multiple section(s)
- View grade distributions and statistics for a certain assignment
- Compare grading progress between sections

For a sample document, please see ```EN.500.130_Biomedical_Engineering_Innovation_Section_4```. 

### Note on tech

Canvas CLI depends on a number of open source projects such as TeXShop, asyncio, matplotlib, and inquirer among others. Clone the repository and within the /canvas_cli directory, install the dependencies by running: ```pipenv install```. Should you encounter the ```Too many open files``` error, please run ```ulimit -Sn 10000```. 

### Tutorial

- To authenticate, you will need a Canvas [access token](https://community.canvaslms.com/t5/Canvas-Developers-Group/A-Simple-Python-GET-Script/ba-p/273742)
- Configure the config file with your institution's url, courses, and sections

```py
# sections.py
# replace the url with your school's canvas website  
url = "https://<yourschool>.instructure.com/api/v1/courses/"

# define the courses dictionary by course name, section number, and canvas ids  
courses = {
    "<course_name>": {
        'sections': [1, 2, 3],
        'ids': {
            1: '13232',
            2: '13233',
            3: '13234',
        }
    },
    "<course_name>": { ... },
}
```

- Finally, run ```python3 canvasCLI.py``` to select options and generate your document

A successful run will look as such:

```sh
> user@user canvas_cli % python3 canvasCLI.py
Canvas access code: 12394~SdDZzwzWSvytpvQXsdkDSKaLdsk3fAkjf9dfsnc4Sknal5skjd

[?] Welcome, choose an option : Find your course
 > Find your course
   Enter course id

[?] Choose a course : EN.500.130 Biomedical Engineering Innovation
   EN.500.109 What is Engineering?
 > EN.500.130 Biomedical Engineering Innovation
   CO.EN.BMEI.100 Teacher Training
   CO.EN.EEI.100 Teacher Training

[?] Choose a section : 4
   1
   2
   3
 > 4
   5
   All sections
   
Pulling submission data from Canvas API... 
13.974240150999998 s

Surveying grading progress from Canvas API... 
3.8051256249999987 s

Creating grade distribution bar charts... 
17.099024909 s

This is pdfTeX, Version 3.141592653-2.6-1.40.24 (TeX Live 2022) (preloaded format=pdflatex)
 restricted \write18 enabled.
entering extended mode

Successfully generated	tex/EN.500.130_Biomedical_Engineering_Innovation_Section_4.tex!
```
