import datetime, os
from flask import Flask, render_template, request, url_for
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_admin.contrib.sqla import ModelView
from flask_ckeditor import CKEditor
from flask_ckeditor import CKEditor, CKEditorField, upload_fail, upload_success

app = Flask(__name__)
basedir = os.path.abspath(os.getcwd())
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['SECRET_KEY'] = 'my secret'
#
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://tblwfvkvcjmsej:bccf23d469fd61cc6aac95067a9357386cc8c12978eace5332ed82f8cbf7fbac@ec2-54-246-100-246.eu-west-1.compute.amazonaws.com:5432/dfq7fh6tl6o2o5'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# app.config['SQLALCHEMY_DATABASE_URI'] =  'mysql://root:@localhost/personal'
app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'
app.config['CKEDITOR_SERVE_LOCAL'] = True

app.config['CKEDITOR_HEIGHT'] = 400
app.config['UPLOADED_PATH'] = os.path.join(basedir, 'uploads')

admin = Admin(app, name='microblog', template_mode='bootstrap3')
db = SQLAlchemy(app)
ckeditor = CKEditor(app)
ckeditor = app.config['extraPlugins'] = True



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return  self.username

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    subtitle = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text(), nullable=False)
    created_date = db.Column(db.DateTime, default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False)
    user = db.relationship('User',
                               backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return self.title


class PostAdmin(ModelView):
    form_overrides = dict(body=CKEditorField)
    edit_template = 'admin/post/edit.html'


admin.add_view(ModelView(User, db.session))
admin.add_view(PostAdmin(Post, db.session))


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/files/<filename>')
def uploaded_files(filename):
    path = app.config['UPLOADED_PATH']
    return send_from_directory(path, filename)


@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')
    extension = f.filename.split('.')[1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='Image only!')
    f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    url = url_for('uploaded_files', filename=f.filename)
    return upload_success(url=url)

db.create_all()
