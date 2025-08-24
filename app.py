from flask import Flask, redirect, render_template, request, flash, url_for
from flask_login import LoginManager, current_user, login_manager,login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from config import User, Message

app = Flask(__name__)
app.secret_key = "secret"
login_manager = LoginManager()
login_manager.init_app(app)

# Flask-Loginがユーザー情報を取得するためのメソッド
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# ログインしていないとアクセスできないページにアクセスがあった場合の処理
@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect("/login")

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

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # 未入力の時
        if not request.form["password"] or not request.form["email"]:
            flash("未入力の項目があります。")
            return redirect(request.url)

        # ログイン処理ここに書く
        user = User.select().where(User.email == request.form["email"]).first()
        if user is not None and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            flash(f"ようこそ！ {user.name} さん")
            return redirect(url_for("index"))

        # ログインできなかった時
        flash("ログインできませんでした")

    return render_template('login.html')

# ログアウト処理
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("ログアウトしました")
    return redirect(url_for("index"))

# ユーザー削除
@app.route('/unregister')
@login_required
def unregister():
    current_user.delete_instance()
    logout_user()
    return redirect(url_for("index"))


@app.route('/', methods=["GET","POST"])
def index():
    if request.method == "POST":
        # メッセージテーブルにクリエイト(追加)
        Message.create(user=current_user, content=request.form["content"])
    messages =(
        Message.select()
        .where(Message.reply_to.is_null(True))
        #descは降順の意味
        .order_by(Message.pub_date.desc(), Message.id.desc())
    )
    return render_template("index.html", messages=messages)


# メッセージ削除
@app.route("/messages/<message_id>/delete/", methods=["POST"])
@login_required
def delete(message_id):
    if Message.select().where((Message.id == message_id) & (Message.user == current_user)).first():
        Message.delete_by_id(message_id)
    else:
        flash("無効な操作です")
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
