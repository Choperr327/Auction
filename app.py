from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, Item, Bid
import click

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auction.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'

# Ініціалізація db з додатком
db.init_app(app)

# Ініціалізація Flask-Admin
admin = Admin(app, name='Аукціон', template_mode='bootstrap3')

# Додавання моделей до адмін-панелі
admin.add_view(ModelView(Item, db.session))
admin.add_view(ModelView(Bid, db.session))

@app.cli.command('init-db')
def init_db():
    """Створення бази даних і таблиць."""
    db.create_all()
    print("База даних створена!")

@app.route('/')
def index():
    items = Item.query.all()
    return render_template('index.html', items=items)

@app.route('/item/<int:item_id>')
def item(item_id):
    item = Item.query.get_or_404(item_id)
    bids = Bid.query.filter_by(item_id=item_id).order_by(Bid.amount.desc()).all()
    return render_template('item.html', item=item, bids=bids)

@app.route('/item/<int:item_id>/bid', methods=['POST'])
def bid(item_id):
    item = Item.query.get_or_404(item_id)
    bidder_name = request.form['bidder_name']
    amount = float(request.form['amount'])

    if amount <= item.current_price:
        return "Ставка повинна бути вищою за поточну ціну."

    new_bid = Bid(bidder_name=bidder_name, amount=amount, item_id=item_id)
    item.current_price = amount
    db.session.add(new_bid)
    db.session.commit()

    return redirect(url_for('item', item_id=item_id))

@app.route('/auction')
def auction():
    items = Item.query.all()
    return render_template('auction.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)



