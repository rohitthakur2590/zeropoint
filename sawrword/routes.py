import secrets
from PIL import Image
from flask import render_template, flash, request, redirect, url_for, abort
from sawrword import app, db, mail
from sawrword.models import User, Post, Article, Journal, Note, Subscription, Subscriber, Forum, Fpost
from sawrword.forms import (LoginForm, RegisterForm, UpdateProfileForm, CommandToSendForm,
	                        OutputForm, PostForm, ArticleForm, JournalForm, NoteForm,
	                        ContactForm, RequestResetForm, ResetPasswordForm, FpostForm)
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import LoginManager, login_user,login_required, logout_user, current_user

from lxml.etree import XMLSyntaxError
from lxml.etree import tostring
from xml.etree  import ElementTree as ET
from flask_mail import Message


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))



@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts= Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    articles= Article.query.order_by(Article.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('index.html', posts=posts, articles = articles)

@app.route('/about_us')
def about_us():
	return render_template('about_us.html')

@app.route('/terms')
def terms():
	return render_template('terms.html')

@app.route('/forums', methods=['GET', 'POST'])
def forums():
	form = FpostForm()
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	if form.validate_on_submit() and request.method == 'POST':
		new_fpost = Forum(firstname=current_user.firstname,
 			            lastname=current_user.lastname,
 			            username=current_user.username,
 			            image_file=img_file,
 			            content=form.content.data)
		db.session.add(new_fpost)
		db.session.commit()
		flash('Query posted successfully !', 'success')
		return redirect(url_for('forums'))
	elif request.method == 'GET':
	    form.content.data = " "
	    page = request.args.get('page', 1, type=int)
	    forums= Forum.query.order_by(Forum.date_posted.desc()).paginate(page=page, per_page=5)
	    fposts= Fpost.query.order_by(Fpost.date_posted.desc())
	    return render_template('forums.html',forums=forums,form = form,fposts=fposts)


@app.route('/reply', methods=['GET', 'POST'])
def  reply():
	form =  FpostForm()
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	page = request.args.get('page', 1, type=int)
	forums= Forum.query.order_by(Forum.date_posted.desc()).paginate(page=page, per_page=5)

	if form.validate_on_submit():
		reply= Fpost(firstname=current_user.firstname,
 			            lastname=current_user.lastname,
 			            username=form.identity,
 			            image_file=img_file,
 			            content=form.content.data,
 			            author=form.identity )

		db.session.add(reply)
		db.session.commit()
		flash('Reply posted successfully!', category='success')
		return redirect(url_for('forums'))
	fposts= Fpost.query.order_by(Fpost.date_posted.desc())
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('forums.html', forums=forums,image_file=img_file, form=form, fposts=fposts,legend = '')



@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		#looking for user in database
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			if check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				return redirect(url_for('dashboard'))
			flash('Invalid username or password!', category='danger')
			return render_template('login.html', form=form)
		flash('User Not registered! Please Sign Up', category='danger')
		return render_template('login.html', form=form)
		#return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
	return render_template('login.html', form=form)
'''
sha256 will generate 80 characters long password
'''
@app.route('/signup', methods=['GET', 'POST'])
def signup():
 	form = RegisterForm()
 	if form.validate_on_submit():
 	    hash_password = generate_password_hash(form.password.data, method='sha256')
 	    new_user = User(firstname=form.firstname.data,
 			            lastname=form.lastname.data,
 			            username=form.username.data,
 			            email=form.email.data,
 			            password=hash_password)

 	    user = User.query.filter_by(email=form.email.data).first()
 	    if user:
 	        flash('User with this email account already registered', 'success')
 	        return redirect(url_for('signup'))
 	    user = User.query.filter_by(username=form.username.data).first()

 	    if user:
 	    	flash('This username already taken !', 'success')
 	    	return redirect(url_for('signup'))

 	    db.session.add(new_user)
 	    db.session.commit()
 	    flash(f'Sign Up successful for {form.firstname.data}!', 'success')
 	    return render_template('index.html')


 		#return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

 	return render_template('signup.html', form=form)


@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
	form = ContactForm()

	if form.validate_on_submit():
		#looking for user in database
		flash('We have received your message successfully',category='success')
		#send_query_email(form.email, form.content)

	return render_template('contact_us.html', form=form)

def send_query_email(email, content):
	msg = Message('Password Reset Request', sender='sawrword@gmail.com', recipients=sawrword@gmail.com)
	mail.send( content )

@app.route('/notepad', methods=['GET', 'POST'])
@login_required
def notepad():
	#form for input notes
	form = CommandToSendForm()
	outputform = OutputForm()

	command = ""

	#parse button_input.xml
	buttons = parse_buttons()
	button_list = sorted(buttons.items())
	if request.method == 'POST' :
		if 'btn_template' in request.form:
			command = read_command_template(request, buttons)
			#set command into command box
			form.command.data = command
		if 'save' in request.form:
			command = request.form['command'].encode('utf-8')

		return render_template('notepad.html',
    		                    command = command,
    		                    buttons=buttons_list,
    		                    form=form,
    		                    output=output.xml,
    		                    outputform=outputform)

	return render_template('notepad.html', form=form,  outputform=outputform)

def parse_buttons():
	XMLtree = ET.parse('button_template/button_config.xml')
	root = XMLtree.getroot()
	button = {}
	for button in root.findall('button'):
		title = button.find('title')
		button[0] = render_template
	return button

@app.route('/dashboard')
@login_required
def dashboard():
	page = request.args.get('page', 1, type=int)
	posts= Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	articles= Article.query.order_by(Article.date_posted.desc()).paginate(page=page, per_page=5)
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('dashboard.html', name=current_user.firstname, image_file=img_file, posts=posts, articles = articles)

@app.route('/subscriptions_home')
@login_required
def subscriptions_home():
	page = request.args.get('page', 1, type=int)
	subscriptions= Subscription.query.filter_by(author=current_user).order_by(Subscription.date_added.desc()).paginate(page=page, per_page=5)
	posts= Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	articles= Article.query.order_by(Article.date_posted.desc()).paginate(page=page, per_page=5)
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	if not subscriptions :
		flash('You have no subscriptions!',category="warning")

	return render_template('subscriptions_home.html',
		                   name=current_user.firstname,
		                   uname=current_user.username,
		                   image_file=img_file,
		                   posts=posts,
		                   articles = articles,
		                   subscriptions=subscriptions)


@app.route('/subscribers_home')
@login_required
def subscribers_home():
	user = User.query.filter_by(username=current_user.username).first_or_404()
	subscribers= Subscriber.query.filter_by(author=current_user)
	page = request.args.get('page', 1, type=int)
#	subscribers= Subscrber.query.order_by(Subscription.date_added.desc()).paginate(page=page, per_page=5)
	posts= Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	articles= Article.query.order_by(Article.date_posted.desc()).paginate(page=page, per_page=5)
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	if not subscribers :
		flash('You have no subscribers!',category="warning")

	return render_template('subscribers_home.html',
		                   name=current_user.firstname,
		                   image_file=img_file,
		                   posts=posts,
		                   articles = articles,
		                   subscribers=subscribers)




@app.route('/dash_blog')
@login_required
def dash_blog():
	page = request.args.get('page', 1, type=int)
	posts= Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('dash_blog.html', name=current_user.firstname, image_file=img_file, posts=posts)

@app.route('/dash_note')
@login_required
def dash_note():
	page = request.args.get('page', 1, type=int)
	notes= Note.query.order_by(Note.date_posted.desc()).paginate(page=page, per_page=5)
	if not notes.items:
	    flash("You don't have any note entry", category='warning')
	    flash("Notes are private and only you can view them ", category='success')
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('dash_note.html', name=current_user.firstname, image_file=img_file, notes=notes)

@app.route('/dash_journal')
@login_required
def dash_journal():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    page = request.args.get('page', 1, type=int)
    journals= Journal.query.filter_by(author=user).order_by(Journal.date_posted.desc()).paginate(page=page, per_page=5)
    if not journals.items:
        flash("You don't have any journal entry", category='warning')
        flash("Journal is private and only you can view it ", category='success')

    img_file = url_for('static', filename='display_pics/' + current_user.image_file)
    return render_template('dash_journal.html', name=current_user.firstname, image_file=img_file, journals=journals)




@app.route('/dash_article')
@login_required
def dash_article():
	page = request.args.get('page', 1, type=int)
	articles= Article.query.order_by(Article.date_posted.desc()).paginate(page=page, per_page=5)
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('dash_article.html', name=current_user.firstname, image_file=img_file, articles=articles)


@app.route('/profession')
@login_required
def profession():
	form = UpdateProfileForm()
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('profession.html', name=current_user.firstname, image_file=img_file, form=form)


@app.route('/profile')
@login_required
def profile():
	form = UpdateProfileForm()
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('profile.html', name=current_user.firstname, image_file=img_file, form=form)

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex+ f_ext
	picture_path = os.path.join(app.root_path, 'static/display_pics', picture_fn)

	output_size = (200, 200)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = UpdateProfileForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file

		current_user.firstname = form.firstname.data
		current_user.lastname = form.lastname.data
		current_user.username = form.username.data
		current_user.email= form.email.data
		db.session.commit()
		flash('Profile Updated Successfully', 'success')
		return redirect(url_for('profile'))
	elif request.method == 'GET':
		form.firstname.data = current_user.firstname
		form.lastname.data = current_user.lastname
		form.username.data = current_user.username
		form.email.data = current_user.email
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('edit_profile.html', name=current_user.firstname, image_file=img_file, form=form)



@app.route('/my_blog', methods=['GET', 'POST'])
@login_required
def my_blog():
	form = PostForm()

	if form.validate_on_submit():
		post= Post(title=form.title.data, content=form.content.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post has been created!', category='success')
		return redirect(url_for('profile'))
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('my_blog.html', image_file=img_file, form=form, legend = 'Create Post')

@app.route('/my_article', methods=['GET', 'POST'])
@login_required
def my_article():
	form = ArticleForm()

	if form.validate_on_submit():
		article= Article(title=form.title.data, content=form.content.data, author=current_user)
		db.session.add(article)
		db.session.commit()
		flash('Your Article has been published!', category='success')
		return redirect(url_for('profile'))
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('my_article.html', image_file=img_file, form=form, legend = 'Create Article')

@app.route('/my_journal', methods=['GET', 'POST'])
@login_required
def my_journal():
	form = JournalForm()

	if form.validate_on_submit():
		journal= Journal(title=form.title.data, content=form.content.data, author=current_user)
		db.session.add(journal)
		db.session.commit()
		flash('Your Journal has been published!', category='success')
		return redirect(url_for('profile'))
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('my_journal.html', image_file=img_file, form=form, legend = 'Create Journal')

@app.route('/my_note', methods=['GET', 'POST'])
@login_required
def my_note():
	form = NoteForm()

	if form.validate_on_submit():
		note= Note(title=form.title.data, content=form.content.data, author=current_user)
		db.session.add(note)
		db.session.commit()
		flash('Note added successfully!', category='success')
		return redirect(url_for('profile'))
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('my_note.html', image_file=img_file, form=form, legend = '')

@app.route("/<int:post_id>")
def post(post_id):
	post =Post.query.get_or_404(post_id)
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('post.html',  image_file=img_file, title=post.title, post=post)

@app.route('/article/<int:article_id>')
def article(article_id):
	article =Article.query.get_or_404(article_id)
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('article.html',  image_file=img_file, title=article.title, article=article)

@app.route('/note/<int:note_id>')
def note(note_id):
	note =Note.query.get_or_404(note_id)
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('note.html',  image_file=img_file, title=note.title, note=note)

@app.route('/journal/<int:journal_id>')
def journal(journal_id):
	journal =Journal.query.get_or_404(journal_id)
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('journal.html',  image_file=img_file, title=journal.title, journal=journal)

@app.route("/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
	post =Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash('Post updated successfully!', category='success')
		return redirect(url_for('post', post_id = post.id))
	elif request.method == 'GET':
		form.title.data =post.title
		form.content.data = post.content
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('update_post.html', image_file=img_file, form=form,
		legend = 'Update Post')

@app.route("/subscribe/<string:username>", methods=['GET', 'POST'])
@login_required
def subscribe(username):
	subscribed_user = User.query.filter_by(username=username).first_or_404()
	img_file = url_for('static', filename='display_pics/' + subscribed_user.image_file)
	sub_img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	new_subscription = Subscription(firstname=subscribed_user.firstname,
 			            lastname=subscribed_user.lastname,
 			            username=subscribed_user.username,
 			            image_file=img_file,
 			            author = current_user)

	new_subscriber = Subscriber(firstname=current_user.firstname,
		                        lastname=current_user.lastname,
		                        username=current_user.username,
		                        image_file=sub_img_file,
		                        author=subscribed_user)

	db.session.add(new_subscription)
	db.session.commit()
	db.session.add(new_subscriber)
	db.session.commit()
	flash('Successfully added to subscriptions !', category='success')
	return redirect(url_for('subscriptions_home'))

@app.route("/unsubscribe/<int:subscription_id>", methods=['GET','POST'])
@login_required
def unsubscribe(subscription_id):
    subscription =Subscription.query.get_or_404(subscription_id)
    #subscriptions= Subscription.query.filter_by(author = current_user)
    #subscriptions= Subscription.query.filter_by(author=user).filter_by(username = username)
    #del_subscribe = Subscription.query.get_or_404(username)
    db.session.delete(subscription)
    db.session.commit()
    flash('Unsubscribed successfully!',category='success')
    return redirect(url_for('subscriptions_home'))


@app.route("/update_article/<int:article_id>", methods=['GET', 'POST'])
@login_required
def update_article(article_id):
	article =Article.query.get_or_404(article_id)
	if article.author != current_user:
		abort(403)
	form = ArticleForm()
	if form.validate_on_submit():
		article.title = form.title.data
		article.content = form.content.data
		db.session.commit()
		flash('Article updated successfully!', category='success')
		return redirect(url_for('article', article_id = article.id))
	elif request.method == 'GET':
		form.title.data =article.title
		form.content.data = article.content
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('update_article.html', image_file=img_file, form=form,
		legend = 'Update Article')


@app.route("/update_journal/<int:journal_id>", methods=['GET', 'POST'])
@login_required
def update_journal(journal_id):
	journal =Journal.query.get_or_404(journal_id)
	if journal.author != current_user:
		abort(403)
	form = JournalForm()
	if form.validate_on_submit():
		journal.title = form.title.data
		journal.content = form.content.data
		db.session.commit()
		flash('Journal updated successfully!', category='success')
		return redirect(url_for('journal', journal_id = journal.id))
	elif request.method == 'GET':
		form.title.data =journal.title
		form.content.data = journal.content
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('update_journal.html', image_file=img_file, form=form,
		legend = 'Update Journal')

@app.route("/update_note/<int:note_id>", methods=['GET', 'POST'])
@login_required
def update_note(note_id):
	note =Note.query.get_or_404(note_id)
	if note.author != current_user:
		abort(403)
	form = NoteForm()
	if form.validate_on_submit():
		note.title = form.title.data
		note.content = form.content.data
		db.session.commit()
		flash('Note updated successfully!', category='success')
		return redirect(url_for('note', note_id = note.id))
	elif request.method == 'GET':
		form.title.data =note.title
		form.content.data = note.content
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('update_note.html', image_file=img_file, form=form,
		legend = 'Update Note')



@app.route("/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
	post =Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Post deleted successfully!',category='success')
	return redirect(url_for('blog_home'))

@app.route("/<int:article_id>/delete", methods=['POST'])
@login_required
def delete_article(article_id):
	article =Article.query.get_or_404(article_id)
	if article.author != current_user:
		abort(403)
	db.session.delete(article)
	db.session.commit()
	flash('Article deleted successfully!',category='success')
	return redirect(url_for('blog_home'))

@app.route("/delete_journal/<int:journal_id>", methods=['POST'])
@login_required
def delete_journal(journal_id):
	journal =Journal.query.get_or_404(journal_id)
	if journal.author != current_user:
		abort(403)
	db.session.delete(journal)
	db.session.commit()
	flash('Journal deleted successfully!',category='success')
	return redirect(url_for('journal_home'))

@app.route("/delete_note/<int:note_id>", methods=['POST'])
@login_required
def delete_note(note_id):
	note =Note.query.get_or_404(note_id)
	if note.author != current_user:
		abort(403)
	db.session.delete(note)
	db.session.commit()
	flash('Note deleted successfully!',category='success')
	return redirect(url_for('note_home'))

@app.route('/blog_home', methods=['GET', 'POST'])
@login_required
def blog_home():
	page = request.args.get('page', 1, type=int)
	posts= Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	flash('Blogs are visible to all', category="success")
	return render_template('blog_home.html', image_file=img_file, posts=posts)

@app.route('/article_home', methods=['GET', 'POST'])
@login_required
def article_home():
	page = request.args.get('page', 1, type=int)
	articles= Article.query.order_by(Article.date_posted.desc()).paginate(page=page, per_page=5)
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	flash('Articles are visible to all', category="success")
	return render_template('article_home.html', image_file=img_file, articles=articles)

@app.route('/journal_home', methods=['GET', 'POST'])
@login_required
def journal_home():
	user = User.query.filter_by(username=current_user.username).first_or_404()
	page = request.args.get('page', 1, type=int)
	journals= Journal.query.filter_by(author=user).order_by(Journal.date_posted.desc()).paginate(page=page, per_page=5)
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	flash("Journal is private and only you can view it ", category='success')
	return render_template('journal_home.html', image_file=img_file, journals=journals)

@app.route("/user_specific_blog_home,<string:username>", methods=['GET', 'POST'])
@login_required
def user_specific_blog_home(username):
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	posts= Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	img_file = url_for('static', filename='display_pics/' + user.image_file)
	return render_template('user_specific_blog_home.html',
	                        firstname=user.firstname,
	                        image_file=img_file,
	                        posts=posts,
	                        username=user.username)


@app.route("/user_specific_article_home,<string:username>", methods=['GET', 'POST'])
@login_required
def user_specific_article_home(username):
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	articles= Article.query.filter_by(author=user).order_by(Article.date_posted.desc()).paginate(page=page, per_page=5)
	img_file = url_for('static', filename='display_pics/' + user.image_file)
	return render_template('user_specific_article_home.html',
	                       firstname=user.firstname,
	                       image_file=img_file,
	                       articles=articles,
	                       username=user.username)


@app.route('/note_home', methods=['GET', 'POST'])
@login_required
def note_home():
	user = User.query.filter_by(username=current_user.username).first_or_404()
	page = request.args.get('page', 1, type=int)
	notes= Note.query.filter_by(author=user).order_by(Note.date_posted.desc()).paginate(page=page, per_page=5)
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	flash("Notes are private and only you can view them ", category='success')
	return render_template('note_home.html', image_file=img_file, notes=notes)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))
'''
@app.route("/<int:post_id>")
def post(post_id):
	post =Post.query.get_or_404(post_id)
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('post.html',  image_file=img_file, title=post.title, post=post)
'''
@app.route("/<string:username>")
def user(username):
    subscribed = False
    self_profile = False
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(firstname=username).first_or_404()
    posts= Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    articles= Article.query.filter_by(author=user).order_by(Article.date_posted.desc()).paginate(page=page, per_page=5)
    subscriptions= Subscription.query.filter_by(author=current_user).order_by(Subscription.date_added.desc()).paginate(page=page, per_page=5)
    img_file = url_for('static', filename='display_pics/' + user.image_file)
    if user.username == current_user.username:
        self_profile = True
    for subscription in  subscriptions.items:
        if subscription.username == username:
            subscribed= True

    return render_template('user.html',
	                        name=user.firstname,
	                        username=user.username,
	                        image_file=img_file,
	                        posts=posts,
	                        articles = articles,
	                        subscribed=subscribed,
	                        subscriptions=subscriptions,
	                        self_profile=self_profile)


@app.route("/user_post/<string:username>")
def user_post():
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(firstname=username ).first_or_404()
	posts= Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('user_post.html', image_file=img_file, posts=posts, user=user)

'''
	articles= Article.query.filter_by(author=user).order_by(Article.date_posted.desc()).paginate(page=page, per_page=5)
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('user_article.html', image_file=img_file, articles=articles, user=user)
'''


def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender='sawrword@gmail.com', recipients=[user.email])

	msg.body = f'''To reset the password click the link below:
	{url_for('reset_token', token=token, _external=True)}
	lINK WILL EXPIRE IN 1 HOUR '''
	mail.send( msg )




@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('blog_home'))

	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('Please Check you email for password reset link', category='info')
		return redirect(url_for('login'))
	return render_template('reset_request.html', title= 'Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
			return redirect(url_for('blog_home'))

	user = User.verify_reset_token(token)
	if user is None:
		flash('Invalid or Expired Token', category='warning')
		return redirect(url_for('reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
 		hashed_password = generate_password_hash(form.password.data, method='sha256')
 		user.password = hashed_password
 		db.session.commit()
 		flash('Password updated  successfully for {form.firstname.data}!', 'success')
 		return redirect('login')
	return render_template('reset_token.html', title='Reset Password', form=form)