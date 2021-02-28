
from flask import Flask, render_template, url_for, jsonify, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
client = app.test_client()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime(300), default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id


@app.route('/api', methods=['GET'])
def get_list():
    article = Article.query.all()
    serialised = []
    for art in article:
        serialised.append({
            'title': art.title,
            'intro': art.intro,
            'text': art.text,
        })
    return jsonify(serialised)


@app.route('/api', methods=['POST'])
def update_list():
    new_one = Article(**request.json)
    db.session.add(new_one)
    db.session.commit()
    serialized = {
        'title': new_one.title,
        'intro': new_one.intro,
        'text': new_one.text,
    }
    return jsonify(serialized)


@app.route('/api/<int:tutorial_id>', methods=['PUT'])
def update_tutorial(tutorial_id):
    item = Article.query.filter(Article.id == tutorial_id).first()
    params = request.json
    if not item:
        return {'message': 'No tutorials with this id'}, 400
    for key, value in params.items():
        setattr(item, key, value)
    db.session.commit()
    serialized = {
        'title': item.title,
        'intro': item.intro,
        'text': item.text,
    }
    return serialized


@app.route('/api/<int:tutorial_id>', methods=['DELETE'])
def delete_tutorial(tutorial_id):
    item = Article.query.filter(Article.id == tutorial_id).first()
    if not item:
        return {'message': 'No tutorials with this id'}, 400
    db.session.delete(item)
    db.session.commit()
    return '', 204


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/posts')
@app.route('/')
@app.route('/home')
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template('posts.html', articles=articles)


@app.route('/posts/<int:id>')
def post_detail(id):
    article = Article.query.get(id)
    return render_template('post_detail.html', article=article)


@app.route('/posts/<int:id>/del')
def posts_delete(id):
    article = Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return 'При удалении статьи произошла ошибка'


@app.route('/create-article', methods=['POST', 'GET'])
def create_article():
    if request.method == 'POST':
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']
        article = Article(title=title, intro=intro, text=text)
        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/posts')
        except:
            return 'При редактировании статьи произошла ошибка'

    else:
        return render_template('create-article.html')


@app.route('/posts/<int:id>/update', methods=['POST', 'GET'])
def post_update(id):
    article = Article.query.get(id)
    if request.method == 'POST':
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/posts')
        except:
            return 'При добавлении статьи возникала ошибка'
    else:
        return render_template('post_update.html', article=article)


if __name__ == '__main__':
    app.run(debug=True)
