import os
from datetime import datetime
from flask import Flask, render_template, request
from reportlab.pdfgen import canvas
from submit_contract import create_contract
from flask import send_file
import tempfile

def download_file(url):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename

app = Flask(__name__)

save_folder = os.path.join(os.getcwd(), 'results')  # 상대 경로로 저장 폴더 설정

@app.route('/')
def contract_form():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_contract():
    # 폼 데이터 가져오기
    employer_name = request.form.get('employer_name')
    employee_name = request.form.get('employee_name')
    job_title = request.form.get('job_title')
    hourly_wage = request.form.get('hourly_wage')
    start_hour = request.form.get('start_hour')
    end_hour = request.form.get('end_hour')
    break_time = request.form.get('break_time')
    weekly_working_days = request.form.get('weekly_working_days')
    contract_start = request.form.get('contract_start')
    contract_end = request.form.get('contract_end')

    # 각 필드가 존재하는지 검증
    fields = [employer_name, employee_name, job_title, hourly_wage, start_hour, end_hour, break_time, weekly_working_days, contract_start, contract_end]
    if not all(fields):
        return '모든 필드를 채워주세요.', 400

    # 각 필드의 유형이 맞는지 확인
    try:
        start_hour = float(start_hour)
        end_hour = float(end_hour)
        hourly_wage = float(hourly_wage)
        break_time = float(break_time)
        weekly_working_days = int(weekly_working_days)
        if '-' not in contract_start:
            raise ValueError("계약 시작일은 '월-일' 형식으로 입력해주세요.")
        if '-' not in contract_end:
            raise ValueError("계약 종료일은 '월-일' 형식으로 입력해주세요.")
        contract_start = tuple(map(int, contract_start.split('-')))
        contract_end = tuple(map(int, contract_end.split('-')))
    except ValueError as e:
        return str(e), 400

    # 데이터 딕셔너리 생성
    data = {
        "employer_name": employer_name,
        "employee_name": employee_name,
        "job_title": job_title,
        "hourly_wage": hourly_wage,
        "start_hour": start_hour,
        "end_hour": end_hour,
        "break_time": break_time,
        "weekly_working_days": weekly_working_days,
        "contract_start": contract_start,
        "contract_end": contract_end
    }

    contract_text = create_contract(data)
    year = datetime.now().year

    # 임시 파일을 생성
    temp = tempfile.NamedTemporaryFile(delete=False)
    file_name = f'{year}_{employee_name}_근로계약서.pdf'
    file_path = os.path.join(save_folder, file_name)

    # PDF 생성
    c = canvas.Canvas(file_path)
    c.drawString(30, 800, contract_text)

    # 한글 폰트 설정
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

     # 한글 폰트 파일 로드
    font_path = download_file('https://github.com/nomac74/my_first_project/raw/gh-pages/NanumSquareNeo-aLt.ttf')  # 한글 폰트 파일의 실제 경로로 수정
    pdfmetrics.registerFont(TTFont('KoreanFont', font_path))

    # PDF 생성 시 폰트 설정
    c.setFont('KoreanFont', 12)  # 폰트 이름으로 설정

    c.drawString(30, 800, contract_text)

    # PDF 저장
    c.save()
    return send_file(temp.name, as_attachment=True, attachment_filename=file_name, mimetype='application/pdf')

if __name__ == '__main__':
    app.run()
