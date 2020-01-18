from common.database import Database
from models.blog import Blog
from models.post import Post
#importing multiple classes in user model
from models.user import User, Organizer, Participant

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


@app.route('/register/auth/organizer')
def org_register_template():
    return render_template('org_register.html')


@app.route('/register/auth/participant')
def part_register_template():
    return render_template('part_register.html')


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
    #extract usertype(participant/organizer) from database
    data = Database.find_one("test", {"username": session['username']})
    type = data['type']
    return render_template("profile.html", type = type)


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
        usertype = request.form['type']
        #added new field usertype for registering
        if User.register(name, email, username, password, usertype):
            session['username'] = username
            data = Database.find_one("test", {"username": session['username']})
            usrType = data['type']
            #extract usertype and redirect to corresponding pages
            if usrType == 'Organizer':
                return redirect(url_for('orgReg'))
            elif usrType == 'Participant':
                return redirect(url_for('partReg'))

        flash('Either Username or Email is already registered in the system!', 'error')
        # Add a comment saying you are already registered
        session['username'] = None
    return redirect(url_for('register_template'))


#organizer details saving to db
@app.route('/auth/register/organizer', methods=['GET', 'POST'])
def orgReg():
    if request.method == 'POST':
        org_name = request.form['org_name']
        org_email = request.form['org_email']
        address = request.form['address']
        if Organizer.orgRegister(org_name, org_email, address):
            return redirect(url_for('Profile_of_User'))
    return redirect(url_for('org_register_template'))


#participant details saving to db
@app.route('/auth/register/participant', methods=['GET', 'POST'])
def partReg():
    if request.method == 'POST':
        preference1 = request.form['preference1']
        preference2 = request.form['preference2']
        preference3 = request.form['preference3']
        address = request.form['address']
        if Participant.partRegister(preference1, preference2, preference3, address):
            return redirect(url_for('Profile_of_User'))
    return redirect(url_for('part_register_template'))


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
