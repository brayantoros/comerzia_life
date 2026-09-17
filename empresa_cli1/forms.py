from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired

class LoginForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[InputRequired()])
    password = PasswordField('Contraseña', validators=[InputRequired()])
    submit = SubmitField('Iniciar sesión')

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length

class LoginForm(FlaskForm):
    nombre_usuario = StringField('Nombre de usuario', validators=[InputRequired(), Length(min=4, max=150)])
    clave = PasswordField('Contraseña', validators=[InputRequired(), Length(min=6)])
