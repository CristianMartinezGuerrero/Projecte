from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, SelectField, SubmitField, DateTimeLocalField, FileField
from wtforms.validators import DataRequired, NumberRange, InputRequired
from datetime import datetime

class ItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    photo = FileField('Photo', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    category_id = SelectField('Category', validators=[InputRequired()])
    seller_id = SelectField('Seller', validators=[InputRequired()], default=10)
    created = DateTimeLocalField('Created', format='%Y-%m-%dT%H:%M', validators=[DataRequired()], default=datetime.now().strftime('%Y-%m-%dT%H:%M'))
    updated = DateTimeLocalField('Updated', format='%Y-%m-%dT%H:%M', validators=[DataRequired()], default=datetime.now().strftime('%Y-%m-%dT%H:%M'))
    submit = SubmitField('Submit')

# Formulari generic per esborrar i aprofitar la CSRF Protection
class DeleteForm(FlaskForm):
    submit = SubmitField()