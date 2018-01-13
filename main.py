

from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hashutils import make_pw_hash, check_pw_hash


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz3187@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'F^zEPCZ8ufN8tN?!'
db = SQLAlchemy(app)


#Blog class
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey ('user.id'))
    created = db.Column(db.DateTime)

    def __init__(self, title, body, owner, created=None):
        self.title = title
        self.body = body
        self.owner = owner
        if created is None:
            created = datetime.utcnow()
        self.created = created;

#User class
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(135), unique = True)
    pw_hash = db.Column(db.String(135))
    blogs = db.relationship('Blog', backref='owner')

    def __init__ (self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)


#not a request handler, will run for every request
#run this function before you call the request
# requires user login to access /newpost
@app.before_request
def require_login():
    #list of routes that users don't have to login to see
    allowed_routes = ['index', 'login', 'signup', 'blog', 'post', 'singleUser']
    # endpoint is the name of the view function, not the url path
        #we put 'login' in the allowed_routes list, rather than '/login'
    if request.endpoint not in allowed_routes and 'username' not in session:
        #If user is trying to go to any route besides the allowed routes and is not logged in (their username is not stored in a session), redirect them to the /login page
        return redirect ('/login')


#Index route
@app.route ('/')
def index ():
    users = User.query.all()
    return render_template( 'index.html', users=users)


# signup route handler function: new user account and redirect when already signed in
@app.route ('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        if (username == '' or (len(username) < 3 or len(username) >35) or (" " in username)):
            flash ('invalid username', 'error')
            return redirect('signup')
        if (password == '' or (len(password) < 3 or len(password) >20) or (" " in password)):
            flash('Invalid password', 'error')
            return redirect('signup')
        #User enters different strings into the password and verify fields and gets an error message that the passwords do not match.
        if verify != password:
            flash('Passwords do not match.', 'error')
            return redirect('signup')
        #User enters a username that already exists and gets an error message that username already exists.
        if existing_user:
            flash('Username already in use.', 'error')
            return redirect('signup')
        #User enters new, valid username, a valid password, and verifies password correctly and is redirected to the '/newpost' page with their username being stored in a session.
        if not existing_user:
        # and not username_error and not password_error and not verify_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect ('/newpost')

    return render_template('signup.html')


#login route handler function
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()

        #User enters a username that is stored in the database with the correct password and is redirected to the /newpost page with their username being stored in a session.
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            return redirect('/newpost')
        #User enters a username that is stored in the database with an incorrect password and is redirected to the /login page with a message that their password is incorrect.
        if not user:
            flash('Incorrect username', 'error')
        #User tries to login with a username that is not stored in the database and is redirected to the /login page with a message that this username does not exist.
        else:
            flash('Incorrect Password', 'error')

    return render_template ('login.html')


@app.route("/blog", methods=['POST', 'GET'])
def blog():
    # single user: /blog?user=bobo2
    if 'user' in request.args:
        userId = request.args.get('user')
        user = User.query.filter_by(id=userId).first()
        blogs = user.blogs
        return render_template('singleUser.html', user=user, blogs=blogs)
    # single post: /blog?id=5701867585667072
    elif 'id' in request.args:
        blogId = request.args.get('id')
        blogs = Blog.query.filter_by(id=blogId).all()
        return render_template('singleUser.html', blogs=blogs)

    else:
        #all posts: /blog
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)


@app.route("/newpost", methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        post = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        if title == '':
            flash('You need to include a title.', 'error')
        if post =='':
            flash('You need to include content in the body', 'error')
        if title != "" and post != "":
            new_post = Blog(title, post, owner)
            db.session.add(new_post)
            db.session.commit()
            #User is logged in and adds a new blog post, then is redirected to a page featuring the individual blog entry they just created
            return redirect ("/blog?id={0}".format(new_post.id))

    return render_template('newpost.html')


# Logout function that handles a POST request to /logout and redirects the user to /blog after deleting the username from the session
#User clicks "Logout" and is redirected to the /blog page and is unable to access the /newpost page (is redirected to /login page instead).
@app.route ('/logout')
def logout():
    del session['username']
    return redirect ('/blog')


if __name__ == '__main__':
    app.run()
