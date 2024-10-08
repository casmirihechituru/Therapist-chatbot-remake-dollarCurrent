'''
#This uncommented code was copied from "Rex- NEW AI API CHANGING" Repl
from flask import Flask, render_template, jsonify, request
#import config
#import openai
#import aiapi.
import os
from hugchat import hugchat
from hugchat.login import Login


mybestcontextprompt = os.environ['pidginprompt']
signin = os.environ['signin']
password = os.environ['password']
#my_secret = os.environ['token']
my_secret2 = "You are a pidgin English AI"  #os.environ['systemprompt']
#def page_not_found(e):
#  return render_template('404.ht

#openai.api_key = my_secret

app = Flask(__name__)

sign = Login(signin, password)
cookies = sign.login()
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())




def parla(context, question,creativity):

############################################################################
# Qua puoi eventualmente aggiungere alla domanda un contesto specifico
############################################################################

    
    prompt="Answer the question based on the following context:"+context+"\n\nQuestion: "+question
    return(chatbot.chat(prompt,temperature=float(creativity)))








conversation_history = [{"role": "system", "content": my_secret2}]









def generateChatResponse(prompt):
    messages = conversation_history  # Use the entire conversation history as messages

    # Add the user's new question to messages
    user_message = {"role": "user", "content": prompt}
    messages.append(user_message)

    # Hugging Face Login
    
    response = parla(mybestcontextprompt, prompt,2.0)
    
  #chatbot.chat(prompt)

    try:
        answer = response
    except:
        answer = "Oops! Try again later"

    # Store the bot's response in the conversation history
    bot_message = {"role": "assistant", "content": answer}
    conversation_history.append(bot_message)

    return answer




@app.route('/', methods=['POST', 'GET'])
def index():

    
    return render_template('index.html', **locals())



@app.route('/privacypolicy')
def privacypolicy():
  return render_template('privacypolicy.html')


@app.route('/aboutus')
def aboutus():
  return render_template('aboutus.html')


@app.route('/contactus')
def contactus():
  return render_template('contactus.html')

@app.route('/rex', methods=['POST', 'GET'])
def rex():

    if request.method == 'POST':
        prompt = request.form['prompt']

        res = {}
        res['answer'] = str(generateChatResponse(prompt))
        return jsonify(res), 200

    return render_template('rexhtml.html', **locals())

#---------------------------------




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
'''




#Code for Rex that uses openai API

from flask import Flask, render_template, jsonify, request, make_response, redirect, session, flash, abort, url_for
#import config
import openai
#import aiapi
import os
#New line
from datetime import datetime, timedelta
#Added from another webapp
import pyrebase
import re






my_secret = os.environ['token']
my_secret2 = os.environ['pidginprompt']
#def page_not_found(e):
#  return render_template('404.ht

openai.api_key = my_secret



app = Flask('app')
# Set the secret key for the Flask app. This is used for session security.
app.secret_key = "your_secret_key"

# Configuration for Firebase
config = {
     'apiKey' : os.environ['firebase_api_key'],
      'authDomain' : "funny-eng-chatbot.firebaseapp.com",
      'databaseURL' : "https://funny-eng-chatbot-default-rtdb.firebaseio.com",
      'projectId' : "funny-eng-chatbot",
      'storageBucket' : "funny-eng-chatbot.appspot.com",
      'messagingSenderId' : "649383467646",
      'appId' : "1:649383467646:web:9155941c081d23ec44162f",
      'measurementId' : "G-6WX7ERK5R8"


  #-----------------------
}

# Initialize Firebase
firebase = pyrebase.initialize_app(config)

# Get reference to the auth service and database service
auth = firebase.auth()
db = firebase.database()


#Added from another webapp
# Route for the login page
@app.route("/")
def login():
    return render_template("login.html")

# Route for the signup page
@app.route("/signup")
def signup():
    return render_template("signup.html")

# Route for the welcome page
@app.route("/welcome")
def welcome():
    # Check if user is logged in
    if session.get("is_logged_in", False):
        return render_template("index.html", email=session["email"], name=session["name"])
        #return render_template("welcome.html", email=session["email"], name=session["name"])
    else:
        # If user is not logged in, redirect to login page
        return redirect(url_for('login'))

# Function to check password strength
def check_password_strength(password):
    # At least one lower case letter, one upper case letter, one digit, one special character, and at least 8 characters long
    return re.match(r'^(?=.*\d)(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z]).{8,}$', password) is not None

