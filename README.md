# Drexel TMS API/Scraper

Drexel TMS API

An api to reference drexel tms and course catalog data
currently has 202235-45 for tms classes and has grad and undergrad course catalog data

`/class/{course_number}` gives you course information for 1 class

`/classes/term` gives you lists of classes matching the params

`/prereqs/{course_number}` gives you all prereqs paths for one class

`/postreqs/{course_number}` gives you classes that have this given course as a prereq

## Run locally
```sh
$ python -m venv .venv # create a virtual environment
$ pip install -r requirements.txt # install all requirements
$ uvicorn dtms.main:app --reload
```

## Run as prod service 
Create a systemd service by following this template and and replace as needed.

Put this file in `/etc/systemd/system/` as `dtms.service`

To auto start at boot: `sudo systemctl enable dtms.service`

To start: `sudo systemctl start dtms.service`

```
[Unit]
Description=Uvicorn Service for Your FastAPI App
After=network.target

[Service]
User={your_username}
Group={your_users_group}
WorkingDirectory={/path/to/dtms/root}
ExecStart={/path/to/dtms/root/.venv/bin/uvicorn} dtms.main:app --reload --host 0.0.0.0
Restart=always
SyslogIdentifier=dtms
Environment="PATH={/path/to/dtms/root/.venv/bin/}

[Install]
WantedBy=multi-user.target
```
