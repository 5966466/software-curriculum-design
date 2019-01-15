# software curriculum design
Xxc worked with Gy and Lbl, who designed a fantastic front-end pages.
## The function of this web application
This is a log file management system, which can help you manage some log files which store in you own server.
## How to run this
We use Python 3.7 and Django 2.1 to develop this web application. Please ensure that you have these basic modules.

If you have installed conda3 in your computer, you can install like this 

`conda install django`

or use pip to install 

`pip install django`

For detail, please see the website of django: <a href="https://www.djangoproject.com"> Django website </a>

Having downloaded, to run this in your computer, please open the project dir in your terminal and input:

`python manage.py makemigrations register`

`python manage.py makemigrations data`

`python manage.py migrate`

`python manage.py runserver`

Then, you can run this project at your localhost in port 8000 for default.