# Route for login result
@app.route("/result", methods=["POST", "GET"])
def result():
    if request.method == "POST":
        result = request.form
        email = result["email"]
        password = result["pass"]
        try:
            # Authenticate user
            user = auth.sign_in_with_email_and_password(email, password)
            session["is_logged_in"] = True
            session["email"] = user["email"]
            session["uid"] = user["localId"]
            # Fetch user data
            data = db.child("users").get().val()
            # Update session data
            if data and session["uid"] in data:
                session["name"] = data[session["uid"]]["name"]
                # Update last login time
                db.child("users").child(session["uid"]).update({"last_logged_in": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")})
            else:
                session["name"] = "User"
            # Redirect to welcome page
            return redirect(url_for('welcome'))
        except Exception as e:
            print("Error occurred: ", e)
            return redirect(url_for('login'))
    else:
        # If user is logged in, redirect to welcome page
        if session.get("is_logged_in", False):
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('login'))

# Route for user registration
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        result = request.form
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        if not check_password_strength(password):
            print("Password does not meet strength requirements")
            return redirect(url_for('signup'))
        try:
            # Create user account
            auth.create_user_with_email_and_password(email, password)
            # Authenticate user
            user = auth.sign_in_with_email_and_password(email, password)
            session["is_logged_in"] = True
            session["email"] = user["email"]
            session["uid"] = user["localId"]
            session["name"] = name
            # Save user data
            data = {"name": name, "email": email, "last_logged_in": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
            db.child("users").child(session["uid"]).set(data)
            return redirect(url_for('welcome'))
        except Exception as e:
            print("Error occurred during registration: ", e)
            return redirect(url_for('signup'))
    else:
        # If user is logged in, redirect to welcome page
        if session.get("is_logged_in", False):
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('signup'))

# Route for password reset
@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form["email"]
        try:
            # Send password reset email
            auth.send_password_reset_email(email)
            return render_template("reset_password_done.html")  # Show a page telling user to check their email
        except Exception as e:
            print("Error occurred: ", e)
            return render_template("reset_password.html", error="An error occurred. Please try again.")  # Show error on reset password page
    else:
        return render_template("reset_password.html")  # Show the password reset page

# Route for logout
@app.route("/logout")
def logout():
    # Update last logout time
    db.child("users").child(session["uid"]).update({"last_logged_out": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")})
    session["is_logged_in"] = False
    return redirect(url_for('login'))

#end of "added..."





@app.route('/landing')
def hello_world():
  return render_template('index.html')


@app.route('/privacypolicy')
def privacypolicy():
  return render_template('privacypolicy.html')


@app.route('/aboutus')
def aboutus():
  return render_template('aboutus.html')


@app.route('/contactus')
def contactus():
  return render_template('contactus.html')

#---------------------------------



conversation_history = [{"role": "system", "content": my_secret2}]

def generateChatResponse(prompt):
    messages = conversation_history  # Use the entire conversation history as messages


     #Intro data
#    que = {"role": "user", "content": "Wetin be your name"}
#    ans = {"role": "assistant", "content": "My name na Rex"}
#    messages.append(que)
#    messages.append(ans)



    # Add the user's new question to messages
    user_message = {"role": "user", "content": prompt}
    messages.append(user_message)

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)



    try:
        answer = response['choices'][0]['message']['content'].replace('\n', '<br>')
    except:
        answer = "Oops! Try again later"

    # Store the bot's response in the conversation history
    bot_message = {"role": "assistant", "content": answer}
    conversation_history.append(bot_message)

    return answer


#Rex response and count which uses cookie instead of session.
user_prompt_count = {}

@app.route('/chatbot', methods=['POST', 'GET'])
def rex():
    # Check if the user is logged in
    if not session.get("is_logged_in", False):
        # Redirect to login page if not logged in
        return redirect(url_for('login'))

    if request.method == 'POST':
        prompt = request.form['prompt']

        # Check if the user has a session
        if 'session_id' not in session:
            # If not, create a new session ID and set the prompt count to 1
            session_id = os.urandom(16).hex()
            session['session_id'] = session_id
            user_prompt_count[session_id] = 1
        else:
            # If yes, get the session ID
            session_id = session['session_id']

        # Get the prompt count for the user
        prompt_count = user_prompt_count.get(session_id, 0)

        # Check if the user has exceeded the daily limit
        if prompt_count >= 5:
            return jsonify({'answer': "NOTIFICATION!!!: Sorry, you've completed your 10 prompts for today."}), 200

        # Generate the chat response
        res = {}
        res['answer'] = generateChatResponse(prompt)

        # Update the user's prompt count
        user_prompt_count[session_id] = prompt_count + 1

        # Create a response object
        response = make_response(jsonify(res), 200)
        return response

    return render_template('rexhtml.html')





        



app.run(debug= True, host='0.0.0.0', port=8000)
