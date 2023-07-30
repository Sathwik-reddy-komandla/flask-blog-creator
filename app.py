from flask import Flask,render_template,flash,request,redirect,url_for

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin,LoginManager,login_user,logout_user,current_user,login_required
# import Form
from forms import UserForm,PostForm,LoginForm







# create a flask application
app=Flask(__name__)

'''
Adding a default dtabase i.e. SQLite database to Flask Appplication'''
# Add database
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///users.db'

# Secret key
app.config['SECRET_KEY']="my super secret key"


# Initializing database
db=SQLAlchemy(app)
migrate=Migrate(app,db)

# Flask_login Stuff
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

'''
login and logout views for authentication 
'''

@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user:
            # check password
            if check_password_hash(user.password_hash,form.password.data):
                flash('Logged in Successfully')
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect Password')
                return render_template('login.html',form=form)

        else:
            flash('User not Found, Enter Valid Username')
            return redirect(url_for('login'))
    return render_template('login.html',form=form)

@app.route('/logout',methods=['Get','POST'])
@login_required
def logout():
    logout_user()
    flash("You have been Logged Out!")
    return redirect(url_for('login'))

@app.route('/')
def home():
    print("in home***********")
    posts=Posts.query.order_by(Posts.date_posted).all()
    print(posts)
    return render_template('home.html',posts=posts)


'''
Dasboard of the user presents all the posts and allows the user to edit,delete,create posts adn can also view all the posts ever created 
'''
# Dashboard Page
@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    form=UserForm()
    id=current_user.id
    user=User.query.get_or_404(id)
    my_posts=Posts.query.filter_by(poster_id=id).all()
    return render_template('dashboard.html',form=form,my_posts=my_posts)










'''
Creating,Updating,Delete Users
'''

# 1 Create User
@app.route("/user/add",methods=['GET','POST'])
def create_user():
    name=None
    form=UserForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_password=generate_password_hash(form.password_hash.data,'sha256')
            user=User(name=form.name.data,email=form.email.data,password_hash=hashed_password,username=form.username.data)
            db.session.add(user)
            db.session.commit()
            flash('User Added Successfully...')
            return redirect(url_for('home'))
        else:
            name=form.name.data
            form.name.data=''
            form.username.data=''
            form.email.data=''
            form.password_hash.data=''
            flash('Email Already Exists...')
    users=User.query.order_by(User.date_added).all()
    return render_template('add_user.html',form=form,our_users=users)
    
# 2) Update User

@app.route('/update_user/<int:id>',methods=['GET','POST'])
@login_required
def update_user(id):
    form=UserForm()
    user=User.query.get_or_404(id)

    if request.method=='POST':
        user.name=request.form['name']
        user.username=request.form['username']
        user.email=request.form['email']
        try:
            db.session.commit()
            flash('User Updated Successfully')
            return redirect(url_for('dashboard'))
        except:
            flash('OOps an Error Occurred')
            return render_template('update_user.html',form=form)
    else:
        return render_template('update_user.html',form=form,user=user)

# 3) Delete User

@app.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    user=User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User Deleted Successfully')
        return redirect(url_for('home'))
    except:
        flash('Oops, Something Went Wrong try again')
        return redirect(url_for('dashboard'))
    

'''
Creating,Updating,Delete Posts
'''

# 1 Create Post
@app.route("/post/add",methods=['GET','POST'])
@login_required
def create_post():
    form=PostForm()
    if form.validate_on_submit():
        poster_id=current_user.id
        post=Posts(title=form.title.data,content=form.content.data,poster_id=poster_id)
        form.title.data=''
        form.content.data=''
        db.session.add(post)
        db.session.commit()
        flash('Post Created Successfully...')
        return redirect(url_for('posts'))

    return render_template('add_post.html',form=form)
    
# 2) Update Post

@app.route('/update_post/<int:id>',methods=['GET','POST'])
@login_required
def update_post(id):
    post=Posts.query.get_or_404(id)
    form =PostForm()
    if form.validate_on_submit():
        post.title=form.title.data
        post.content=form.content.data

        db.session.add(post)
        db.session.commit()
        flash('Post has Been Updated')
        return redirect(url_for('view_post',id=id))
    
    form.title.data= post.title
    form.content.data=post.content
    return render_template('update_post.html',form=form)
   

# 3) Delete Post

@app.route('/delete_post/<int:id>')
@login_required
def delete_post(id):
    post=Posts.query.get_or_404(id)
    id=current_user.id
    if id==post.poster.id:
        try:
            db.session.delete(post)
            db.session.commit()
            flash("Post Deleted Successfully")
            return redirect(url_for('posts'))
        except:
            flash("Oops and error occurred")
            return redirect(url_for('posts'))

    else:
        flash('You aren\'t Authorized to Delete this post ')
        return redirect(url_for('posts'))


# 4) view a post
@app.route('/post/<int:id>')
def view_post(id):
    post=Posts.query.get_or_404(id)
    return render_template('view_post.html',post=post)

# 5) view all posts
@app.route('/posts')
def posts():
    posts=Posts.query.order_by(Posts.date_posted)
    return render_template('all_posts.html',posts=posts)


######################===MODELS===#######################

from app import db
from datetime import datetime
from werkzeug.security import check_password_hash,generate_password_hash


class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(255),nullable=False,unique=True)
    name=db.Column(db.String(255),nullable=False)
    email=db.Column(db.String(255),nullable=False,unique=True)
    date_added=db.Column(db.DateTime,default=datetime.utcnow())
    password_hash=db.Column(db.String(255))

    # User can create many Blogs(Posts)
    posts=db.relationship('Posts',backref='poster')

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
    

    def _repr__(self):
        return "<Name %r"%self.name
    
class Posts(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(255),nullable=False)
    content=db.Column(db.Text)
    poster_id=db.Column(db.ForeignKey('user.id'))
    date_posted=db.Column(db.DateTime,default=datetime.utcnow())
    
    