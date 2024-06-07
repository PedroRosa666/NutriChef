from flask import render_template, url_for, flash, redirect, request
from app import app, db, login_manager
from forms import RegistrationForm, LoginForm, RecipeForm, RatingForm
from models import User, Recipe, Favorite, Rating, Notification
from flask_login import login_user, current_user, logout_user, login_required

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
@app.route("/home")
def home():
    recipes = Recipe.query.all()
    return render_template('home.html', recipes=recipes)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/recipe/new", methods=['GET', 'POST'])
@login_required
def new_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        recipe = Recipe(title=form.title.data, ingredients=form.ingredients.data, instructions=form.instructions.data, nutrition_info=form.nutrition_info.data, author=current_user)
        db.session.add(recipe)
        db.session.commit()
        flash('Your recipe has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_recipe.html', title='New Recipe', form=form, legend='New Recipe')

@app.route("/recipe/<int:recipe_id>")
def recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe.html', title=recipe.title, recipe=recipe)

@app.route("/recipe/<int:recipe_id>/favorite", methods=['POST'])
@login_required
def favorite_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    favorite = Favorite(user_id=current_user.id, recipe_id=recipe.id)
    db.session.add(favorite)
    db.session.commit()
    flash('Recipe added to favorites!', 'success')
    return redirect(url_for('recipe', recipe_id=recipe.id))

@app.route("/recipe/<int:recipe_id>/rate", methods=['GET', 'POST'])
@login_required
def rate_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    form = RatingForm()
    if form.validate_on_submit():
        rating = Rating(rating=form.rating.data, comment=form.comment.data, user_id=current_user.id, recipe_id=recipe.id)
        db.session.add(rating)
        db.session.commit()
        flash('Your rating has been submitted!', 'success')
        return redirect(url_for('recipe', recipe_id=recipe.id))
    return render_template('rate_recipe.html', title='Rate Recipe', form=form, recipe=recipe)

@app.route("/notifications")
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).all()
    return render_template('notifications.html', title='Notifications', notifications=notifications)

@app.route("/admin")
@login_required
def admin():
    if current_user.username != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    users = User.query.all()
    recipes = Recipe.query.all()
    return render_template('admin.html', title='Admin', users=users, recipes=recipes)
