import os
import secrets
from flask import Flask, render_template, abort, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import models
from forms import Select_Pen, Add_Brand

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pens.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.secret_key = 'crazyhorse'

db = SQLAlchemy(app)

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'ludicrousmode'

# home page route
@app.route('/')
def home():
    brands = models.Brand.query.all()
    tags = models.Tag.query.all()
    return render_template('home.html', page_title='S', brands = brands, tags = tags)

# brand page route
@app.route('/brand/<int:id>')
def brand(id):
    brand = models.Brand.query.filter_by(id=id).first_or_404()
    return render_template('brand.html', page_title=' BRANDS', brand = brand)

# tag page route
@app.route('/tag/<int:id>')
def tag(id):
    tag = models.Tag.query.filter_by(id=id).first_or_404()
    return render_template('tag.html', page_title=' TAGS', tag = tag)

# pen page route
@app.route('/pen/<int:id>')
def pen(id):
    pen = models.Pen.query.filter_by(id=id).first_or_404()
    return render_template('pen.html', page_title=(' PENS'), pen = pen)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

# dropdown list form to select a pen
@app.route('/choose_pen', methods = ['GET', 'POST'])
def choose_pen():
    form = Select_Pen()
    pens = models.Pen.query.all()
    form.pens.choices = [(pen.id, pen.name) for pen in pens]
    if request.method == 'POST':
        if form.validate_on_submit():
            return redirect(url_for('pen', id = form.pens.data))
        else:
            abort(404)
            # uses a premade template. pen.html ????
    return render_template('pen.html', title = 'Select A Pen', form = form)

# save brand photo
def save_photo(form_photo):
    # give the file a random name to prevent errors with similar file names already in the database
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_photo.filename)
    photo_fn = random_hex + f_ext
    # save the uploaded photo to the database
    photo_path = os.path.join(app.root_path, 'static/images/brands', photo_fn)
    form_photo.save(photo_path)

    return photo_fn

# form to add a brand to the database
@app.route('/add_brand', methods = ['GET', 'POST'])
def add_brand():
    form = Add_Brand()
    # request to see the page
    if request.method=='GET':
        return render_template('add_brand.html', form = form, title = "Add a Brand")
    # form submitted to the server by a user
    else:
        if form.validate_on_submit():
            new_brand = models.Brand()
            new_brand.name = form.name.data
            new_brand.desc = form.desc.data
            if form.photo.data:
                photo_file = save_photo(form.photo.data)
                new_brand.photo = photo_file
            db.session.add(new_brand)
            db.session.commit()
            return redirect(url_for('brand', id=new_brand.id))
        else:
            return render_template('add_brand.html', form = form, title = "Add a Brand")


if __name__ == "__main__":
    app.run(debug=True)
