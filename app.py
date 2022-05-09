import json

import sqlalchemy
from flask import Flask, request
from flask_login import login_user, logout_user, login_required, LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column, String, Integer

from user import User

app = Flask(__name__)
app.secret_key = 'asdasdasdasd'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo-collection.db'
lm = LoginManager()
lm.init_app(app)

db = SQLAlchemy(app)


class Todo(db.Model):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True)
    text = Column(String(250), nullable=False)
    author = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    modified = Column(Boolean, default=False)
    end = Column(Boolean, default=False)


db.create_all()


@app.route('/create', methods=['POST'])
def create_task():
    body = json.loads(request.data)
    new_todo = Todo(text=body['text'], author=body['author'],
                    email=body['email'])
    db.session.add(new_todo)
    db.session.commit()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/change-text', methods=['POST'])
@login_required
def change_text():
    body = json.loads(request.data)
    editedTodo = db.session.query(Todo).filter_by(id=body['id']).one()
    editedTodo.text = body['text']
    editedTodo.modified = True
    db.session.add(editedTodo)
    db.session.commit()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/end', methods=['POST'])
@login_required
def end():
    body = json.loads(request.data)
    editedTodo = db.session.query(Todo).filter_by(id=body['id']).one()
    editedTodo.end = not editedTodo.end
    db.session.add(editedTodo)
    db.session.commit()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/get', methods=['GET'])
def get_tasks():
    order_dict = {
        'email': Todo.email,
        'author': Todo.author,
        'end': Todo.end
    }
    page_size = 3
    page_num = request.args.get('page', 1, type=int) - 1
    order_by = request.args.get('order', None, type=str)
    desk = request.args.get('desk', False, type=bool)
    q = db.session.query(Todo)
    if order_by in order_dict:
        order_by = order_dict[order_by]
        if desk:
            order_by = sqlalchemy.desc(order_by)
        q = q.order_by(order_by)
    page = q.offset(page_size * page_num).limit(page_size).all()
    pages_amount = db.session.query(Todo).count() // page_size + 1
    return {'todo': [{c.name: getattr(x, c.name) for c in x.__table__.columns} for x in page],
            'pages': pages_amount}


@app.route('/login', methods=['POST'])
def login():
    if request.form['login'] == 'admin' and request.form['password'] == '123':
        login_user(User())
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    return 0


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@lm.user_loader
def load_user(user_id):
    return User()


if __name__ == '__main__':
    app.run()
