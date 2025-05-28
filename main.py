from flask import Flask, render_template, request, redirect, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timezone
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
app.config['SECRET_KEY'] = 'very_secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

users = {
    'evgeniy': 'mypassword123'
}


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[
        DataRequired(), Length(min=2, max=30)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[
                        DataRequired(), Length(min=3, max=100)])
    content = TextAreaField('Контент', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


@app.route('/')
def index():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('index.html', posts=posts)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if username in users and password == users[username]:
            session['user'] = username
            flash('Добро пожаловать, {}!'.format(username), 'success')
            return redirect(url_for('protected'))
        else:
            return flash('Неверный логин или пароль', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/protected')
def protected():
    if 'user' not in session:
        flash('Войдите в систему, чтобы увидеть эту страницу', 'warning')
        return redirect(url_for('login'))
    return f'Привет, {session["user"]}! Это секретная страница.'


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/create', methods=['POST', 'GET'])
def create():
    if 'user' not in session:
        return "Вам нужно войти"
    form = PostForm()
    if form.validate_on_submit():
        title = request.form['title']
        text = request.form['content']

        post = Post(title=title, text=text)

        try:
            db.session.add(post)
            db.session.commit()
            flash('Пост успешно добавлен!', 'success')
            return redirect('/')
        except Exception as e:
            print(e)
            return "Возникла ошибка при создании поста"
    else:
        return render_template('create.html', form=form)


@app.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)


@app.route('/post/<int:id>/del')
def delete(id):
    post = Post.query.get(id)

    try:
        db.session.delete(post)
        db.session.commit()
        return redirect('/')
    except:
        return "Возникла ошибка при удалении"


@app.route('/post/<int:id>/update', methods=['POST', 'GET'])
def update(id):
    post = Post.query.get(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return "Возникла ошибка при редактировании поста"
    else:
        return render_template('post_update.html', post=post)


if __name__ == '__main__':
    app.run(debug=True)
