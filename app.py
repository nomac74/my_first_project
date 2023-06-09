import os
from datetime import datetime
from flask import Flask, render_template, request, send_from_directory
from submit_contract import create_contract
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# 수정: 결과 파일을 상대 경로에 저장하도록 변경하였습니다.
save_folder = os.path.join(app.root_path, 'contract')

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

    # 계약서 생성
    contract_text = create_contract(data)
    year = datetime.now().year

    file_name = f'{year}_{employee_name}_근로계약서.pdf'
    file_path = os.path.join(save_folder, file_name)

    # PDF 생성
    doc = SimpleDocTemplate(file_path, pagesize=letter)  # reportlab's high level interface for PDF creation

    # 한글 폰트 설정
    # 수정: 폰트 경로를 직접 지정합니다.
    font_folder = os.path.join(app.root_path, 'fonts')
    font_path = os.path.join(font_folder, 'AppleSDGothicNeoR.ttf')
    pdfmetrics.registerFont(TTFont('AppleSDGothicNeoR', font_path))

    Story = []
    styles = getSampleStyleSheet()

    # 한글 폰트 지정
    styles['Normal'].fontName = 'AppleSDGothicNeoR'

    for line in contract_text.split("\n"):
        para = Paragraph(line, styles['Normal'])  # encoding option removed
        Story.append(para)
        Story.append(Spacer(1, 12))  # Add a little space between lines

    doc.build(Story)  # Create the PDF

    # 수정: PDF 파일 자체를 반환하도록 변경하였습니다.
    return send_from_directory(save_folder, file_name, as_attachment=True)

if __name__ == '__main__':
    app.run(port=8000)
