import io
import json
import logging
import os
from datetime import datetime, timezone
from functools import wraps
import pandas as pd
import pytz
from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from models import db, CallInfo, User

app = Flask(__name__, instance_relative_config=True)
app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads')

if not os.path.exists(app.instance_path):
    os.makedirs(app.instance_path)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'calls.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

with app.app_context():
    db.create_all()

logging.basicConfig(level=logging.DEBUG)


def adjust_to_gmt_plus_5(dt):
    gmt_plus_5 = pytz.timezone('Asia/Yekaterinburg')
    if dt is not None and (dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None):
        dt = pytz.utc.localize(dt).astimezone(gmt_plus_5)
    return dt


def get_current_time_utc():
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    return now


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
@login_required
@admin_required
def index():
    return render_template('index.html')


@app.route('/notes/<client_id>', methods=['GET'])
def get_notes(client_id):
    logging.debug(f'Getting notes for client ID: {client_id}')
    try:
        call_infos = CallInfo.query.filter_by(Client_id=client_id).order_by(CallInfo.date_of_import.desc()).all()

        for info in call_infos:
            info.date_of_call = adjust_to_gmt_plus_5(info.date_of_call)

        if call_infos:
            logging.debug(f'Call infos retrieved: {call_infos}')
        else:
            logging.debug('No call infos found')

        notes = [call_info.comment for call_info in call_infos]

        return render_template('notes.html', client_id=client_id, notes=notes, call_infos=call_infos)
    except Exception as e:
        logging.error(f'Error getting notes for client ID {client_id}: {e}')
        return jsonify({'message': 'Failed to get notes', 'error': str(e)}), 500


@app.route('/notes/<client_id>', methods=['POST'])
def add_note(client_id):
    try:
        data = request.get_json()
        note = data.get('note', '')
        date_of = data.get('date_of')
        phone_new = data.get('phone_new', '')
        result1 = data.get('result1', '')
        result2 = data.get('result2', '')
        time_of_call = data.get('time_of_call', 0)

        logging.debug(
            f'Adding note for client ID: {client_id} - Note: {note}, Date of: {date_of}, Phone New: {phone_new}, Result1: {result1}, Result2: {result2}, Time of Call: {time_of_call}')

        last_entry = CallInfo.query.filter_by(Client_id=client_id).order_by(CallInfo.id.desc()).first()
        logging.debug(f'Last entry retrieved for client ID {client_id}: {last_entry}')

        if date_of:
            try:
                date_of = datetime.strptime(date_of, '%Y-%m-%d').date()
            except ValueError as e:
                logging.error(f'Invalid date_of format: {date_of} - Error: {e}')
                return jsonify({'message': 'Invalid date_of format. Use YYYY-MM-DD.'}), 400
        else:
            date_of = None

        date_of_call = datetime.utcnow().replace(tzinfo=timezone.utc)

        call_info = CallInfo(
            Client_id=client_id,
            comment=note,
            date_of_call=date_of_call,
            phone_new=phone_new,
            result1=result1 if result1 else (last_entry.result1 if last_entry else None),
            result2=result2 if result2 else (last_entry.result2 if last_entry else None),
            phone1=last_entry.phone1 if last_entry else None,
            phone2=last_entry.phone2 if last_entry else None,
            phone3=last_entry.phone3 if last_entry else None,
            phone4=last_entry.phone4 if last_entry else None,
            Id_chain=last_entry.Id_chain if last_entry else None,
            phone=last_entry.phone if last_entry else None,
            fio=last_entry.fio if last_entry else None,
            all_summ=last_entry.all_summ if last_entry else 0,
            summ=last_entry.summ if last_entry else 0,
            summ_dolg=last_entry.summ_dolg if last_entry else 0,
            summ_perc=last_entry.summ_perc if last_entry else 0,
            summ_mail=last_entry.summ_mail if last_entry else 0,
            summ_perc_plus=last_entry.summ_perc_plus if last_entry else 0,
            day=last_entry.day if last_entry else 0,
            product=last_entry.product if last_entry else None,
            Sud_vixod=last_entry.Sud_vixod if last_entry else None,
            Sud_resh=last_entry.Sud_resh if last_entry else None,
            region=last_entry.region if last_entry else None,
            adress=last_entry.adress if last_entry else None,
            anketa=last_entry.anketa if last_entry else None,
            status_of_call=last_entry.status_of_call if last_entry else None,
            Try=last_entry.Try if last_entry else 0,
            Operator=last_entry.Operator if last_entry else None,
            date_of=date_of,
            date_of_import=datetime.utcnow().replace(tzinfo=timezone.utc),
            time_of_call=time_of_call
        )
        db.session.add(call_info)
        db.session.commit()
        logging.debug('Note added successfully')
        return jsonify({'message': 'Note added successfully'}), 201
    except Exception as e:
        logging.error(f'Error adding note: {e}')
        return jsonify({'message': 'Failed to add note', 'error': str(e)}), 500


