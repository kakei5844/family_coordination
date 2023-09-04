import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, and_

from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure Flask-SQLAlchemy to use sqlite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///home.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    birthday = db.Column(db.Date, nullable=False)

    def __init__(self, username, hash, name, birthday):
        self.username = username
        self.hash = hash
        self.name = name
        self.birthday = birthday

    def __repr__(self):
        return f"User: {self.username} User ID: {self.id} Birthday: {self.birthday}"

class Activity(db.Model):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    start = db.Column(db.DateTime, nullable=False) # DATE_FORMAT() when select https://learnsql.com/cookbook/how-to-change-datetime-formats-in-mysql/
    end = db.Column(db.DateTime, nullable=False)

    def __init__(self, title, start, end):
        self.title = title
        self.start = start
        self.end = end

    def __repr__(self):
        return f"Activity: {self.title} Start: {self.start} End: {self.end}"


class ShoppingList(db.Model):
    __tablename__ = "shoppinglist"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    creator_id = db.Column(db.ForeignKey('users.id'), nullable=False)
    bought = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Title: {self.title} Created by: {self.creator_id} bought?: {self.bought}"


class Who_bought(db.Model):
    __tablename__ = "who_boughts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    buyer_id = db.Column(db.ForeignKey('users.id'), nullable=True)
    item_id = db.Column(db.ForeignKey('shoppinglist.id'), nullable=False)
    pur_date = db.Column(db.DateTime, nullable=True)
    expense = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"Item: {self.item_id} Bought by: {self.buyer_id} at {self.expense} on {self.pur_date}"


