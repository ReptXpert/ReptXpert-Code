#Bis und mit Zeile 199 mehrheitlich aus Emanuel Grimbergs Blog übernommen
from datetime import datetime, timedelta
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, \
    EmptyForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm, TerrariumForm, EventForm
from app.models import User, Post, Terrarium, Event
from app.email import send_password_reset_email, send_email

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Dein Post ist jetzt sichtbar!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Erkunden', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Falscher Benutzername oder Passwort')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Anmelden', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Willkommen bei ReptXpert!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Registrieren', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Pruefe deinen Email-Posteingang um ein neues Passwort zu erstellen.')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Passwort vergessen', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Du kannst dich jetzt mit deinem neuen Passwort anmelden.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    terrariums = user.terrariums
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url,
                           form=form, terrariums=terrariums)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Deine Anpassungen sind gespeichert.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Profil bearbeiten',
                           form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('Benutzer {} nicht gefunden'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('Du kannst dich nicht selber abonieren')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('Du folgst {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('Benutzer {} nicht gefunden.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('Du kannst dich nicht selber unabonieren!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('Du folgst {} nicht.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))
#Bis und mit Zeile 256 eigener Code
@app.route('/create-terrarium', methods=['GET', 'POST'])
@login_required
def create_terrarium():
    form = TerrariumForm()
    if form.validate_on_submit():
        terrarium = Terrarium(name=form.name.data,
                              size=form.size.data,
                              optimal_humidity=form.optimal_humidity.data,
                              optimal_temperature=form.optimal_temperature.data,
                              actual_humidity=form.actual_humidity.data,
                              actual_temperature=form.actual_temperature.data,
                              country=form.country.data,
                              sunrise_time=form.sunrise_time.data,
                              sunset_time=form.sunset_time.data,
                              notes=form.notes.data,
                              owner=current_user)
        db.session.add(terrarium)
        db.session.commit()
        flash('Terrarium erfolgreich erstellt!', 'success')
        return redirect(url_for('index'))
    return render_template('new_terrarium.html', title='Neues Terrarium', form=form)

@app.route('/delete_terrarium/<int:terrarium_id>', methods=['POST'])
@login_required
def delete_terrarium(terrarium_id):
    terrarium = Terrarium.query.get(terrarium_id)
    if terrarium is None or terrarium.user_id != current_user.id:
        flash('Du hast keine Berechtigung, dieses Terrarium zu löschen.')
        return redirect(url_for('user', username=current_user.username))
    db.session.delete(terrarium)
    db.session.commit()
    flash('Das Terrarium wurde gelöscht.')
    return redirect(url_for('user', username=current_user.username))

@app.route('/edit_terrarium/<int:terrarium_id>', methods=['GET', 'POST'])
@login_required
def edit_terrarium(terrarium_id):
    terrarium = Terrarium.query.get_or_404(terrarium_id)
    if terrarium.user_id != current_user.id:
        flash('Du hast keine Berechtigung, dieses Terrarium zu bearbeiten.', 'danger')
        return redirect(url_for('user', username=current_user.username))
    form = TerrariumForm(obj=terrarium)
    if form.validate_on_submit():
        terrarium.name = form.name.data
        terrarium.size = form.size.data
        terrarium.optimal_humidity = form.optimal_humidity.data
        terrarium.optimal_temperature = form.optimal_temperature.data
        terrarium.actual_humidity = form.actual_humidity.data
        terrarium.actual_temperature = form.actual_temperature.data
        terrarium.country = form.country.data
        terrarium.sunrise_time = form.sunrise_time.data
        terrarium.sunset_time = form.sunset_time.data
        terrarium.notes = form.notes.data
        db.session.commit()
        flash('Terrarium erfolgreich bearbeitet!', 'success')
        return redirect(url_for('terrarium', terrarium_id=terrarium_id))
    return render_template('edit_terrarium.html', title='Terrarium bearbeiten', form=form)

@app.route('/calendar')
@login_required
def calendar():
    today = datetime.utcnow()
    events = Event.query.filter_by(user_id=current_user.id).order_by(Event.start_time).all()
    return render_template('user.html', events=events, today=today)

@app.route('/event/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        title = request.form.get('title')
        start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
        description = request.form.get('description')
        event = Event(title=title, start_time=start_time, end_time=end_time, description=description, user_id=current_user.id)
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('calendar'))
    return render_template('create_event.html')

@app.route('/event/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        event.title = request.form.get('title')
        event.start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
        event.end_time = datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
        event.description = request.form.get('description')
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('calendar'))
    return render_template('edit_event.html', event=event)

@app.route('/event/delete/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        abort(403)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('calendar'))

