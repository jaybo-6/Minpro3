from flask import Flask, render_template, request, redirect, session
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId  # Import ObjectId from bson
import datetime
import json  

current_date = datetime.date.today()
print(current_date)

app = Flask(__name__)
app.secret_key = '9663062483afbc071040aa71d6cb7933' 

# Initialize MongoDB client and database 
client = MongoClient("mongodb+srv://flaskdb:ypO42J2mw2N4NbY4@cluster0.axkqqxz.mongodb.net/?retryWrites=true&w=majority")
db = client.expense_tracker

# Define the custom 'ObjectId' route converter
from werkzeug.routing import BaseConverter

class ObjectIdConverter(BaseConverter):
    def to_python(self, value):
        return ObjectId(value)

    def to_url(self, value):
        return str(value)

app.url_map.converters['ObjectId'] = ObjectIdConverter

# Pydantic model for user registration
class UserRegistrationModel(BaseModel):
    username: str
    email: str
    password: str

# Pydantic model for adding expenses
class ExpenseModel(BaseModel):
    username: str
    date: str
    expensename: str
    amount: float
    paymode: str
    category: str

@app.route("/home")
def home():
    return render_template("homepage.html")

@app.route("/")
def add():
    return render_template("home.html")

# SIGN-UP OR REGISTER
@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route('/register', methods=['POST'])
def register():
    user_data = request.form.to_dict()
    registration_data = UserRegistrationModel(**user_data)
    
    # Save the user registration data to MongoDB
    users_collection = db.users
    users_collection.insert_one(registration_data.model_dump())
    
    msg = 'You have successfully registered!'
    return render_template('signup.html', msg=msg)

# LOGIN PAGE
@app.route("/signin")
def signin():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Validate the user's credentials from MongoDB
    users_collection = db.users
    user = users_collection.find_one({'username': username, 'password': password})

    if user:
        session['loggedin'] = True
        session['username'] = username
        return redirect('/home')
    else:
        msg = 'Incorrect username / password!'
        return render_template('login.html', msg=msg)

# ADDING DATA
@app.route("/add")
def adding():
    return render_template('add.html')

@app.route('/addexpense', methods=['POST'])
def addexpense():
    expense_data = request.form.to_dict()
    expense_data['username'] = session.get('username')  # Store the username in MongoDB for reference
    expense_data = ExpenseModel(**expense_data)
    # Save the expense data to MongoDB
    expenses_collection = db.expenses
    expenses_collection.insert_one(expense_data.model_dump())

    return redirect("/display")

# DISPLAY graph
@app.route("/display")
def display():
    expenses_collection = db.expenses
    username = session.get('username')  # Retrieve the username from the session
    # Retrieve expenses for the logged-in user
    expenses = list(expenses_collection.find({'username': username}).sort('date', -1))
    print(expenses)
    return render_template('display.html', expenses=expenses)


# DELETE the data
@app.route('/delete/<ObjectId:id>', methods=['POST'])
def delete(id):
    expenses_collection = db.expenses

    # Delete the specified expense record
    expenses_collection.delete_one({'_id': id})
    
    print('Deleted successfully')
    return redirect("/display")

# UPDATE DATA
@app.route('/edit/<ObjectId:id>', methods=['POST'])
def edit(id):
    expenses_collection = db.expenses

    # Retrieve the expense record to edit
    expense = expenses_collection.find_one({'_id': id})
    return render_template('edit.html', expenses=expense)

@app.route('/update/<ObjectId:id>', methods=['POST'])
def update(id):
    expenses_collection = db.expenses

    # Update the expense record with the edited data
    updated_data = request.form.to_dict()
    expenses_collection.update_one({'_id': id}, {'$set': updated_data})
    
    print('Successfully updated')
    return redirect("/display")

# LIMIT
@app.route("/limit")
def limit():
    return redirect('/limitn')

@app.route("/limitnum", methods=['POST'])
def limitnum():
    number = float(request.form['number'])
    limits_collection = db.limits
    limits_collection.insert_one({'userid': session['username'], 'limitss': number})
    return redirect('/limitn')

@app.route("/limitn")
def limitn():
    limits_collection = db.limits

    # Retrieve the latest spending limit for the logged-in user
    latest_limit = limits_collection.find_one({'userid': session['username']}, sort=[('_id', -1)])
    
    return render_template("limit.html", y=latest_limit.get('limitss', 0))

# REPORT
@app.route("/today")
def today():
    expenses_collection = db.expenses
    username = session.get('username')
    
    # Retrieve expenses for the logged-in user that occurred today
    today_expenses = list(expenses_collection.find({
        'userid': username,
        'date': current_date  # Implement 'current_date' with the appropriate format
    }))

    total = sum(expense['amount'] for expense in today_expenses)
    
    categories = {'food': 0, 'entertainment': 0, 'business': 0, 'rent': 0, 'EMI': 0, 'other': 0}
    for expense in today_expenses:
        category = expense['category']
        categories[category] += expense['amount']

    return render_template("today.html", texpense=today_expenses, total=total, **categories)

# MONTH
@app.route("/month")
def month():
    expenses_collection = db.expenses
    username = session.get('username')
    
    # Retrieve expenses for the logged-in user for the current month
    current_month_expenses = list(expenses_collection.find({
        'userid': username,
        'date': {'$regex': r'\d{4}-\d{2}'}
    }))

    total = sum(expense['amount'] for expense in current_month_expenses)
    
    categories = {'food': 0, 'entertainment': 0, 'business': 0, 'rent': 0, 'EMI': 0, 'other': 0}
    for expense in current_month_expenses:
        category = expense['category']
        categories[category] += expense['amount']

    return render_template("today.html", texpense=current_month_expenses, total=total, **categories)

# YEAR
@app.route("/year")
def year():
    expenses_collection = db.expenses
    username = session.get('username')
    
    # Retrieve expenses for the logged-in user for the current year
    current_year_expenses = list(expenses_collection.find({
        'userid': username,
        'date': {'$regex': r'\d{4}'}
    }))

    total = sum(expense['amount'] for expense in current_year_expenses)
    
    categories = {'food': 0, 'entertainment': 0, 'business': 0, 'rent': 0, 'EMI': 0, 'other': 0}
    for expense in current_year_expenses:
        category = expense['category']
        categories[category] += expense['amount']

    return render_template("today.html", texpense=current_year_expenses, total=total, **categories)

# LOG-OUT
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
