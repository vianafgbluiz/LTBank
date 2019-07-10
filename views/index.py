import string
from random import randint

from datetime import datetime, date
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

# Inicializando
index_blueprint = Blueprint('index', __name__)

from .nav import nav, ExtendedNavbar

nav.register_element('index_top', ExtendedNavbar(
    title='LTBank',
    root_class='navbar navbar-inverse',
    items=(
        View('Home', '.index'),
        View('Login', '.login'),
    )
))

# ------------------------------------ ORM --------------------------------------------
db = create_engine("postgresql+psycopg2://postgres:postgres@database/asa")

metadados = MetaData(schema="banklt_desnv")

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
                    Column('nm_bairro',String(50)),
                    Column('nm_city',String(40)),
                    Column('nm_state',String(2)),
                    Column('user_id', Integer, ForeignKey('lt_users.id')))

accounts = Table('lt_accounts', metadados,
                 Column('id', Integer, primary_key=True),
                 Column('ds_agency', String(4)),
                 Column('ds_digit', String(1)),
                 Column('ds_account', String(5)),
                 Column('ds_card', String(16)),
                 Column('dt_validate', String(5)),
                 Column('ds_security', String(3)),
                 Column('user_id', Integer, ForeignKey('lt_users.id')))

conn = db.connect()
# -------------------------------------------------------------------------------------
# ----------------------------------- FUNCS -------------------------------------------
(MINLEN_CC, MAXLEN_CC) = (7, 19)

def _toIntList(numstr, acceptX=0):
    """
    Converte string passada para lista de inteiros,
    eliminando todos os caracteres inválidos.
    Recebe string com nmero a converter.
    Segundo parÃ¢metro indica se 'X' e 'x' devem ser
    convertidos para '10' ou não.
    """
    res = []

    # converter todos os dígitos
    for i in numstr:
        if i in string.digits:
            res.append(int(i))

    # converter dígito de controlo no ISBN
    if acceptX and (numstr[-1] in 'Xx'):
        res.append(10)
    return res

def controlCreditCard(ncc):
    """
    Verifica a validade de número de cartão de crédito.
    Recebe string com número do cartão de crédito.
    """

    # converter número para lista de inteiros e inverter lista
    ncc = _toIntList(ncc)
    ncc.reverse()

    # verificar tamanho do número
    if MINLEN_CC > len(ncc) or len(ncc) > MAXLEN_CC:
        return False

    # computar soma de controlo
    sum = 0
    alt = False

    for i in ncc:
        if alt:
            i *= 2
            if i > 9:
                i -= 9
        sum += i
        alt = not alt

    # verificar soma de controlo
    return not (sum % 10)

def validate_cpf(cpf):
    if len(cpf) < 11:
        return False

    if cpf in [s * 11 for s in [str(n)
 for n in range(10)]]:
        return False

    calc = lambda t: int(t[1]) * (t[0] + 2)
    d1 = (sum(map(calc, enumerate(reversed(cpf[:-2])))) * 10) % 11
    d2 = (sum(map(calc, enumerate(reversed(cpf[:-1])))) * 10) % 11
    return str(d1) == cpf[-2] and str(d2) == cpf[-1]

def randomNumber(number):
    pot = 10 ** number
    random_num = randint(0, pot)
    random_num = str(random_num).zfill(number)
    return random_num

def generateCreditCardMaster():
    while True:
        number = '5' + randomNumber(15)
        if controlCreditCard(number):
            print(controlCreditCard(number))
            return number

# -------------------------------------------------------------------------------------
# ------------------------------------ AUTH -------------------------------------------
@index_blueprint.route("/")
def index():
    return render_template('index.html')

@index_blueprint.route("/insertuser", methods=['POST'])
def veioaqui():
    num = randomNumber(5)
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
        select_command = select([users]).where(users.c.nm_cpf == request.form['inputCPF'])
        result = conn.execute(select_command)
        print(result)
        for row in result:
            if row['nm_cpf'] == request.form['inputCPF']:
                user = row
                print(user)
                conn.execute(addresses.insert(), [
                    {
                        'nm_local': request.form['inputAddress'],
                        'nm_bairro': request.form['inputBairro'],
                        'nm_city': request.form['inputCity'],
                        'nm_state': request.form['inputState'],
                        'user_id': user['id']
                    }
                ])
                conn.execute(accounts.insert(), [
                    {
                        'ds_agency': 1311,
                        'ds_digit': randomNumber(1),
                        'ds_card': generateCreditCardMaster(),
                        'dt_validate': '02/22',
                        'ds_account': randomNumber(5),
                        'ds_security': randomNumber(3),
                        'user_id': user['id']
                    }
                ])
                return render_template('index.html')
    return render_template('index.html')

