from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, AddAuctionItemForm
from models import db, User, AuctionItem, Bid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auction.db'
app.config['SECRET_KEY'] = 'supersecretkey'
db.init_app(app)

# Налаштування Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    items = AuctionItem.query.all()
    return render_template('index.html', items=items)

@app.route('/auction')
def auction():
    items = AuctionItem.query.all()
    return render_template('auction.html', items=items)

@app.route('/item/<int:item_id>', methods=['GET', 'POST'])
def item(item_id):
    item = AuctionItem.query.get_or_404(item_id)
    bids = Bid.query.filter_by(item_id=item_id).order_by(Bid.amount.desc()).all()

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash("Увійдіть, щоб зробити ставку.", "danger")
            return redirect(url_for('login'))
        
        amount = float(request.form['amount'])
        if amount <= item.current_bid:
            flash("Ставка має бути вищою за поточну ціну.", "danger")
            return redirect(url_for('item', item_id=item_id))
        
        new_bid = Bid(bidder_name=current_user.username, amount=amount, item_id=item_id)
        item.current_bid = amount
        db.session.add(new_bid)
        db.session.commit()
        flash("Ставку зроблено!", "success")
        return redirect(url_for('item', item_id=item_id))
    
    return render_template('item.html', item=item, bids=bids)

@app.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_auction_item():
    form = AddAuctionItemForm()  
    if form.validate_on_submit():  
        new_item = AuctionItem(
            name=form.name.data,
            description=form.description.data,
            starting_price=form.starting_price.data,
            current_bid=form.starting_price.data,
            image_url=form.image_url.data
        )
        db.session.add(new_item)
        db.session.commit()
        flash("Лот додано!", "success")
        return redirect(url_for('index'))

    return render_template('add_item.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Цей email вже використовується!", "danger")
            return redirect(url_for('register'))
        
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Реєстрація успішна!", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Ви увійшли!", "success")
            return redirect(url_for('index'))
        flash("Неправильний email або пароль.", "danger")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Ви вийшли.", "info")
    return redirect(url_for('login'))

@app.cli.command('init-db')
def init_db():
    db.create_all()
    print("База даних створена!")

if __name__ == '__main__':
    app.run(debug=True)


