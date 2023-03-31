# Drexel TMS API/Scraper

WIP Drexel TMS API

An api to reference drexel tms and course catalog data
currently has 202235-45 for tms classes and has grad and undergrad course catalog data

`/class/{course_number}` gives you course information for 1 class

`/classes/term` gives you lists of classes matching the params

`/prereqs_for/{course_number}` gives you all prereqs paths for one class

`/postreq/{course_number}` gives you classes that have this given course as a prereq

## Run locally
```sh
$ poetry shell
$ poetry install
$ uvicorn dtms.main:app --reload
```
