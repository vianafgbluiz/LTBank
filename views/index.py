from flask import Flask, Blueprint, render_template, request
from flask_wtf import FlaskForm
from wtforms.fields import *
from wtforms.validators import Required
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from markupsafe import escape
from .forms import Device, Alunos

#Import de Criptografia
import hashlib

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy import text, select, ForeignKey

index_blueprint = Blueprint('index', __name__)

from .nav import nav, ExtendedNavbar

nav.register_element('index_top', ExtendedNavbar(
    #title=View('Modbus Sniffer1', '.index'),
    title='LTBank',
    root_class='navbar navbar-inverse',
    items=(
        View('Home', '.index'),
        View('Login', '.login'),
        #View('Debug-Info', 'bootstrap.static'),
        Subgroup(
            'Docs1',
            Link('Flask-Bootstrap1', 'http://pythonhosted.org/Flask-Bootstrap'),
            Separator(),
            Text('Bootstrap'),
            Link('Getting started', 'http://getbootstrap.com/getting-started/'),
            Link('CSS', 'http://getbootstrap.com/css/'),
            Link('Components', 'http://getbootstrap.com/components/'),
            Link('Javascript', 'http://getbootstrap.com/javascript/'),
        ),
    )
))

# ------------------------------------ ORM --------------------------------------------
db = create_engine("postgresql+psycopg2://postgres:banco@localhost/ltbank")

metadados = MetaData()

users = Table('lt_users', metadados,
               Column('id',Integer,primary_key=True),
               Column('nm_name',String(60)),
               Column('nm_cpf',String(14)),
               Column('nm_telefone',String(18)),
               Column('nm_email',String(100)),
               Column('nm_password',String(32)),
               Column('fl_active',Integer))

addresses = Table('lt_addresses', metadados,
                    Column('id',Integer,primary_key=True),
                    Column('nm_local',String(100)),
                    Column('nm_city',String(40)),
                    Column('nm_state',String(2)),
                    Column('user_id', Integer, ForeignKey('lt_users.id')))


conn = db.connect()
# -------------------------------------------------------------------------------------


class Device(FlaskForm):
    device_description = TextField(u'Device Description')
    submit = SubmitField(u'Signup')

@index_blueprint.route("/")
def index():
    return render_template('index.html')

@index_blueprint.route("/insertuser", methods=['POST'])
def veioaqui():
    if request.form:
        senha = hashlib.md5(bytes(request.form['inputSenha'], "ascii"))
        conn.execute(users.insert(), [
            {
                'nm_name': request.form['inputName'],
                'nm_cpf': request.form['inputCPF'],
                'nm_telefone': request.form['inputPhone'],
                'nm_email': request.form['inputEmail'],
                'nm_password': senha.hexdigest(),
                'fl_active': 1
            }
        ])


        return render_template('authenticated.html')
    return render_template('index.html')

@index_blueprint.route("/loginuser", methods=['POST'])
def loginuser():
    if request.form:
        senha = hashlib.md5(bytes(request.form['inputSenha'], "ascii"))
        select_command = select([users]).where(users.cpf == request.form['inputCPF'])

@index_blueprint.route("/login", methods=['GET'])
def login():
    return render_template('login.html')


@index_blueprint.route("/teste", methods=['GET', 'POST'])
def teste():
    form = Device(request.form)
    
    if form.validate_on_submit():
        device = form.data.copy()
        print(device['device_description'])
        return render_template('index.html')
    return render_template('device.html', form=form)

@index_blueprint.route("/cad-aluno", methods=['GET', 'POST'])
def cad_aluno():
    form = Alunos(request.form)
    if form.validate_on_submit():
        alunos = form.data.copy()
        print(alunos['nome'])
        return render_template('index.html')
    return render_template('alunos.html', form=form)