# -------------------------------------------------------------------------------------

# ------------------------------------ USER -------------------------------------------
@index_blueprint.route("/user/<id>", methods=["GET"])
def user(id):
    # Comandos DB
    select_command = select([users]).where(users.c.id == id)
    result = conn.execute(select_command)

    for row in result:
        user = row
        return render_template("authenticated.html", user=user)

    return render_template("error.html")

@index_blueprint.route("/user/<id>/show", methods=['GET'])
def show(id):
    # Comandos DB
    first_command = select([users]).where(users.c.id == id)
    second_command = select([accounts]).where(accounts.c.user_id == id)
    third_command = select([addresses]).where(addresses.c.user_id == id)

    user_result = conn.execute(first_command)
    account_result = conn.execute(second_command)
    address_result = conn.execute(third_command)

    for row in user_result:
        user = row
        for row_a in account_result:
            account = row_a
            for row_ad in address_result:
                address = row_ad
                print(address)
                return render_template("show.html", user=user, account=account, address=address)

    return render_template("error.html")

@index_blueprint.route("/user/<id>/sales", methods=['GET'])
def sales(id):
    query = "SELECT id, vn_total, vn_dividers, DATE(dt_sale) as dt_sale, account_id FROM banklt_desnv.lt_sales WHERE account_id = " + str(id)

    result = conn.execute(query)
    result = result.fetchall()

    sales = []

    for row in result:
        d = dict(row.items())
        d['dt_sale'] = str(datetime.strptime(str(row['dt_sale']), '%Y-%m-%d'))

        data = datetime.now()

        x = datetime.strptime(str(row['dt_sale']), '%Y-%m-%d')
        print(x.strftime('%d/%m/%Y'))

        if d['vn_dividers'] == 1:
            valor_parcela = d['vn_total']
        else:
            valor_parcela = round(d['vn_total']/d['vn_dividers'], 2)

        if data.day > 5:
            print("Maior que 5")

        sales.append({'id' : d['id'],
                          'vn_total' : str(d['vn_total']),
                          'vn_dividers' : d['vn_dividers'],
                          'dt_sale': x.strftime('%d/%m/%Y'),
                          'vn_parcela' : str(valor_parcela)
                          })

    tamanho = len(sales)

    return render_template("fatura.html", sales=sales, tamanho=tamanho)

@index_blueprint.route("/user/<id>/filtersale")
def filtersale(id):
    # query = "SELECT id, vn_total, vn_dividers, DATE(dt_sale) as dt_sale, account_id FROM banklt_desnv.lt_sales WHERE account_id = " + str(id) + " AND " +



    tamanho = len(sales)
    return render_template("fatura.html", sales=sales, tamanho=tamanho)

# -------------------------------------------------------------------------------------


@index_blueprint.route("/user/<id>/showinsert", methods=['GET'])
def showinsert(id):
    return render_template("financas.html")

@index_blueprint.route("/user/<id>/insertsale", methods=['POST'])
def insertsale(id):
    try:
        if request.form:
            print(request.form['inputValor'])
            print(request.form['inputParcelas'])

            inputValor = request.form['inputValor']
            inputParcelas = request.form['inputParcelas']

            query = "INSERT INTO banklt_desnv.lt_sales(vn_total, vn_dividers, account_id) VALUES (" + inputValor + " , " + inputParcelas + " , " + id + ")"

            # print("INSERT INTO banklt_desnv.lt_sales(vn_total, vn_dividers, account_id) VALUES (%s, %s, %s)", inputValor, inputParcelas, id)

            conn.execute(query)

        return redirect(url_for('index.user', id=id))
    except:
        print("Problemas ao Inserir!")
        return render_template("error.html")


@index_blueprint.route("/login", methods=['GET'])
def login():
    return render_template('login.html')

@index_blueprint.route("/loginuser", methods=['POST'])
def loginuser():
    if request.form:
        # Variaveis
        senha = hashlib.md5(bytes(request.form['inputSenha'], "ascii"))

        # Comandos DB
        select_command = select([users]).where(users.c.nm_cpf == request.form['inputCPF'])
        result = conn.execute(select_command)

        for row in result:
            if row['nm_password'] == senha.hexdigest():
                return redirect(url_for('index.user', id=str(row['id'])))

    return render_template("error.html")
