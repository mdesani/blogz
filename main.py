from flask import Flask, request, redirect, render_template,session,flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:megha28@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'qwerty123'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
        
class Users(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owner', lazy='dynamic')

    def __init__(self, username, password):
        self.username = username
        self.password = password
        

@app.before_request
def require_login():
    allowed_routes = ['login','signup','blog','index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login' , methods=['POST','GET'])
def login():
    if request.method  == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Users.query.filter_by(username=username).first()
        if user :
            if user.password == password:
                session['username'] = username
                flash("Logged in")
                return redirect('/newpost')
            else:
                flash('User password incorrect.','error' )
                return redirect('/login')
        else:
            flash('User does notexist.Please sign up','error' )
            return redirect('/signup')
    return render_template('login.html',pgtitle='Login Information')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method =='POST':
        user = request.form['username']
        password = request.form['password']
        vrfy_passwrd = request.form['vrfy_passwrd']
        exist_user=Users.query.filter_by(username=user).first()
        if exist_user :
            flash("User already exists")
            return redirect("/signup")
        if user =='' :
            error = "Please specify the valid username."
            return redirect("/signup?nmerror=" + error)
        if len(user) < 3 :
            error = "Username should be more than 3 characters."
            return redirect("/signup?nmerror=" + error)
        if password =='':
            error = "Password required."
            return redirect("/signup?pwerror=" + error +"&username=" + user)
        if len(password) < 3 :
            error = "Password should be more than 3 characters."
            return redirect("/signup?pwerror=" + error +"&username=" + user)
        if password != vrfy_passwrd :
            error = "Oops password must match."
            return redirect("/signup?vpwerror=" + error +"&username=" + user)     
        
        new_user = Users(user,password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = user
        flash("You are now signed up")
        return redirect('/newpost')
    nmerror = request.args.get("nmerror")
    pwerror = request.args.get("pwerror") 
    vpwerror = request.args.get("vpwerror")
    username = request.args.get("username")  
    if not username :
        username = ''  
    
    return render_template('signup.html', pgtitle='Signup', nmerror = nmerror, pwerror = pwerror, vpwerror = vpwerror, username = username)
        



@app.route('/', defaults={'id':0,'username':''})
@app.route('/details/<int:id>',defaults={'username':''})
@app.route('/details/<username>',defaults={'id':0})
def index(id,username):
    if id:
        blog = Blog.query.get(id)
        return render_template('details.html',pgtitle="Blog Details",blog=blog)

    if username:
        user = Users.query.filter_by(username=username).first()
        blogs=Blog.query.filter_by(owner=user).all()
        return render_template('details.html',pgtitle="Blog Details",blogs=blogs)
    users = Users.query.filter_by().all()
    return render_template('index.html',pgtitle="Users",users=users)  

@app.route('/blog')
def blog():
    blogs = Blog.query.filter_by().all()
    return render_template('blog.html',pgtitle="Blog Posts",blogs=blogs)  

@app.route('/newpost', methods=['POST','GET'])
def new_post():
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        owner = Users.query.filter_by(username=session['username']).first()
        blog = Blog.query.filter_by(owner=owner,title=blog_title).all()
        if blog:
            error = "Title already exists."
            return redirect("/newpost?title_error=" + error)
        if blog_title =='':
            error = "Please specify the blog title."
            return redirect("/newpost?title_error=" + error)
        if blog_body =='':
            error = "Please specify the blog content."
            return redirect("/newpost?bad_error=" + error+"&title=" +blog_title)
    
        new_blog = Blog(blog_title,blog_body,owner)
        db.session.add(new_blog)
        db.session.commit()
        return render_template('/details.html',blog=new_blog)
        
    title_error = request.args.get("title_error")
    bad_error = request.args.get("bad_error")   
    blog_title = request.args.get("title")
    
    if not blog_title:
        blog_title='' 
    return render_template('newpost.html',pgtitle='Add A Blog Post',title_error=title_error,bad_error=bad_error,title = blog_title)


if __name__ == '__main__':
    app.run()