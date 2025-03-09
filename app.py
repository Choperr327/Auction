from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import rules
from forms import RegisterForm, LoginForm, AddAuctionItemForm
from models import db, User, AuctionItem, Bid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auction.db'  # Database URI
app.config['SECRET_KEY'] = 'supersecretkey'  # Secret key for sessions
db.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Flask-Admin setup
admin = Admin(app, name='Auction Admin', template_mode='bootstrap3')

# AuctionItem Admin View for managing Auction Items
class AuctionItemAdmin(ModelView):
    form = AddAuctionItemForm
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin  # only for admins

    column_list = ('name', 'description', 'starting_price', 'current_bid')
    form_columns = ('name', 'description', 'starting_price')

    # Set current bid to the starting price when a new item is created
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.current_bid = model.starting_price
        return super().on_model_change(form, model, is_created)

# Add AuctionItem model to Flask-Admin
admin.add_view(AuctionItemAdmin(AuctionItem, db.session))

# User Admin View for managing Users
class UserAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin  # only for admins

admin.add_view(UserAdmin(User, db.session))

# Home page (Auction items list)
@app.route('/')
def index():
    items = AuctionItem.query.all()
    return render_template('index.html', items=items)

# Item details page with bidding functionality
@app.route('/item/<int:item_id>', methods=['GET', 'POST'])
def item(item_id):
    item = AuctionItem.query.get_or_404(item_id)
    bids = Bid.query.filter_by(item_id=item_id).order_by(Bid.amount.desc()).all()

    if request.method == 'POST':
        if current_user.is_authenticated:
            amount = float(request.form['amount'])
            if amount <= item.current_bid:
                flash("Bid must be higher than current price.", "danger")
                return redirect(url_for('item', item_id=item_id))

            new_bid = Bid(bidder_name=current_user.username, amount=amount, item_id=item_id)
            item.current_bid = amount
            db.session.add(new_bid)
            db.session.commit()
            flash("Bid placed successfully!", "success")
            return redirect(url_for('item', item_id=item_id))
        else:
            flash("You must log in to place a bid.", "danger")
            return redirect(url_for('login'))

    return render_template('item.html', item=item, bids=bids)

# Register user
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("This email is already in use!", "danger")
            return redirect(url_for('register'))

        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# Login user
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))
        flash("Invalid email or password.", "danger")
    return render_template('login.html', form=form)


@app.route('/auction')
def auction():
    return render_template('auction.html')

# Log out user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logged out.", "info")
    return redirect(url_for('login'))

# Admin dashboard and database initialization
@app.cli.command('init-db')
def init_db():
    db.create_all()
    print("Database created!")

if __name__ == '__main__':
    app.run(debug=True)

