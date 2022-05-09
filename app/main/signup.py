from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email


class SignupForm(FlaskForm):
    """Accepts a nickname and a room."""
    username = StringField('UserName', validators=[DataRequired()])
    fname = StringField('FirstName', validators=[DataRequired()])
    lname = StringField('LastName', validators=[DataRequired()])
    email = StringField("EmailAddr", validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Signup')
