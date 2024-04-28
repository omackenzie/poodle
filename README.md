# Poodle

An assignment submission system created with Django. This project was made for my major SDD work.

## Setup
1.  `git clone https://github.com/omackenzie/poodle`
2.  Install the required modules by running `pip install -r requirements.txt` (create a virtualenv first if you wish)
3.  Run `python manage.py runserver` to start the server, then navigate to localhost:8000 in the browser

## Features
 - Creating classes and assigning teachers and students to those classes
 - Teachers can create assignments which students can view and upload files to
 - These assignments have individual sections with their own separate upload option
 - Teachers can then view all submissions from students in their class
 - Custom styling and the ability to add images for assignment and sections using the rich text editor Quill

## Setup Guide
 - First sign into the admin account using the credentials admin:password then navigate to the admin panel (either by clicking your profile in the top right and clicking "admin panel" in the dropdown, or by going to the URL localhost:8000/admin
 - Create any teachers or students you want to use, then create a class, assigning students as required to that class
 - You can then go back to the main page and sign in using the teacher or student accounts you created
 - A tutorial on the features of the site is available by clicking your profile in the top right and clicking help in the dropdown

## Testing and linting
 - To run tests, execute `python manage.py test`
 - To install the necessary tools for linting, run `pip install -r dev-requirements.txt`
 - Linting uses ruff, `ruff check .`
 - Import ordering is done with isort, `isort .`

## TODO
 - Add additional unit tests and achieve 100% code coverage

## Screenshots
![Home](https://user-images.githubusercontent.com/30273552/188298163-8958436e-68ae-46dc-9f7b-439ba2d786f5.PNG)
![Assignment](https://user-images.githubusercontent.com/30273552/188298375-56d00f29-4e25-45e8-a793-270dec06efc5.PNG)
