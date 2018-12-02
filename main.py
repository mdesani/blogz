from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:megha28@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body= db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', defaults={'id': 0})
@app.route('/blog/details/<int:id>')
def index(id):

    if id:
        blog = Blog.query.get(id)
        return render_template('details.html', pgtitle="Blog Details",blog=blog)

    blogs = Blog.query.filter_by().all()
    return render_template('blog.html',pgtitle="Build A Blog",blogs=blogs) 


@app.route('/blog/newpost', methods=['POST','GET'])
def new_post():
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        if blog_title =='':
            error = "Please specify the blog title."
            return redirect("/blog/newpost?title_error=" + error)
        if blog_body =='':
            error = "Please specify the blog content."
            return redirect("/blog/newpost?bad_error=" + error+"&blog_title=" +blog_title)
    
        new_blog = Blog(blog_title,blog_body)
        db.session.add(new_blog)
        db.session.commit()
        return render_template('/details.html',blog=new_blog)
        
    tit_error = request.args.get("title_error")
    bod_error = request.args.get("bad_error")   
    blog_title = request.args.get("blog_title")
    if not blog_title:
        blog_title=''
    return render_template('newpost.html',pgtitle='Build A Blog',title_error=tit_error,bad_error=bod_error,blog_title=blog_title)


if __name__ == '__main__':
    app.run()