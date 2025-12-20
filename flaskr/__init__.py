from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("/index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("/login.html")
    elif request.method == "POST":
        # Get user creadentials 
        # Compare against database
        # Save user login to session 
        return {}
    
@app.route("/registar", methods=["GET", "POST"])
def registar():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":

        #Add try catch block 
        data = request.get_json()
        print(data)
        return {}
    
def save_user(email, password):
    
    return True