@app.route('/add_unload_note', methods=['POST'])
def add_unload_note():
    try:
        data = json.loads(request.data.decode('utf-8'))
        client_id = data.get('client_id')
        note = data.get('note', '')
        date_of = data.get('date_of')
        phone_new = data.get('phone_new', '')
        result1 = data.get('result1', '')
        result2 = data.get('result2', '')
        time_of_call = data.get('time_of_call', 0)

        logging.debug(
            f'Adding unload note for client ID: {client_id} - Note: {note}, Date of: {date_of}, Phone New: {phone_new}, Result1: {result1}, Result2: {result2}, Time of Call: {time_of_call}')

        last_entry = CallInfo.query.filter_by(Client_id=client_id).order_by(CallInfo.id.desc()).first()
        logging.debug(f'Last entry retrieved for client ID {client_id}: {last_entry}')

        if date_of:
            try:
                date_of = datetime.strptime(date_of, '%Y-%m-%d').date()
            except ValueError as e:
                logging.error(f'Invalid date_of format: {date_of} - Error: {e}')
                return jsonify({'message': 'Invalid date_of format. Use YYYY-MM-DD.'}), 400
        else:
            date_of = None

        date_of_call = datetime.utcnow().replace(tzinfo=timezone.utc)

        call_info = CallInfo(
            Client_id=client_id,
            comment=note,
            date_of_call=date_of_call,
            phone_new=phone_new,
            result1=result1 if result1 else (last_entry.result1 if last_entry else None),
            result2=result2 if result2 else (last_entry.result2 if last_entry else None),
            phone1=last_entry.phone1 if last_entry else None,
            phone2=last_entry.phone2 if last_entry else None,
            phone3=last_entry.phone3 if last_entry else None,
            phone4=last_entry.phone4 if last_entry else None,
            Id_chain=last_entry.Id_chain if last_entry else None,
            phone=last_entry.phone if last_entry else None,
            fio=last_entry.fio if last_entry else None,
            all_summ=last_entry.all_summ if last_entry else 0,
            summ=last_entry.summ if last_entry else 0,
            summ_dolg=last_entry.summ_dolg if last_entry else 0,
            summ_perc=last_entry.summ_perc if last_entry else 0,
            summ_mail=last_entry.summ_mail if last_entry else 0,
            summ_perc_plus=last_entry.summ_perc_plus if last_entry else 0,
            day=last_entry.day if last_entry else 0,
            product=last_entry.product if last_entry else None,
            Sud_vixod=last_entry.Sud_vixod if last_entry else None,
            Sud_resh=last_entry.Sud_resh if last_entry else None,
            region=last_entry.region if last_entry else None,
            adress=last_entry.adress if last_entry else None,
            anketa=last_entry.anketa if last_entry else None,
            status_of_call=last_entry.status_of_call if last_entry else None,
            Try=last_entry.Try if last_entry else 0,
            Operator=last_entry.Operator if last_entry else None,
            date_of=date_of,
            date_of_import=datetime.utcnow().replace(tzinfo=timezone.utc),
            time_of_call=time_of_call
        )
        db.session.add(call_info)
        db.session.commit()
        logging.debug('Unload note added successfully')
        return jsonify({'message': 'Unload note added successfully'}), 201
    except Exception as e:
        logging.error(f'Error adding unload note: {e}')
        return jsonify({'message': 'Failed to add unload note', 'error': str(e)}), 500


@app.route('/clear', methods=['POST'])
@login_required
@admin_required
def clear_db():
    try:
        num_deleted = db.session.query(CallInfo).delete()
        db.session.commit()
        logging.debug(f'Cleared {num_deleted} records from the database.')
        return jsonify({'message': 'Database cleared successfully', 'num_deleted': num_deleted}), 200
    except Exception as e:
        logging.error(f'Error clearing database: {e}')
        return jsonify({'message': 'Failed to clear database', 'error': str(e)}), 500


@app.route('/clear_form')
@login_required
@admin_required
def clear_form():
    return render_template('clear.html')


@app.route('/import_form')
@login_required
@admin_required
def import_form():
    return render_template('import.html')


