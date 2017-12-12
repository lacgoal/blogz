# This web app will display blog posts on a main page and allows users to add new blog posts on a form page.
# After submitting a new blog entry on the form page, the user is redirected to a page that displays only that blog (rather than returning to the form page or to the main page).
#Each blog post has a title and a body. To get an idea what the finished project should look like and how it should function, check out this video:


from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:root@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    content = db.Column(db.Text)

    def __init__(self, title, content):
        self.title = title
        self.content = content

#display blog posts on a main page
@app.route ('/')
def index ():
    if request.args:
        post_id = request.args.get('id')
        blog_post = Blog.query.get(post_id)
        return render_template('post.html', title='Single Post', post = blog_post)

    blog_posts = Blog.query.all()
    return render_template('blog.html', title="Build A Blog", posts = blog_posts)


#submit a new post at the (newpost) route
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    post_title = ''
    post_title_error = ''
    post_content = ''
    post_content_error = ''

    #request user data
    if request.method == 'POST':
        post_title = request.form['post_title']
        post_content = request.form['post_content']

        #error checks
        if post_title == '':
            post_title_error = 'Enter a blog title'
        elif len(post_title) <= 5:
            post_title_error = 'Enter a longer title'
        elif (post_content == ''):
            post_content_error = 'Enter blog content'
        elif len(post_title) > 5:
            new_post = Blog(post_title, post_content)
            db.session.add(new_post)
            db.session.commit()

            post_id = new_post.id

            url = '/?id=' + str(post_id)
            return redirect(url)

    return render_template ('newpost.html', title = 'New Post', post_title = post_title, post_content = post_content, post_title_error = post_title_error, post_content_error = post_content_error)


if __name__ == '__main__':
    app.run()
