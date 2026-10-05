import random
from flask import Flask, render_template_string, request, redirect, url_for, session
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

app = Flask(__name__)

# Secret key for login session
app.secret_key = "change-this-secret-key"


# ==========================================================
# 1. CREATE SAMPLE PATIENT DATA
# ==========================================================

X = []
y = []

for i in range(300):

    age = random.randint(20, 90)
    heart_rate = random.randint(50, 140)
    oxygen = random.randint(85, 100)
    temperature = round(random.uniform(35.5, 40.0), 1)

    points = 0

    if age > 65:
        points += 1

    if heart_rate > 100:
        points += 1

    if oxygen < 92:
        points += 2

    if temperature > 38:
        points += 1

    X.append([age, heart_rate, oxygen, temperature])

    if points >= 3:
        y.append(1)
    else:
        y.append(0)


# ==========================================================
# 2. SPLIT DATA
# ==========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# ==========================================================
# 3. TRAIN MACHINE LEARNING MODEL
# ==========================================================

model = LogisticRegression(max_iter=1000)

model.fit(X_train, y_train)


# ==========================================================
# 4. CALCULATE MODEL PERFORMANCE
# ==========================================================

predictions = model.predict(X_test)

probabilities = model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, predictions)

precision = precision_score(
    y_test,
    predictions,
    zero_division=0
)

recall = recall_score(
    y_test,
    predictions,
    zero_division=0
)

f1 = f1_score(
    y_test,
    predictions,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    probabilities
)


# Convert to percentage

accuracy = round(accuracy * 100, 1)
precision = round(precision * 100, 1)
recall = round(recall * 100, 1)
f1 = round(f1 * 100, 1)
roc_auc = round(roc_auc * 100, 1)


print("--------------------------------")
print("MODEL PERFORMANCE")
print("--------------------------------")
print("Accuracy     :", accuracy, "%")
print("Precision    :", precision, "%")
print("Recall       :", recall, "%")
print("F1 Score     :", f1, "%")
print("ROC-AUC Score:", roc_auc, "%")
print("--------------------------------")


# ==========================================================
# 5. LOGIN PAGE
# ==========================================================

login_page = """
<!DOCTYPE html>

<html>

<head>

<title>Login</title>

<style>

body {
    font-family: Arial;
    background-color: #f2f2f2;
    margin: 30px;
}

.login-box {
    width: 350px;
    margin: 100px auto;
    padding: 25px;
    border: 2px solid black;
    background-color: white;
}

h1 {
    color: darkblue;
}

input {
    padding: 8px;
    width: 95%;
}

button {
    padding: 10px 20px;
    background-color: darkblue;
    color: white;
    border: none;
    cursor: pointer;
}

.error {
    color: red;
}

</style>

</head>

<body>

<div class="login-box">

<h1>Patient Risk Checker</h1>

<h3>Login</h3>

{% if error %}
<p class="error">{{ error }}</p>
{% endif %}

<form method="POST">

<label>Username:</label>

<br>

<input type="text"
       name="username"
       required>

<br><br>

<label>Password:</label>

<br>

<input type="password"
       name="password"
       required>

<br><br>

<button type="submit">
Login
</button>

</form>

</div>

</body>

</html>
"""


# ==========================================================
# 6. MAIN PAGE
# ==========================================================