@app.route('/import', methods=['POST'])
@login_required
@admin_required
def import_data():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file and file.filename.endswith('.xlsx'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        df = pd.read_excel(file_path, parse_dates=['date_of_call', 'date_of'])
        df = df.where(pd.notnull(df), None)

        new_records = []
        for _, row in df.iterrows():
            if row['phone'] is None:
                continue

            row_dict = {col: (None if pd.isna(val) else val) for col, val in row.items()}
            logging.debug(f'Processing row: {row_dict}')

            duplicate_exists = CallInfo.query.filter(
                CallInfo.phone == row_dict['phone'],
                CallInfo.phone1 == row_dict.get('phone1'),
                CallInfo.phone2 == row_dict.get('phone2'),
                CallInfo.phone3 == row_dict.get('phone3'),
                CallInfo.phone4 == row_dict.get('phone4'),
                CallInfo.Id_chain == row_dict.get('Id_chain'),
                CallInfo.Client_id == row_dict.get('Client_id'),
                CallInfo.fio == row_dict.get('fio'),
                CallInfo.all_summ == row_dict.get('all_summ'),
                CallInfo.summ == row_dict.get('summ'),
                CallInfo.summ_dolg == row_dict.get('summ_dolg'),
                CallInfo.summ_perc == row_dict.get('summ_perc'),
                CallInfo.summ_mail == row_dict.get('summ_mail'),
                CallInfo.summ_perc_plus == row_dict.get('summ_perc_plus'),
                CallInfo.day == row_dict.get('day'),
                CallInfo.product == row_dict.get('product'),
                CallInfo.Sud_vixod == row_dict.get('Sud_vixod'),
                CallInfo.Sud_resh == row_dict.get('Sud_resh'),
                CallInfo.region == row_dict.get('region'),
                CallInfo.adress == row_dict.get('adress'),
                CallInfo.anketa == row_dict.get('anketa'),
                CallInfo.status_of_call == row_dict.get('status_of_call'),
                CallInfo.Try == row_dict.get('Try'),
                CallInfo.result1 == row_dict.get('result1'),
                CallInfo.result2 == row_dict.get('result2'),
                CallInfo.date_of_call == row_dict.get('date_of_call'),
                CallInfo.comment == row_dict.get('comment'),
                CallInfo.phone_new == row_dict.get('phone_new'),
                CallInfo.Operator == row_dict.get('Operator'),
                CallInfo.date_of == row_dict.get('date_of')
            ).first()

            if duplicate_exists:
                logging.debug(f'Skipping duplicate record: {row_dict}')
                continue

            logging.debug(f'No duplicate found, adding new record: {row_dict}')
            new_call_info = CallInfo(
                phone=row_dict['phone'],
                phone1=row_dict.get('phone1', None),
                phone2=row_dict.get('phone2', None),
                phone3=row_dict.get('phone3', None),
                phone4=row_dict.get('phone4', None),
                Id_chain=row_dict.get('Id_chain', None),
                Client_id=row_dict.get('Client_id', None),
                fio=row_dict.get('fio', None),
                all_summ=row_dict.get('all_summ', None),
                summ=row_dict.get('summ', None),
                summ_dolg=row_dict.get('summ_dolg', None),
                summ_perc=row_dict.get('summ_perc', None),
                summ_mail=row_dict.get('summ_mail', None),
                summ_perc_plus=row_dict.get('summ_perc_plus', None),
                day=row_dict.get('day', None),
                product=row_dict.get('product', None),
                Sud_vixod=row_dict.get('Sud_vixod', None),
                Sud_resh=row_dict.get('Sud_resh', None),
                region=row_dict.get('region', None),
                adress=row_dict.get('adress', None),
                anketa=row_dict.get('anketa', None),
                status_of_call=row_dict.get('status_of_call', None),
                Try=row_dict.get('Try', None),
                result1=row_dict.get('result1', None),
                result2=row_dict.get('result2', None),
                date_of_call=adjust_to_gmt_plus_5(row_dict.get('date_of_call')),
                comment=row_dict.get('comment', None),
                phone_new=row_dict.get('phone_new', None),
                Operator=row_dict.get('Operator', None),
                date_of=row_dict.get('date_of', None),
                date_of_import=get_current_time_utc()
            )
            new_records.append(new_call_info)

        try:
            if new_records:
                db.session.bulk_save_objects(new_records)
                db.session.commit()
                logging.debug(f'Added {len(new_records)} new records')
            return jsonify({'message': f'Data imported successfully, {len(new_records)} records added'}), 201
        except Exception as e:
            db.session.rollback()
            logging.error(f'Failed to import data: {str(e)}')
            return jsonify({'message': 'Failed to import data', 'error': str(e)}), 500

    return jsonify({'message': 'Invalid file type'}), 400


@app.route('/export_form')
@login_required
@admin_required
def export_form():
    return render_template('export.html')


@app.route('/export', methods=['POST'])
@login_required
@admin_required
def export_data():
    filename = request.form.get('filename', 'call_info') + '.xlsx'
    try:
        today = datetime.utcnow().date()

        query = CallInfo.query.filter(or_(CallInfo.date_of == None, CallInfo.date_of <= today)).order_by(
            CallInfo.summ.desc()).all()
        data = []
        for row in query:
            data.append({
                'Client_id': row.Client_id,
                'Phone': row.phone,
                'Result 1': row.result1,
                'Result 2': row.result2,
                'Date of Call': row.date_of_call.strftime('%Y-%m-%d %H:%M:%S') if row.date_of_call else None,
                'Comment': row.comment,
                'Phone New': row.phone_new,
                'Date of': row.date_of.strftime('%Y-%m-%d') if row.date_of else None,
                'Summ': row.summ
            })

        df = pd.DataFrame(data)

        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')

        df.to_excel(writer, index=False, sheet_name='CallInfo')
        writer.close()
        output.seek(0)

        return send_file(output, as_attachment=True, download_name=filename,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        logging.error(f'Error exporting data: {e}')
        return jsonify({'message': 'Failed to export data', 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
