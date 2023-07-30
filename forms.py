from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,FileField
from wtforms.validators import DataRequired,EqualTo
from wtforms.widgets import TextArea


class UserForm(FlaskForm):
    name=StringField('Name',validators=[DataRequired()])
    username=StringField("Username",validators=[DataRequired()])
    email=StringField("Email",validators=[DataRequired()])
    password_hash=PasswordField('Password',validators=[DataRequired(),EqualTo('password_hash2',message='Passwords must match')])
    password_hash2=PasswordField('Confirm Password',validators=[DataRequired()])
    submit=SubmitField('Submit')

class PostForm(FlaskForm):
    title=StringField('Title',validators=[DataRequired()])
    content=StringField("Content",validators=[DataRequired()],widget=TextArea())
    submit=SubmitField('Submit')
    
class LoginForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Submit')
    