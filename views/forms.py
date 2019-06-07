from flask_wtf import FlaskForm
from wtforms.fields import *
from wtforms.validators import Required

class Device(FlaskForm):
    device_description = TextField(u'Your name')
    submit = SubmitField(u'Signup')

class Alunos(FlaskForm):
    nome = TextField(u'Preencha o seu nome')
    idade = IntegerField(u'Preencha a sua Idade')
    endereco = TextField(u'Preencha o seu Endereço')
    submit = SubmitField(u'Enviar')