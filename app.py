from common.database import Database
from models.blog import Blog
from models.post import Post
# importing multiple classes in user model
from models.user import User
from models.participant import Participant
from models.organiser import Organizer
from models.events import Event
from random import randint

from flask import Flask, render_template, request, session, make_response, redirect, url_for, flash
from functools import wraps
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

#----------------------------------------------------------------------------------------------------------------------

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
app.secret_key = 'siva123'


mail = Mail(app)

#----------------------------------------------------------------------------------------------------------------------

@app.route('/')
def home_template():
    event_log = Database.find("event", {})
    return render_template('home.html', events=event_log)


@app.route('/login')
def login_template():
    return render_template('login.html')


@app.route('/ch-uname')
def ch_uname_template():
    return render_template('username.html')


@app.route('/ch-passwd')
def ch_passwd_template():
    return render_template('password.html')


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

#------------------------------------------------------------------------------------------------------------------------

@app.before_first_request
def initialize_database():
    Database.initialize()
    
#-------------------------------------------------------------------------------------------------------------------------
@app.route('/send/<email>')
def send_confirmation(email):
    token = generate_confirmation_token(email)
    confirm_url = url_for('confirm_email', token=token, email=email, _external=True)
    html = render_template('activate.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(email, subject, html)
    flash('A confirmation email has been sent.', 'success')
    return redirect(url_for('unconfirmed', email=email))

@app.route('/cnf_url_fp/<token>/<email>')
def cnf_url_fp(token, email):
    email = confirm_token(token)
    user = Database.find_one("test", {"email": email})
    if user['email'] == email:
        render_template('up_pass.html', email=email)
    else:
        flash('The confirmation link is invalid or has expired.', 'danger')

def send_confirmation_fp(email):
    token = generate_confirmation_token(email)
    cnf_url_fp = url_for('cnf_url_fp', token=token, email=email, _external=True)
    subject = "To change your password, Please click on the link below. "
    html = render_template('fp_activate_msg.html', cnf_url_fp=cnf_url_fp)
    send_email(email,subject,html)
     
   
    
#-------------------------------------------------------------------------------------------------------------------------
#Login Functions

@app.route('/auth/register', methods=['POST', 'GET'])
def register_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        #added new field usertype for registering
        if User.register(name, email, username, password):
            send_confirmation(email)
    else:
        flash('Either Username or Email is already registered in the system!', 'danger')
        # Add a comment saying you are already registered
        session['username'] = None
    return redirect(url_for('register_template'))

@app.route('/auth/login', methods=['POST', 'GET'])
def login_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.login(email, password):
            return redirect(url_for('Profile_of_User'))
        else:
            flash("Username/Email not found or Incorrect password provided!", 'warning')
        return render_template("login.html")


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        # No Need of the else part. Redirect the whole thing form Login Function.
        else:
            flash('Unauthorized User, Please login', 'danger')
            return redirect(url_for('login_user'))

    return wrap

@app.route('/logout')
@is_logged_in
def logout_user():
    User.logout()
    return render_template('login.html')

@app.route('/profile')
@is_logged_in
def Profile_of_User():
    return render_template("profile.html")

#------------------------------------------------------------------------------------------------------------------------
#Updation Things

@app.route('/auth/ch-uname', methods=['POST', 'GET'])
def ch_uname():
    if request.method == 'POST':
        puname = request.form['puname']
        password = request.form['password']
        nuname = request.form['nuname']
        #if User.login(puname, password):  # for checking correct details
            # return redirect(url_for('Profile_of_User'))

        if User.up_uname(nuname, puname, password):
            #flash('Username is changed')

            return render_template("profile.html")
    else:
        return render_template("username.html")

#password change function
@app.route('/auth/ch-passwd', methods=['POST', 'GET'])
def ch_passwd():
    if request.method == 'POST':
        oldpassword = request.form['oldpassword']
        newpassword = request.form['newpassword']
        renewpassword = request.form['renewpassword']
        if newpassword == renewpassword:
            if User.up_passwd(oldpassword, renewpassword):
                flash('successfully password changed','success')
                return redirect(url_for('Profile_of_User'))
            else:
                return redirect(url_for('ch_passwd_template'))
        else:
            flash('Newpassword and retyped newpassword are different','danger')
            return redirect(url_for('ch_passwd_template'))
    else:
        return redirect(url_for('ch_passwd_template'))

@app.route('/forgot_password')
def fp():
    return render_template('forgot_password.html')

@app.route('/auth/forgot_password', methods=['GET', 'POST'])
def afp():
    if request.method == 'POST':
        email = request.form['email']
        send_confirmation_fp(email)
        flash('A confirmation message has been sent to your registered email. Please click on the link to reset your password', 'success')
    return True
        
@app.route('/set-password/<email>', methods=['POST', 'GET'])
def set_password(email):
    if request.method == 'POST':
        password = request.form['newpassword']
        re_password = request.form['renewpassword']
        if newpassword == renewpassword:
            if User.up_passwd_1(email, renewpassword):
                flash('successfully password changed','success')
                return render_template('login.html')
        
    

#----------------------------------------------------------------------------------------------------------------
#Sending Confirmation Email

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
    except:
        return False
    return email


@app.route('/confirm_email/<token>/<email>')
def confirm_email(token, email):
    user = Database.find_one("test", {"email": email})
    if user['confirmed'] == 'True':
        flash('Account already confirmed. Please login.', 'success')
        return redirect(url_for('home_template'))
    email = confirm_token(token)
    if user['email'] == email:
        Database.update_confirm("test", email)
        flash('You have confirmed your account. Thanks!', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'danger')
    return redirect(url_for('home_template'))


def send_email(to, subject, template):
    message = Mail(from_email=app.config['MAIL_DEFAULT_SENDER'], to_emails=[to], subject=subject, html_content=template)
    sg = SendGridAPIClient(app.config['SENDGRID_API_KEY'])
    sg.send(message)
    
@app.route('/unconfirmed/<email>')
def unconfirmed(email):
    user = Database.find_one("test", {'email': email})
    if user['confirmed'] == 'True':
        return redirect(url_for('Profile_of_User'))
    flash('Please confirm your Email ID!', 'warning')
    return render_template('unconfirmed.html', email=email)

#-----------------------------------------------------------------------------------------------------------------------------

'''
It is to design update, delete feature of the user after login. e.g. Updating Password, preferences and all
@app.route('/account', methods=['GET', 'POST', 'PUT', 'DELETE']
def acc_details():
update asap
'''


@app.route('/create_eve', methods=['GET', 'POST'])
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
        if Event.createEvent(title, description, banner_image, address_line1, address_line2, city, state, country,
                             terms_and_condition, event_category, event_date, event_time, contact_no, email,
                             ticket_price):
            return redirect(url_for('Profile_of_User'))
    return redirect(url_for('create_event_template'))




@app.route('/book_event/<_id>')
def book_event(_id):
    return render_template('booked.html', id=_id)

@app.route('/event_page/<_id>')
def event_page(_id):
    event = Database.find_one('event', {'_id':_id})
    return render_template('Event_Page.html', event = event)

    
    
'''
# organizer details saving to db
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





# participant details saving to db
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


if __name__ == "__main__":
    app.run(debug=True)
