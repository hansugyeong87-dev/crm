from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    company = db.Column(db.String(100))
    position = db.Column(db.String(100))
    memo = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    if search_query:
        customers = Customer.query.filter(
            (Customer.name.contains(search_query)) |
            (Customer.phone.contains(search_query)) |
            (Customer.email.contains(search_query)) |
            (Customer.company.contains(search_query))
        ).order_by(Customer.name).all()
    else:
        customers = Customer.query.order_by(Customer.name).all()
    return render_template('index.html', customers=customers, search_query=search_query)

@app.route('/customer/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        try:
            customer = Customer(
                name=request.form['name'],
                phone=request.form.get('phone', ''),
                email=request.form.get('email', ''),
                company=request.form.get('company', ''),
                position=request.form.get('position', ''),
                memo=request.form.get('memo', '')
            )
            db.session.add(customer)
            db.session.commit()
            flash('고객이 성공적으로 추가되었습니다!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'오류가 발생했습니다: {str(e)}', 'danger')
    return render_template('customer_form.html', customer=None)

@app.route('/customer/edit/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        try:
            customer.name = request.form['name']
            customer.phone = request.form.get('phone', '')
            customer.email = request.form.get('email', '')
            customer.company = request.form.get('company', '')
            customer.position = request.form.get('position', '')
            customer.memo = request.form.get('memo', '')
            db.session.commit()
            flash('고객 정보가 성공적으로 수정되었습니다!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'오류가 발생했습니다: {str(e)}', 'danger')
    return render_template('customer_form.html', customer=customer)

@app.route('/customer/delete/<int:id>', methods=['POST'])
def delete_customer(id):
    try:
        customer = Customer.query.get_or_404(id)
        db.session.delete(customer)
        db.session.commit()
        flash('고객이 성공적으로 삭제되었습니다!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'오류가 발생했습니다: {str(e)}', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True)
