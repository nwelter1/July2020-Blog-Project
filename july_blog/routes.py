from july_blog import app, db, Message, mail
from flask import render_template, request, redirect, url_for
from july_blog.forms import UserInfoForm, BlogPostForm, LoginForm
# Import for Models
from july_blog.models import User, Post, check_password_hash
#import for flask login
from flask_login import login_required, login_user, current_user, logout_user
#Home route
@app.route('/')
def home():
    posts = Post.query.all()
    return render_template("home.html", posts=posts)

#Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserInfoForm()
    if request.method =='POST' and form.validate():
        # Get Information
        username = form.username.data
        password = form.password.data
        email = form.email.data
        print("\n",username, password, email)
        # Create an instance of User
        user = User(username, email, password)
        # Open and insert into database
        db.session.add(user)
        # Save info into database
        db.session.commit()
        #Flask email sender
        msg = Message(f"Thanks for signing up, {username}!", recipients=[email])
        msg.body = ('Congrats on signing up! Looking forawrd to your posts!')
        msg.html = ('<h1>Welcome to the July Blog!</h1>' '<p>This will be fun.</p>')

        mail.send(msg)
    return render_template("register.html", form=form)

#CreatePosts Route
@app.route('/createposts', methods=['GET','POST'])
@login_required
def createposts():
    form = BlogPostForm()
    if request.method == 'POST' and form.validate():
        title = form.title.data
        content = form.content.data
        user_id = current_user.id
        print('\n', title, content)
        post = Post(title, content, user_id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('createposts'))
    return render_template("createposts.html", form=form)

#Create route for retrieve methods
@app.route('/posts/<int:post_id>')
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

# Create route for updating forms
@app.route('/posts/update/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_update(post_id):
    post = Post.query.get_or_404(post_id)
    update_form = BlogPostForm()

    if request.method == 'POST' and update_form.validate():
        title = update_form.title.data
        content = update_form.content.data
        user_id = current_user.id

        # update post with form info
        post.title = title
        post.content = content
        post.user_id = user_id

        #Commit change to db
        db.session.commit()
        return redirect(url_for('post_update', post_id=post.id))
    return render_template('post_update.html', update_form=update_form)

#Create route for delete forms
@app.route('/posts/delete/<int:post_id>', methods=['POST'])
def post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('home'))

#login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method =='POST' and form.validate():
        email = form.email.data
        password = form.password.data
        logged_user = User.query.filter(User.email == email).first()
        if logged_user and check_password_hash(logged_user.password, password):
            login_user(logged_user)
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))