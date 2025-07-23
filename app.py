from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime, date
import calendar
import json
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__, static_folder='static', static_url_path='/static')
# PostgreSQL 연결 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_MXdTpbtFY91K@ep-summer-pond-afcn2u1o-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False)
    time = db.Column(db.String)
    center = db.Column(db.String, default='구래')
    people_count = db.Column(db.Integer, default=1)
    amount = db.Column(db.Integer, default=15000)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class CenterPricing(db.Model):
    __tablename__ = 'center_pricing'
    id = db.Column(db.Integer, primary_key=True)
    center_name = db.Column(db.String, unique=True, nullable=False)
    base_people = db.Column(db.Integer, default=2)
    above_amount = db.Column(db.Integer, default=30000)
    below_amount = db.Column(db.Integer, default=15000)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# 센터별 기준인원에 따른 금액 계산 함수
def calculate_amount(center, people_count):
    center_obj = CenterPricing.query.filter_by(center_name=center).first()
    if center_obj:
        base_people = center_obj.base_people
        above_amount = center_obj.above_amount
        below_amount = center_obj.below_amount
        return above_amount if people_count >= base_people else below_amount
    return 15000  # 기본값

# 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    # 일정 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT,
            center TEXT DEFAULT '구래',
            people_count INTEGER DEFAULT 1,
            amount INTEGER DEFAULT 15000,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 센터별 기준인원 금액 설정 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS center_pricing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            center_name TEXT UNIQUE NOT NULL,
            base_people INTEGER DEFAULT 2,
            above_amount INTEGER DEFAULT 30000,
            below_amount INTEGER DEFAULT 15000,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 기본 센터별 금액 설정 추가
    cursor.execute('INSERT OR IGNORE INTO center_pricing (center_name, base_people, above_amount, below_amount) VALUES (?, ?, ?, ?)', ('구래', 2, 30000, 15000))
    cursor.execute('INSERT OR IGNORE INTO center_pricing (center_name, base_people, above_amount, below_amount) VALUES (?, ?, ?, ?)', ('사우', 2, 30000, 15000))
    cursor.execute('INSERT OR IGNORE INTO center_pricing (center_name, base_people, above_amount, below_amount) VALUES (?, ?, ?, ?)', ('마곡', 2, 30000, 15000))
    
    conn.commit()
    conn.close()

# 메인 페이지 (달력으로 리다이렉트)
@app.route('/')
def index():
    return redirect(url_for('calendar_view'))

# 달력 페이지
@app.route('/calendar')
def calendar_view():
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)

    # 해당 월의 일정 가져오기 (ORM)
    schedules = {}
    schedule_objs = Schedule.query.filter(
        Schedule.date.like(f'{year:04d}-{month:02d}-%')
    ).order_by(Schedule.date, Schedule.time, Schedule.center).all()
    for row in schedule_objs:
        day = int(row.date.split('-')[2])
        if day not in schedules:
            schedules[day] = []
        schedules[day].append({
            'time': row.time,
            'center': row.center,
            'people_count': row.people_count,
            'amount': row.amount
        })

    # 센터 목록 가져오기 (ORM)
    centers = [c.center_name for c in CenterPricing.query.order_by(CenterPricing.center_name).all()]
    if not centers:
        # 기본 센터 추가
        for name in ['구래', '사우', '마곡']:
            db.session.add(CenterPricing(center_name=name))
        db.session.commit()
        centers = [c.center_name for c in CenterPricing.query.order_by(CenterPricing.center_name).all()]

    # 달력의 첫 요일을 일요일로 설정
    calendar.setfirstweekday(calendar.SUNDAY)
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    return render_template('calendar.html', 
                         calendar=cal, 
                         year=year, 
                         month=month, 
                         month_name=month_name,
                         schedules=schedules,
                         centers=centers)

# 정산관리 페이지
@app.route('/settlement')
def settlement_view():
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)

    center_pricing = CenterPricing.query.order_by(CenterPricing.center_name).all()
    # 월별 합산
    monthly_summary = db.session.query(
        Schedule.center,
        db.func.sum(Schedule.amount),
        db.func.count()
    ).filter(Schedule.date.like(f'{year:04d}-{month:02d}-%')).group_by(Schedule.center).all()
    total_amount = sum(row[1] for row in monthly_summary) if monthly_summary else 0

    return render_template('settlement.html',
                         year=year,
                         month=month,
                         center_pricing=center_pricing,
                         monthly_summary=monthly_summary,
                         total_amount=total_amount)

# 일정 추가 API (여러 날짜)
@app.route('/api/schedule/bulk', methods=['POST'])
def add_schedule_bulk():
    data = request.json
    dates = data.get('dates', [])
    time = data.get('time', '')
    center = data.get('center', '구래')
    people_count = data.get('people_count', 1)
    try:
        for date_str in dates:
            amount = calculate_amount(center, people_count)
            new_schedule = Schedule(date=date_str, time=time, center=center, people_count=people_count, amount=amount)
            db.session.add(new_schedule)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# 일정 수정 API
@app.route('/api/schedule/update/<int:schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    data = request.json
    try:
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return jsonify({'success': False, 'error': '일정이 존재하지 않습니다.'}), 404
        schedule.date = data['date']
        schedule.time = data.get('time', '')
        schedule.center = data.get('center', '구래')
        schedule.people_count = data.get('people_count', 1)
        schedule.amount = calculate_amount(schedule.center, schedule.people_count)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# 일정 삭제 API
@app.route('/api/schedule/delete/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    try:
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return jsonify({'success': False, 'error': '일정이 존재하지 않습니다.'}), 404
        db.session.delete(schedule)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# 특정 날짜의 일정 가져오기 API
@app.route('/api/schedule/date/<date>')
def get_schedules_by_date(date):
    schedules = Schedule.query.filter_by(date=date).order_by(Schedule.time).all()
    result = []
    for row in schedules:
        result.append({
            'id': row.id,
            'date': row.date,
            'time': row.time,
            'center': row.center,
            'people_count': row.people_count,
            'amount': row.amount
        })
    return jsonify(result)

# 특정 일정 ID로 일정 가져오기 API
@app.route('/api/schedule/detail/<int:schedule_id>')
def get_schedule_by_id(schedule_id):
    row = Schedule.query.get(schedule_id)
    if row:
        schedule_data = {
            'id': row.id,
            'date': row.date,
            'time': row.time,
            'center': row.center,
            'people_count': row.people_count,
            'amount': row.amount
        }
        return jsonify(schedule_data)
    else:
        return jsonify({'error': '일정을 찾을 수 없습니다'}), 404

# 센터별 기준인원 금액 설정 API
@app.route('/api/center-pricing', methods=['POST'])
def update_center_pricing():
    data = request.json
    try:
        center = CenterPricing.query.filter_by(center_name=data['center_name']).first()
        if not center:
            center = CenterPricing(center_name=data['center_name'])
            db.session.add(center)
        center.base_people = data['base_people']
        center.above_amount = data['above_amount']
        center.below_amount = data['below_amount']
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# 금액 계산 API
@app.route('/api/calculate-amount', methods=['POST'])
def calculate_amount_api():
    data = request.json
    center = data.get('center', '구래')
    people_count = data.get('people_count', 1)
    
    amount = calculate_amount(center, people_count)
    
    return jsonify({'success': True, 'amount': amount})

@app.route('/test-db')
def test_db():
    try:
        result = db.session.execute(text('SELECT * FROM schedules LIMIT 5')).fetchall()
        return '<br>'.join(str(row) for row in result) or 'No data found.'
    except Exception as e:
        return f'Error: {e}'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    init_db()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port) 