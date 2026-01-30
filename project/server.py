from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    user = request.form.get("user")
    pwd = request.form.get("pwd")
    if user == "admin" and pwd == "123456":
        return render_template("show.html")
    return "登录失败"

if __name__ == "__main__":
    app.run(debug=True)
