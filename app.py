from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auction.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'

db = SQLAlchemy(app)

# Ініціалізація Flask-Admin
admin = Admin(app, name='Аукціон', template_mode='bootstrap3')

# Моделі
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    starting_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    bids = db.relationship('Bid', backref='item', lazy=True)

class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bidder_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)

# Додавання моделей до адмін-панелі
admin.add_view(ModelView(Item, db.session))
admin.add_view(ModelView(Bid, db.session))

@app.before_first_request
def create_tables():
    db.create_all()

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

if __name__ == '__main__':
    app.run(debug=True)