page = """

<!DOCTYPE html>

<html>

<head>

<title>Patient Risk Checker</title>

<style>

body {
    font-family: Arial;
    background-color: #f2f2f2;
    margin: 30px;
}

h1 {
    color: darkblue;
}

input {
    padding: 5px;
    width: 200px;
}

button {
    padding: 8px 15px;
    background-color: darkblue;
    color: white;
    border: none;
    cursor: pointer;
}

button:hover {
    background-color: navy;
}

.logout {
    float: right;
    background-color: darkred;
}

.result {
    margin-top: 20px;
    padding: 10px;
    width: 300px;
    border: 2px solid black;
}

.low {
    background-color: lightgreen;
}

.medium {
    background-color: yellow;
}

.high {
    background-color: lightcoral;
}

.metrics {
    margin-top: 20px;
    padding: 15px;
    width: 350px;
    border: 2px solid black;
    background-color: white;
}

.security {
    margin-top: 20px;
    padding: 15px;
    width: 350px;
    border: 2px solid black;
    background-color: #e8f4ff;
}

</style>

</head>

<body>


<a href="/logout">

<button class="logout">
Logout
</button>

</a>


<h1>
Patient Deterioration Risk Checker
</h1>


<p>
Welcome, {{ username }}.
</p>


<p>
Enter the patient details to check the risk.
</p>


<form method="POST">


<label>
Age:
</label>

<br>

<input
type="number"
name="age"
min="0"
max="120"
required>

<br><br>


<label>
Heart Rate (beats per minute):
</label>

<br>

<input
type="number"
name="heart_rate"
min="30"
max="220"
required>

<br><br>


<label>
Oxygen Level (%):
</label>

<br>

<input
type="number"
name="oxygen"
min="50"
max="100"
required>

<br><br>


<label>
Temperature (°C):
</label>

<br>

<input
type="number"
step="0.1"
name="temperature"
min="30"
max="45"
required>

<br><br>


<button type="submit">
Check Risk
</button>


</form>


{% if risk != None %}

<div class="result {{ level }}">

<h2>
Risk: {{ risk }}%
</h2>

<p>
Risk Level: {{ level }}
</p>


{% if level == "high" %}

<p>
Please inform the doctor immediately.
</p>

{% elif level == "medium" %}

<p>
Check the patient more often.
</p>

{% else %}

<p>
Patient looks stable.
</p>

{% endif %}

</div>

{% endif %}


<div class="metrics">

<h2>
Model Performance
</h2>

<p>
<b>Accuracy:</b>
{{ accuracy }}%
</p>

<p>
<b>Precision:</b>
{{ precision }}%
</p>

<p>
<b>Recall:</b>
{{ recall }}%
</p>

<p>
<b>F1 Score:</b>
{{ f1 }}%
</p>

<p>
<b>ROC-AUC Score:</b>
{{ roc_auc }}%
</p>

</div>


<div class="security">

<h3>
Security Features
</h3>

<p>✔ User authentication enabled</p>

<p>✔ Server-side input validation enabled</p>

<p>✔ Debug mode disabled</p>

</div>


<p>

<small>

This is only a student prototype using fake data.
Not for real medical use.

</small>

</p>


</body>

</html>

"""


# ==========================================================
# 7. LOGIN ROUTE
# ==========================================================

@app.route("/login", methods=["GET", "POST"])

def login():

    error = None

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        # Demo username and password

        if username == "admin" and password == "admin123":

            session["logged_in"] = True

            session["username"] = username

            return redirect(
                url_for("home")
            )


        error = "Invalid username or password."


    return render_template_string(
        login_page,
        error=error
    )


# ==========================================================
# 8. LOGOUT
# ==========================================================

@app.route("/logout")

def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ==========================================================
# 9. HOME PAGE AND RISK PREDICTION
# ==========================================================

@app.route("/", methods=["GET", "POST"])

def home():

    # Check login

    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )


    risk = None

    level = None


    if request.method == "POST":

        try:

            # Get patient information

            age = float(
                request.form.get("age", "")
            )

            heart_rate = float(
                request.form.get("heart_rate", "")
            )

            oxygen = float(
                request.form.get("oxygen", "")
            )

            temperature = float(
                request.form.get("temperature", "")
            )


            # ==================================================
            # SERVER-SIDE VALIDATION
            # ==================================================

            if not (0 <= age <= 120):

                return "Invalid age."


            if not (30 <= heart_rate <= 220):

                return "Invalid heart rate."


            if not (50 <= oxygen <= 100):

                return "Invalid oxygen level."


            if not (30 <= temperature <= 45):

                return "Invalid temperature."


            # ==================================================
            # PREDICT RISK
            # ==================================================

            chance = model.predict_proba(
                [[
                    age,
                    heart_rate,
                    oxygen,
                    temperature
                ]]
            )[0][1]


            risk = round(
                chance * 100,
                1
            )


            # ==================================================
            # DETERMINE RISK LEVEL
            # ==================================================

            if risk < 30:

                level = "low"

            elif risk < 60:

                level = "medium"

            else:

                level = "high"


        except (ValueError, TypeError):

            return "Invalid input. Enter numbers only."


    return render_template_string(

        page,

        risk=risk,

        level=level,

        username=session.get("username"),

        accuracy=accuracy,

        precision=precision,

        recall=recall,

        f1=f1,

        roc_auc=roc_auc

    )


# ==========================================================
# 10. START PROGRAM
# ==========================================================

if __name__ == "__main__":

    app.run(debug=False)