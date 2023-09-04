# Family Coordination Web App
#### Video Demo:  <https://youtu.be/fyykub8g9Z8>
#### Description:

## Overview
This web-based application is used for better coordination among family members. Calendar Page reminds members of birthdays and family gatherings, whereas Shopping List Page keeps track on what item the family needs to buy.

## Prerequisites

1. Installing Python:

    Visit the official Python website at https://www.python.org/downloads/. ↗Download the latest version of Python for your operating system (e.g., Windows, macOS, or Linux).Run the installer and follow the installation instructions.Make sure to check the box that says "Add Python to PATH" during the installation.

2. Installing Flask, Flask-SQLAlchemy, Flask session, Werkzeug

    Open a terminal or command prompt. Install Flask and Flask-SQLAlchemy by running the following command:

    `pip3 install flask flask-sqlalchemy`

   Install Werkzeug by running this:

    `pip3 install werkzeug`

   Install Flask session by running this:

    `pip3 install flask-session`

## To Run the Web Application Locally

1. Make sure you have the above prerequisites installed.

2. Open a terminal or command prompt and navigate to the root directory of the Flask application.

3. Set the Flask app environment variable. In the terminal, execute the appropriate command based on your operating system:

    For Windows (Command Prompt):

    `set FLASK_APP=app.py`

    For macOS/Linux:

    `export FLASK_APP=app.py`

    (Optional) If your Flask application uses environment variables, make sure to set them accordingly before running the server.

4. Start the Flask development server by running the following command:

    `flask run`


You should see output similar to the following:


* Running on [http://127.0.0.1:5000/ ↗](http://127.0.0.1:5000/) (Press CTRL+C to quit)
Open your web browser and visit http://127.0.0.1:5000/ or http://localhost:5000/ to access the locally running Flask web application.

To stop the Flask development server, press CTRL+C in the terminal or command prompt where the server is running.


## Directory Structure

```
|____flask_session
| |____dd825763530c96adee7295cdb71fa935
| |____0a6d6a9b6ee7abcfea2bdd8885b8bba2
| |____bebadf5da5efaf34568ce4c370e8b929
| |____16c497939ff0c62a4585d33731b4c115
| |____2029240f6d1128be89ddc32729463129
| |____594a7e15175f6df870ec4f22a779ee1f
|____static                             # Static assets (CSS, JS)
| |____styles.css
| |____shoppinglist.js
|____requirements.txt                   # Dependencies required for the project
|____helpers.py
|____instance
| |____home.db
|____README.md                          # Project documentation
|____app.py                             # Flask application entry point
|____templates                          # HTML templates
| |____apology.html
| |____calendar.html
| |____shopping_list.html
| |____setting.html
| |____login.html
| |____layout.html
| |____register.html

```

## Specific Usage Details
* Registration

    When a new user registers for an account, he/she is required to input his/her name, login information (username and password) and birthday. Both client-side and server-side validations are done.

* Calendar

    The calendar shows your family activities and all members' birthdays so that you won't forget anyone of them! The top-right buttons enable you to navigate to different months whereas the today button brings you back to the current month. Scrolling down, you will see a form to add a new activity. Type the activity name and time such that it will be added to the back-end database. The page will then automatically reload and the new activity will show up.

* Shopping List

    When you realize anything is missing in your house, type the item name in the textbox and click Add. Then it will be added to the table below. On the other hand, if you buy any item in the list and want to tell all other members immediately, go check the checkbox of that item. A pop-up will then ask you how much it is. After answering it, data will be updated. It will show that this item is purchased by "your name" and the amount paid. If any item is wrongly added to the list, click the delete button.