with app.app_context():
    db.create_all()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show calendar"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        title = request.form.get("title")
        start_str = request.form.get("start")
        end_str = request.form.get("end")

        # Ensure title, start and end were input
        if (not title or not start_str or not end_str):
            return apology("must provide all info about the activity", 400)

        # Validate start and end time
        try:
            start = datetime.strptime(start_str, "%Y-%m-%dT%H:%M")
            end = datetime.strptime(end_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            return apology("invalid time", 400)
        except:
            return apology("Unexpected error", 400)

        # Remember activity
        new_activity = Activity(title=title, start=start, end=end)
        db.session.add(new_activity)
        db.session.commit()

        flash("Activity initiated!")
        return redirect("/")

    # Query database for birthdays
    bday_rows = db.session.execute(db.select(User.name, User.birthday)).all()
    bdays = [{'title': f"{row.name}'s birthday", 'rrule': {'dtstart': row.birthday.isoformat(), 'freq': 'yearly'}} for row in bday_rows]

    # Query database for activities
    activity_rows = db.session.execute(db.select(Activity.title, func.strftime('%Y-%m-%dT%H:%M:%S', Activity.start).label('start'), func.strftime('%Y-%m-%dT%H:%M:%S', Activity.end).label('end'))).all()
    activities = [{'title': row.title, 'start': row.start, 'end': row.end} for row in activity_rows]
    return render_template("calendar.html", bdays=bdays, activities=activities)


@app.route("/process", methods=["GET", "POST"])
@login_required
def process():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        data = request.get_json()
        shopping_list_new = ShoppingList(title=data['item'], creator_id=session['user_id'])
        db.session.add(shopping_list_new)
        db.session.commit()

        who_bought_new = Who_bought(item_id=shopping_list_new.id)
        db.session.add(who_bought_new)
        db.session.commit()
        return {'success': True}
    else:
        shoppingList_rows = db.session.execute(db.select(ShoppingList.title, User.name.label('creator'), ShoppingList.bought, ShoppingList.id).join(ShoppingList, User.id==ShoppingList.creator_id)).all()
        shoppingList_items = [{'item': row.title, 'creator': row.creator, 'checked': row.bought, 'id': row.id} for row in shoppingList_rows]
        for item in shoppingList_items:
            if item['checked']:
                purchase_data = db.session.execute(db.select(User.name.label('buyer'), Who_bought.expense, Who_bought.pur_date).join(ShoppingList, Who_bought.item_id==item['id']).join(User, User.id==Who_bought.buyer_id)).first()
                item['buyer'] = purchase_data.buyer
                item['expense'] = purchase_data.expense
                item['pur_date'] = purchase_data.pur_date
        return jsonify(shoppingList_items)


@app.route("/delete_item", methods=["POST"])
@login_required
def delete_item():
    item_id_delete = int(request.get_json()['id'])
    item_delete = db.session.scalars(db.select(ShoppingList).filter_by(id=item_id_delete)).first()
    db.session.delete(item_delete)
    who_bought_delete = db.session.scalars(db.select(Who_bought).filter_by(item_id=item_id_delete)).first()
    db.session.delete(who_bought_delete)
    db.session.commit()
    return {'success': True}


@app.route("/checked_item", methods=["POST"])
@login_required
def checked_item():
    item_id_check = request.get_json()
    item_check = db.session.scalars(db.select(ShoppingList).filter_by(id=int(item_id_check['id']))).first()
    who_bought = db.session.scalars(db.select(Who_bought).filter_by(item_id=int(item_id_check['id']))).first()
    if (item_check.bought):
        item_check.bought = False
        who_bought.buyer_id = None
        who_bought.expense = None
        who_bought.pur_date = None
    else:
        try:
            who_bought.expense = float(item_id_check['expense'])
        except ValueError:
            flash("Please enter a valid expense")
            return {'success': False}
        item_check.bought = True
        who_bought.buyer_id = session['user_id']
        who_bought.pur_date = datetime.now()

    db.session.commit()
    return {'success': True}


@app.route("/shoppinglist")
@login_required
def shoppinglist():
    """Show shopping list"""
    return render_template("shopping_list.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        with app.app_context():
            rows = db.session.execute(db.select(User).filter_by(username=request.form.get("username"))).all()

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0][0].hash, request.form.get("password")):
                return apology("invalid username and/or password", 403)

            # Remember which user has logged in
            session["user_id"] = rows[0][0].id

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    return apology("TODO quote")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Forget any user_id
        session.clear()

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        dd = request.form.get("dd")
        mm = request.form.get("mm")
        yyyy = request.form.get("yyyy")
        name = request.form.get("name")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        if not password:
            return apology("must provide password", 400)

        # Ensure confirming password was submitted
        if not confirmation:
            return apology("must type your password again", 400)

        # Ensure name was submitted
        if not name:
            return apology("must provide your name", 400)

        # Ensure birthday was submitted
        if (not dd or not mm or not yyyy):
            return apology("must provide your birthday", 400)

        # Validate birthday
        try:
            birthday=date(int(yyyy), int(mm), int(dd))
        except ValueError:
            return apology("invalid birthday", 400)

        # Ensure password and confirmation match
        if password != confirmation:
            return apology("those password didn't match", 400)

       # Ensure the username hasn't be taken
        if len(db.session.execute(db.select(User).filter_by(username=username)).all()) == 1:
            return apology("username already taken", 400)

        # Remember registrant
        new_user = User(username=username, hash=generate_password_hash(password), birthday=birthday, name=name)
        db.session.add(new_user)
        db.session.commit()

        # Remember which user has logged in
        user_db = db.session.execute(db.select(User).filter_by(username=username)).first()[0]
        session["user_id"] = user_db.id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/setting", methods=["GET", "POST"])
@login_required
def setting():
    """Change password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure old password was submitted
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm = request.form.get("confirm")

        # Ensure old password was submitted
        if not old_password:
            return apology("Missing Old Password", 400)

        # Ensure password was submitted
        elif not new_password:
            return apology("Missing New Password", 400)

        # Ensure confirming password was submitted
        elif not confirm:
            return apology("must type your new password again", 400)

        # Get the user id
        user_id = session["user_id"]

        # Query database for the User Object
        user_row = db.session.execute(db.select(User).filter_by(id=user_id)).first()[0]

        # Ensure old password is correct
        if not check_password_hash(user_row.hash, old_password):
            return apology("Old password is not correct", 400)

        # Ensure new password and confirmation match
        if new_password != confirm:
            return apology("those new passwords didn't match", 400)

        # Update hash
        user_row.hash = generate_password_hash(new_password)
        db.session.commit()

        # flash message
        flash("Password Changed!")

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("setting.html")