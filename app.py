from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///home_automation.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Integer, nullable=True)

class DeviceForm(FlaskForm):
    name = StringField('Device Name', validators=[DataRequired(), Length(min=2, max=150)])
    type = SelectField('Device Type', choices=[('light', 'Light'), ('thermostat', 'Thermostat')], validators=[DataRequired()])
    value = IntegerField('Value (e.g., brightness or temperature)', validators=[NumberRange(min=0, max=100)])
    submit = SubmitField('Add Device')

db.create_all()

@app.route('/')
def home():
    devices = Device.query.all()
    return render_template('index.html', devices=devices)

@app.route('/add_device', methods=['GET', 'POST'])
def add_device():
    form = DeviceForm()
    if form.validate_on_submit():
        new_device = Device(
            name=form.name.data,
            type=form.type.data,
            status='off',
            value=form.value.data
        )
        db.session.add(new_device)
        db.session.commit()
        flash('Device added successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('add_device.html', form=form)

@app.route('/toggle_device/<int:id>')
def toggle_device(id):
    device = Device.query.get_or_404(id)
    device.status = 'on' if device.status == 'off' else 'off'
    db.session.commit()
    flash(f'{device.name} turned {"on" if device.status == "on" else "off"}!', 'success')
    return redirect(url_for('home'))

@app.route('/set_value/<int:id>', methods=['POST'])
def set_value(id):
    device = Device.query.get_or_404(id)
    new_value = request.form['value']
    device.value = int(new_value)
    db.session.commit()
    flash(f'{device.name} value set to {new_value}!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
