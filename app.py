from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime, date
import calendar
import json
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')

# 센터별 기준인원에 따른 금액 계산 함수
def calculate_amount(center, people_count):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    # 해당 센터의 기준인원 금액 설정 가져오기
    cursor.execute('''
        SELECT base_people, above_amount, below_amount 
        FROM center_pricing 
        WHERE center_name = ?
    ''', (center,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        base_people, above_amount, below_amount = result
        # 기준인원 이상이면 above_amount, 미만이면 below_amount 반환
        return above_amount if people_count >= base_people else below_amount
    
    # 기본값 반환
    return 15000

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
    
    # 해당 월의 일정 가져오기
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT date, time, center, people_count, amount 
        FROM schedules 
        WHERE strftime('%Y-%m', date) = ?
        ORDER BY date, time, center
    ''', (f'{year:04d}-{month:02d}',))
    
    schedules = {}
    for row in cursor.fetchall():
        day = int(row[0].split('-')[2])  # 문자열이 아닌 int로 변환
        if day not in schedules:
            schedules[day] = []
        schedules[day].append({
            'time': row[1],
            'center': row[2],
            'people_count': row[3],
            'amount': row[4]
        })
    
    # 센터 목록 가져오기
    cursor.execute('SELECT center_name FROM center_pricing ORDER BY center_name')
    centers = [row[0] for row in cursor.fetchall()]
    
    # 센터가 없으면 기본 센터들 추가
    if not centers:
        print("센터 목록이 비어있어 기본 센터들을 추가합니다.")
        cursor.execute('INSERT OR IGNORE INTO center_pricing (center_name, base_people, above_amount, below_amount) VALUES (?, ?, ?, ?)', ('구래', 2, 30000, 15000))
        cursor.execute('INSERT OR IGNORE INTO center_pricing (center_name, base_people, above_amount, below_amount) VALUES (?, ?, ?, ?)', ('사우', 2, 30000, 15000))
        cursor.execute('INSERT OR IGNORE INTO center_pricing (center_name, base_people, above_amount, below_amount) VALUES (?, ?, ?, ?)', ('마곡', 2, 30000, 15000))
        conn.commit()
        
        # 다시 센터 목록 가져오기
        cursor.execute('SELECT center_name FROM center_pricing ORDER BY center_name')
        centers = [row[0] for row in cursor.fetchall()]
    
    print(f"사용 가능한 센터 목록: {centers}")  # 디버깅용
    
    conn.close()
    
    # 달력 생성
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
    
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    # 센터별 기준인원 금액 설정 가져오기
    cursor.execute('''
        SELECT center_name, base_people, above_amount, below_amount 
        FROM center_pricing 
        ORDER BY center_name
    ''')
    center_pricing = cursor.fetchall()
    
    # 해당 월의 일정별 합산
    cursor.execute('''
        SELECT center, SUM(amount) as total_amount, COUNT(*) as count
        FROM schedules 
        WHERE strftime('%Y-%m', date) = ?
        GROUP BY center
    ''', (f'{year:04d}-{month:02d}',))
    
    monthly_summary = cursor.fetchall()
    print(f"월별 요약 데이터: {monthly_summary}")  # 디버깅용
    
    # 총합 계산
    try:
        total_amount = sum(row[1] for row in monthly_summary) if monthly_summary else 0
        print(f"계산된 총합: {total_amount}")  # 디버깅용
    except Exception as e:
        print(f"총합 계산 에러: {e}")  # 디버깅용
        total_amount = 0
    
    conn.close()
    
    return render_template('settlement.html',
                         year=year,
                         month=month,
                         center_pricing=center_pricing,
                         monthly_summary=monthly_summary,
                         total_amount=total_amount)

# 일정 추가 API
@app.route('/api/schedule', methods=['POST'])
def add_schedule():
    data = request.json
    print(f"받은 데이터: {data}")  # 디버깅용
    
    try:
        conn = sqlite3.connect('schedule.db')
        cursor = conn.cursor()
        
        people_count = data.get('people_count', 1)
        center = data.get('center', '구래')
        amount = calculate_amount(center, people_count)
        
        print(f"센터: {center}, 인원: {people_count}, 금액: {amount}")  # 디버깅용
        
        cursor.execute('''
            INSERT INTO schedules (date, time, center, people_count, amount)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['date'], data.get('time', ''), data.get('center', '구래'), 
              people_count, amount))
        
        conn.commit()
        conn.close()
        
        print("일정 저장 성공")  # 디버깅용
        return jsonify({'success': True})
    except Exception as e:
        print(f"에러 발생: {e}")  # 디버깅용
        return jsonify({'success': False, 'error': str(e)}), 500

