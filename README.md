# World Values Data parser

A data processing rig for the [World Values Survey](http://www.worldvaluessurvey.org/wvs.jsp). Currently tested only with WVS Wave 6 (2010-2014).

Have a Mac and need help getting the requirements installed? [Read our guide](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html)!

# Installation

## System requirements

* bash
* Python + pip
* PostgreSQL

## Python requirements


Install project requirements (preferably in a virtualenv):

```
pip install -r requirements.txt
```

## Download the data

The data cannot be redistributed, so you'll have to go [download it](http://www.worldvaluessurvey.org/WVSDocumentationWV6.jsp). Follow the *WV6_Data_ascii_delimited_v_2015_04_18 (delimited with comma)* link, unzip the file, and copy `WV6_Data_ascii_v_2015_04_18.dat` into this projects `data` folder.

# Processing all the data

To import the data and summarize it the way we do, run:

```
./process.sh
```

This will generate summary output for all the questions NPR analyzed in our reporting. The output will go in the `output` directory in CSV format.

# Import the data and process yourself

First, run the importer:

```
./import.sh
```

Now, you can create summaries for individual questions by calling:

```
./summarize_questions.py <question_id>
```

So if you were interested in the responses per-country to question v52 (*"A university education is more important for a boy than for a girl."*), you would run:

```
./summarize_questions.py v52
```

The summary output will be in `output/v52.csv`.

You can pass multiple questions, just separate them with space:

```
./summarize_questions.py v52 v54 v60
```
