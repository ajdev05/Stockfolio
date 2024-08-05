from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from extensions import db
from models import User, Stock
import init_db as start_db
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stockfolio.db'
    db.init_app(app)

    @app.template_filter('format_date')
    def format_date(date):
        return date.strftime("%B %d, %Y at %I:%M %p")

    with app.app_context():
        db.create_all()

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                flash('Logged in successfully!', 'success')
                return redirect(url_for('index'))
            flash('Invalid username or password', 'danger')
        if 'user_id' in session:
            return redirect(url_for('index'))
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        flash('You have been logged out!', 'info')
        return redirect(url_for('login'))

    @app.route('/')
    def index():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        stocks = Stock.query.all()
        return render_template('portfolio.html', stocks=stocks)

    @app.route('/add_stock', methods=['POST'])
    def add_stock():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        ticker = request.form.get('ticker')
        name = request.form.get('name')
        shares = float(request.form.get('shares'))
        purchase_price = float(request.form.get('price'))
        purchase_date = request.form.get('purchase_date')

        if purchase_date:
            purchase_date = datetime.strptime(purchase_date, '%Y-%m-%dT%H:%M')
        else:
            purchase_date = datetime.utcnow()

        new_stock = Stock(
            ticker=ticker,
            name=name,
            shares=shares,
            purchase_price=purchase_price,
            purchase_date=purchase_date
        )
        db.session.add(new_stock)
        db.session.commit()
        flash('Stock added successfully!', 'success') 
        return redirect(url_for('index'))

    @app.route('/delete_stock/<int:stock_id>', methods=['POST'])
    def delete_stock(stock_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        stock = Stock.query.get_or_404(stock_id)
        db.session.delete(stock)
        db.session.commit()
        flash('Stock deleted successfully!', 'success')
        return redirect(url_for('index'))

    return app

if __name__ == "__main__":
    app = create_app()
    start_db.initialize_database()
    app.run(debug=True, host="0.0.0.0", port=5000)

