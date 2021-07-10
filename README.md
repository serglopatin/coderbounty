<img src="http://www.coderbounty.com/static/images/coder-bounty-logo.9e4b0ca1564d.png" alt="coder bounty logo"/>

#### Join us on Slack:

[![Slack Status](https://coderbounty-slackin.herokuapp.com/badge.svg)](https://coderbounty-slackin.herokuapp.com) [![Codacy Badge](https://api.codacy.com/project/badge/grade/e7dd6887193546529274f78fc0c9993b)](https://www.codacy.com/app/sean_2/coderbounty) [![Codeship Status](https://codeship.com/projects/79d8f370-6de1-0133-9c97-6eccd6fcb9f2/status?branch=master)](https://codeship.com/projects/115741)


To contribute, take an issue, and submit a pull request with the issue number in it win bounty!

#### Google Drive folder:
###### With design docs and notes. 
<a href="https://drive.google.com/folderview?id=0B27eQuixxEoiNWhIT2ZQeVhJaW8&usp=sharing">
<img width="77" src="http://icons.iconarchive.com/icons/alecive/flatwoken/512/Apps-Google-Drive-icon.png" alt="google drive icon"/> 
https://goo.gl/xvb6CI
</a>

<a href="http://burndown.io/#Coderbounty/coderbounty/summary/90">90 day burndown chart</a>

#### Notes on getting started:
###### Run the server with:

 `python manage.py runserver`

The first time you may need to run:
- `If postgresql is not installed`, `brew install postgresql` (mac), `sudo apt-get install postgresql` (Ubuntu)
- `cd coderbounty`
- `virtualenv venv`
- `venv\Scripts\activate` (windows)
- `source venv/bin/activate` (mac)
- `pip install -r requirements.txt`
- `python manage.py migrate`
- `python manage.py createsuperuser` (then go to /admin) and add filler information for social auth accounts
- `python manage.py runserver`

#### License:

Coderbounty.com is a web app to accelerate software development by placing bounties on coding tasks.
Copyright (C) 2011  Coderbounty, Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
