# Poodle

A learning management system created with Django.
This project was made for my major SDD work, and later revised to add additional features and testing

## Setup

### Docker Setup (Recommended)
1.  `git clone https://github.com/omackenzie/poodle`
2.  `cd poodle`
3.  `docker-compose up --build`
4.  Navigate to http://localhost:8000 in your browser

A test admin user is automatically created with:
- Username: `admin`
- Password: `password`

### Manual Setup
1.  `git clone https://github.com/omackenzie/poodle`
2.  Install the required modules by running `pip install -r requirements.txt` (create a virtualenv first if you wish)
3.  Set up a PostgreSQL database and configure the database settings
4.  Run `python manage.py migrate` to set up the database
5.  Run `python manage.py createsuperuser` to create an admin account
6.  Run `python manage.py runserver` to start the server, then navigate to http://localhost:8000 in the browser

## Features
 - Creating classes and assigning teachers and students to those classes
 - Teachers can create assignments which students can view and upload files to
 - These assignments have individual sections with their own separate upload option
 - Teachers can then view all submissions from students in their class
 - Custom styling and the ability to add images for assignment and sections using the rich text editor Quill

## Setup Guide
 - The Docker setup automatically creates an admin account with credentials `admin:password`
 - Navigate to the admin panel by clicking your profile in the top right and clicking "admin panel" in the dropdown, or by going to http://localhost:8000/admin
 - Create any teachers or students you want to use, then create a class, assigning students as required to that class
 - You can then go back to the main page and sign in using the teacher or student accounts you created
 - A tutorial on the features of the site is available by clicking your profile in the top right and clicking help in the dropdown

## Testing and linting

### With Docker (Recommended)
 - To run tests: `docker-compose exec web python manage.py test`
 - To check coverage: `docker-compose exec web coverage run manage.py test && docker-compose exec web coverage report -m`
 - To run linting: `docker-compose exec web ruff check .`
 - To run import sorting: `docker-compose exec web isort .`

**Convenient shortcut:** Use the development script for common tasks:
 - `./dev.sh test` - Run tests
 - `./dev.sh coverage` - Run coverage
 - `./dev.sh lint` - Run linting
 - `./dev.sh format` - Run import sorting
 - `./dev.sh all` - Run all checks

### Manual Setup
 - To run tests, execute `python manage.py test`
 - To check coverage, execute `coverage run manage.py test`, then `coverage report -m`
 - To install the necessary tools for linting, run `pip install -r dev-requirements.txt`
 - Linting uses ruff, `ruff check .`
 - Import ordering is done with isort, `isort .`

## TODO
 - Quizzes

## Screenshots
![Home](https://user-images.githubusercontent.com/30273552/188298163-8958436e-68ae-46dc-9f7b-439ba2d786f5.PNG)
![Assignment](https://user-images.githubusercontent.com/30273552/188298375-56d00f29-4e25-45e8-a793-270dec06efc5.PNG)
