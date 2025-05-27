from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)


@app.route('/')
def index():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('index.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']

        post = Post(title=title, text=text)

        try:
            db.session.add(post)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            print(e)
            return "Возникла ошибка при создании поста"
    else:
        return render_template('create.html')


@app.route('/post/<int:id>')
def post(id):
    post = Post.query.get(id)
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
