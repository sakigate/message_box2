from flask import Flask, redirect, render_template, request, flash
from werkzeug.security import generate_password_hash
from config import User

app = Flask(__name__)
app.secret_key = "secret"

@app.route('/register',methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # データの検証 未入力の処理
        if not request.form["name"] or not request.form["password"] or not request.form["email"]:
            flash("未入力の項目があります。")
            return redirect(request.url)

        # データの重複
        if User.select().where(User.name == request.form["name"]):
            flash("その名前はすでに使われています。")
            return redirect(request.url)
        if User.select().where(User.email == request.form["email"]):
            flash("そのメールアドレスはすでに使われています。")
            return redirect(request.url)

        # ユーザー登録
        User.create(
            name=request.form["name"],
            email=request.form["email"],
            password=generate_password_hash(request.form["password"])
        )
    return render_template('register.html')


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