# 일정 수정 API
@app.route('/api/schedule/update/<int:schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    data = request.json
    print(f"수정 데이터: {data}")  # 디버깅용
    
    try:
        conn = sqlite3.connect('schedule.db')
        cursor = conn.cursor()
        
        people_count = data.get('people_count', 1)
        center = data.get('center', '구래')
        amount = calculate_amount(center, people_count)
        
        cursor.execute('''
            UPDATE schedules 
            SET date=?, time=?, center=?, people_count=?, amount=?
            WHERE id=?
        ''', (data['date'], data.get('time', ''), data.get('center', '구래'), 
              people_count, amount, schedule_id))
        
        conn.commit()
        conn.close()
        
        print("일정 수정 성공")  # 디버깅용
        return jsonify({'success': True})
    except Exception as e:
        print(f"수정 에러: {e}")  # 디버깅용
        return jsonify({'success': False, 'error': str(e)}), 500

# 일정 삭제 API
@app.route('/api/schedule/delete/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM schedules WHERE id=?', (schedule_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# 특정 날짜의 일정 가져오기 API
@app.route('/api/schedule/date/<date>')
def get_schedules_by_date(date):
    print(f"요청된 날짜: {date}")  # 디버깅용
    
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, date, time, center, people_count, amount
        FROM schedules 
        WHERE date = ?
        ORDER BY time
    ''', (date,))
    
    schedules = []
    for row in cursor.fetchall():
        schedule_data = {
            'id': row[0],
            'date': row[1],
            'time': row[2],
            'center': row[3],
            'people_count': row[4],
            'amount': row[5]
        }
        schedules.append(schedule_data)
        print(f"일정 데이터: {schedule_data}")  # 디버깅용
    
    conn.close()
    
    print(f"반환할 일정들: {schedules}")  # 디버깅용
    return jsonify(schedules)

# 특정 일정 ID로 일정 가져오기 API
@app.route('/api/schedule/detail/<int:schedule_id>')
def get_schedule_by_id(schedule_id):
    print(f"요청된 일정 ID: {schedule_id}")  # 디버깅용
    
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, date, time, center, people_count, amount
        FROM schedules 
        WHERE id = ?
    ''', (schedule_id,))
    
    row = cursor.fetchone()
    if row:
        schedule_data = {
            'id': row[0],
            'date': row[1],
            'time': row[2],
            'center': row[3],
            'people_count': row[4],
            'amount': row[5]
        }
        print(f"찾은 일정: {schedule_data}")  # 디버깅용
        conn.close()
        return jsonify(schedule_data)
    else:
        print(f"일정 ID {schedule_id}를 찾을 수 없습니다")  # 디버깅용
        conn.close()
        return jsonify({'error': '일정을 찾을 수 없습니다'}), 404

# 센터별 기준인원 금액 설정 API
@app.route('/api/center-pricing', methods=['POST'])
def update_center_pricing():
    data = request.json
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO center_pricing (center_name, base_people, above_amount, below_amount)
        VALUES (?, ?, ?, ?)
    ''', (data['center_name'], data['base_people'], data['above_amount'], data['below_amount']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# 금액 계산 API
@app.route('/api/calculate-amount', methods=['POST'])
def calculate_amount_api():
    data = request.json
    center = data.get('center', '구래')
    people_count = data.get('people_count', 1)
    
    amount = calculate_amount(center, people_count)
    
    return jsonify({'success': True, 'amount': amount})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port) 