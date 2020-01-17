from common.database import Database
from models.blog import Blog
from models.post import Post
from models.user import User
from flask import Flask, render_template, request, session, make_response, redirect, url_for, flash
from functools import wraps


app = Flask(__name__)
app.secret_key = 'siva123'


@app.route('/')
def home_template():
    return render_template('home.html')


@app.route('/login')
def login_template():
    return render_template('login.html')


@app.route('/register')
def register_template():
    return render_template('register.html')


@app.before_first_request
def initialize_database():
    Database.initialize()


@app.route('/auth/login', methods=['POST', 'GET'])
def login_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.login(email, password):
            return redirect(url_for('Profile_of_User'))
    else:
        return render_template("login.html")


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized User, Please login', 'danger')
            return redirect(url_for('login_user'))
    return wrap   


@app.route('/profile')
@is_logged_in
def Profile_of_User():
    return render_template("profile.html")


@app.route('/logout')
@is_logged_in
def logout_user():
    User.logout()
    return render_template('login.html')


@app.route('/auth/register', methods=['POST', 'GET'])
def register_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if User.register(name, email, username, password):
            session['username'] = username
            return redirect(url_for('Profile_of_User'))

        flash('Either Username or Email is already registered in the system!', 'error')
        # Add a comment saying you are already registered
        session['username'] = None
    return redirect(url_for('register_template'))


# @app.route('/blogs/<string:user_id>')
# @app.route('/blogs')
# def user_blogs(user_id=None):
#     if user_id is not None:
#         user = User.get_by_id(user_id)
#     else:
#         user = User.get_by_email(session['email'])
#
#     blogs = user.get_blogs()
#
#     return render_template("user_blogs.html", blogs=blogs, email=user.email)
#
#
# @app.route('/blogs/new', methods=['POST', 'GET'])
# def create_new_blog():
#     if request.method == 'GET':
#         return render_template('new_blog.html')
#     else:
#         title = request.form['title']
#         description = request.form['description']
#         user = User.get_by_email(session['email'])
#
#         new_blog = Blog(user.email, title, description, user._id)
#         new_blog.save_to_mongo()
#
#         return make_response(user_blogs(user._id))
#
#
# @app.route('/posts/<string:blog_id>')
# def blog_posts(blog_id):
#     blog = Blog.from_mongo(blog_id)
#     posts = blog.get_posts()
#
#     return render_template('posts.html', posts=posts, blog_title=blog.title, blog_id=blog._id)
#
#
# @app.route('/posts/new/<string:blog_id>', methods=['POST', 'GET'])
# def create_new_post(blog_id):
#     if request.method == 'GET':
#         return render_template('new_post.html', blog_id=blog_id)
#     else:
#         title = request.form['title']
#         content = request.form['content']
#         user = User.get_by_email(session['email'])
#
#         new_post = Post(blog_id, title, content, user.email)
#         new_post.save_to_mongo()
#
#         return make_response(blog_posts(blog_id))


if __name__ == '__main__':
    app.run(debug=True)
