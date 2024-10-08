from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


class CallInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String, nullable=True)
    phone1 = db.Column(db.String, nullable=True)
    phone2 = db.Column(db.String, nullable=True)
    phone3 = db.Column(db.String, nullable=True)
    phone4 = db.Column(db.String, nullable=True)
    Id_chain = db.Column(db.String, nullable=True)
    Client_id = db.Column(db.String, nullable=True)
    fio = db.Column(db.String, nullable=True)
    all_summ = db.Column(db.Float, nullable=True)
    summ = db.Column(db.Float, nullable=True)
    summ_dolg = db.Column(db.Float, nullable=True)
    summ_perc = db.Column(db.Float, nullable=True)
    summ_mail = db.Column(db.Float, nullable=True)
    summ_perc_plus = db.Column(db.Float, nullable=True)
    day = db.Column(db.Integer, nullable=True)
    product = db.Column(db.String, nullable=True)
    Sud_vixod = db.Column(db.Date, nullable=True)
    Sud_resh = db.Column(db.Date, nullable=True)
    region = db.Column(db.String, nullable=True)
    adress = db.Column(db.String, nullable=True)
    anketa = db.Column(db.String, nullable=True)
    status_of_call = db.Column(db.String, nullable=True)
    Try = db.Column(db.Integer, nullable=True)
    result1 = db.Column(db.String, nullable=True)
    result2 = db.Column(db.String, nullable=True)
    date_of_call = db.Column(db.DateTime, nullable=True)
    comment = db.Column(db.String, nullable=True)
    phone_new = db.Column(db.String, nullable=True)
    Operator = db.Column(db.String, nullable=True)
    date_of = db.Column(db.Date, nullable=True)
    date_of_import = db.Column(db.DateTime, nullable=True)
    time_of_call = db.Column(db.Integer, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('phone', 'phone1', 'phone2', 'phone3', 'phone4', 'Id_chain', 'Client_id', 'fio', 'all_summ',
                            'summ', 'summ_dolg', 'summ_perc', 'summ_mail', 'summ_perc_plus', 'day', 'product',
                            'Sud_vixod', 'Sud_resh', 'region', 'adress', 'anketa', 'status_of_call', 'Try', 'result1',
                            'result2', 'date_of_call', 'comment', 'phone_new', 'Operator', 'date_of',
                            name='unique_call_info'),
    )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
