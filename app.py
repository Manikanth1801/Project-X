from common.database import Database
from models.blog import Blog
from models.post import Post
#importing multiple classes in user model
from models.user import User 
from models.participant import Participant
from models.organiser import Organizer
from models.events import Event

from flask import Flask, render_template, request, session, make_response, redirect, url_for, flash
from functools import wraps


app = Flask(__name__)
app.secret_key = 'siva123'


@app.route('/')
def home_template():
    event_log= Database.find("event", {})
    '''for events in :
        event_log.append(events)'''
    return render_template('home.html', events=event_log)


@app.route('/login')
def login_template():
    return render_template('login.html')

@app.route('/ch-uname')
def ch_uname_template():
    return render_template('username.html')


@app.route('/register')
def register_template():
    return render_template('register.html')


@app.route('/register/auth/organizer')
def org_register_template():
    return render_template('org_register.html')


@app.route('/register/auth/participant')
def part_register_template():
    return render_template('part_register.html')


@app.route('/create_event')
def create_event_template():
    return render_template('create_event.html')
            


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
        address1 = request.form['address1']
        address2 = request.form['address2']
        state = request.form['stt']
        city = request.form['sttt']
        pin = request.form['pin']
        org_phone = request.form['org_phone']
        if Organizer.orgRegister(org_name, address1, address2, state, city, pin, org_phone):
            return redirect(url_for('Profile_of_User'))
    return redirect(url_for('org_register_template'))


#participant details saving to db
@app.route('/auth/register/participant', methods=['GET', 'POST'])
def partReg():
    if request.method == 'POST':
        preference1 = request.form['preference1']
        preference2 = request.form['preference2']
        preference3 = request.form['preference3']
        state = request.form['stt']
        city = request.form['sttt']
        if Participant.partRegister(preference1, preference2, preference3, state, city):
            return redirect(url_for('Profile_of_User'))
    
    return redirect(url_for('part_register_template'))


'''
It is to design update, delete feature of the user after login. e.g. Updating Password, preferences and all
@app.route('/account', methods=['GET', 'POST', 'PUT', 'DELETE']
def acc_details():
update asap
'''

@app.route('/create_eve', methods = ['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        banner_image = request.form['banner_image']
        address_line1 = request.form['address1']
        address_line2 = request.form['address2']
        city = request.form['sttt']
        state = request.form['stt']
        country = request.form['country']
        terms_and_condition = request.form['terms_and_condition']
        event_category = request.form['event_category']
        event_date = request.form['event_date']
        event_time = request.form['event_time']
        contact_no = request.form['contact_no']
        email = request.form['email']
        ticket_price = request.form['ticket_price']
        if Event.createEvent(title, description, banner_image, address_line1, address_line2, city, state, country, terms_and_condition, event_category, event_date, event_time, contact_no, email, ticket_price):
            return redirect(url_for('Profile_of_User'))
    return redirect(url_for('create_event_template'))
           

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
