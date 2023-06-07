from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import requests
from datetime import datetime
from pdfdocument.document import PDFDocument

def download_file(url):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename

#전역변수
current_year = date.today().year
font_path = download_file('https://github.com/nomac74/my_first_project/raw/gh-pages/NanumSquareNeo-aLt.ttf') 

def calculate_salary(hourly_wage, start_hour, end_hour, weekly_working_days, break_time):
    if end_hour >= start_hour:
        daily_hours = end_hour - start_hour
    else:
        daily_hours = (24 - start_hour) + end_hour

    daily_hours -= break_time

    night_hours = max(0, min(end_hour, 6) - max(start_hour, 22))
    daily_hours += night_hours * 0.5

    weekly_hours = daily_hours * weekly_working_days
    monthly_hours = weekly_hours * 4.345  # 평균적인 한달의 주당 근무시간
   
    # 주휴수당 보너스 계산
    bonus_hours = 0
    if weekly_hours >= 40:
        bonus_hours = 8 * 4.345  # 주당 48시간 근무한 것으로 계산
    elif 15 <= weekly_hours < 40:
        bonus_hours = (weekly_hours / 40) * 8 * 4.345  # 비율에 맞게 주휴수당 보너스 계산
    # weekly_hours가 15보다 작은 경우 bonus_hours는 0으로 그대로 유지됩니다.

    # 평균적인 한달의 실제 근무시간 계산
    monthly_actual_hours = round(monthly_hours)
    bonus_actual_hours = round(bonus_hours)
    total_pay = hourly_wage * (monthly_actual_hours + bonus_actual_hours)

    return monthly_actual_hours, bonus_actual_hours, total_pay
# total_insurance = national_pension + health_insurance + employment_insurance + industrial_accident_insurance
    
def format_salary(salary):
    return "{:,.0f}".format(salary)

pdfmetrics.registerFont(TTFont('NANUMSQUARENEO-ALT', font_path))     
def save_to_pdf(text, file_name="C:/Users/USER/Desktop/contract.pdf"):
    c = canvas.Canvas(file_name, pagesize=letter)
    width, height = letter
    lines = text.split('\n')
    line_height = 12  # You can adjust this value to your needs
    top_margin = 25  # Adjust this value too
    c.setFont('NANUMSQUARENEO-ALT', 10)  # 폰트 설정
    for i, line in enumerate(lines):
        c.drawString(10, height - top_margin - i*line_height, line)
    c.save()

def create_contract(data):
    # Extract data from the form
    employer_name = data["employer_name"]
    employee_name = data["employee_name"]
    job_title = data["job_title"]
    hourly_wage = data["hourly_wage"]
    start_hour = data["start_hour"]
    end_hour = data["end_hour"]
    break_time = data["break_time"]
    weekly_working_days = data["weekly_working_days"]
    contract_start = data["contract_start"]
    contract_end = data["contract_end"]

    current_year = datetime.now().year # 전역변수에서 선언됨.

    return generate_contract(current_year, hourly_wage, start_hour, end_hour, weekly_working_days, break_time, employer_name, employee_name, job_title, contract_start, contract_end)
    

def generate_contract(current_year, hourly_wage, start_hour, end_hour, weekly_working_days, break_time, employer_name, employee_name, job_title, contract_start, contract_end):
    monthly_hours, bonus_hours, total_pay = calculate_salary(hourly_wage, start_hour, end_hour, weekly_working_days, break_time)
    total_pay_formatted = format_salary(total_pay)
    current_year = int(current_year)

    start_date = date(current_year, contract_start[0], contract_start[1])
    end_date = date(current_year + 1 if contract_end[0] < contract_start[0] else current_year, contract_end[0], contract_end[1])
    
    contract_template = f"""
    
                [{current_year} 근로 계약서]
                    
                고용주 {employer_name}(이하 '고용주'이라 함)과 근로자 {employee_name} (이하 '근로자'이라 함)는 
                신의성실의 원칙에 따라 '고용주'의 규정을 준수할 것을 서약하고 다음과 같이 근로계약을 체결한다.
                근로계약에 따른 절차와 처리는 근로기준법 및 회사의 규정에 의한다.

                제1조 【부서/ 업무】'근로자'의 근무부서/  담당업무는 다음과 같다.
                    1. 직 책 및 담당업무 : {job_title}
                    2. 회사운용상 필요한 경우 업무조정 및 변경을 지시할 수 있다.
                    3. 업무조정 및 변경은 최소 1주일에서 최대 1개월 전에 통보함을 원칙으로 한다. 
                        단, 급박한 경우에는 예외로 한다.

                제2조 [급여산정] (2023년 시급 {hourly_wage}원기준)
                    A : 급여내역
                    - 시급: {hourly_wage}원/시간
                    - 일일 근무시간: {round(monthly_hours / 4.345 / weekly_working_days, 1)}시간
                    - 주당 근무시간: {round(monthly_hours / 4.345, 1)}시간
                    - 월 기본 근무시간: {monthly_hours}시간
                    - 월 주휴수당 시간: {bonus_hours}시간
                    B. 휴게시간
                    - 브레이크 타임: {break_time}시간 "휴게시간은 매 4시간 근무후 30분~1시간으로 한다."
                    C. 월 급여(세전)
                    - 월간 총급여: {total_pay_formatted}원

                제3조 【급여 및 퇴직금】 
                    -'근로자'이 1년 이상 계속 근무한 경우로 퇴직금 중간정산을 신청한 경우에 1회에 한해 지급할 수 있으며, 
                      중간정산 이후 퇴직금 산정을 위한 근로연수는 근로기준법에 따른다. 
                    - 4대보험의 근로자분을 회사에서 지급한 경우, 차후 근로자에게 실수로 미지급한 급여의 일부분을 상계할 수 있다.
                      상계후 남은 금액은 보너스로 지급한 것으로 한다. 

                제4조 【연월차휴가, 휴일, 휴가】 
                    - 근로기준법을 따른다. 다만, 회사업무 특성상 합의가 필요한 경우는 사전에 합의한다.
                    - 업무특성상 연차 사용이 힘든 경우나, 불가항력적인 사정이 있는 경우 및 근로자의 요청 있는 경우는 
                        사전 합의 후 발생한 연차를 급여와 함께 1/n으로 합산 지급할 수 있다.
                    
                제5조 【근로계약의 해지】
                    '고용주'은 '근로자'이 다음의 사항에 해당된다고 판단되는 경우 사전통보후 이 계약을 해지할 수 있다.
                    1. 제4조의 의무를 위반했을 때.
                    2. 업무를 태만히 하거나 업무수행능력이 부족한 때.
                    3. 고의 또는 과실로 회사나 동료에게 심각한 피해를 끼치거나 위협, 기강을 문란케 한 경우.
                    4. 신체 / 정신상의 이상 기타 개인적인 사정으로 계약서상의 의무를 충실하게 수행할 수 없게 된 때.
                    5. 기타 객관적이고 명백하게 업무수행을 할 수 없는 경우.
                    6. 범죄등 형사처벌 대상이 되는 경우는 적발 즉시 해고 / 해지 할 수 있다. 

                    '근로자'이 이 계약을 해지하고자 할 경우는'고용주'에게 30일전에 사직서을 제출하여야 한다.

                제6조 【손해배상】
                    '근로자'의 귀책사유로 인해 재직 중 또는 퇴직 후'고용주'에게 금전적 또는 비금전적 손해가 발생한 경우에는 
                    징계절차를 거쳐 해고/권고사직 할 수 있으며, 이와 별도로'근로자'는 그 손해를 배상하여야 한다.    

                제7조 【기타】 
                    본 계약서에 정하지 아니한 사항은 관계 법령에 의하며, 계약조건은 상호 합의하여 변경할 수 있다.
                    이상의 계약을 명확히 하기 위하여 본 계약서 2부를 작성, '고용주'과'근로자'이 각각 날인한 후 각1부씩 보관한다.
                    다만, 전자문서로 계약서의 SNS 통지도 가능하며, 통지된 근로계약서는 1년간 전자 저장매체에 보관한다.
                    
                    입사일 : {start_date.strftime('%Y년 %m월 %d일')}
                    퇴사일 : {end_date.strftime('%Y년 %m월 %d일')}


                    고용주 : {employer_name}                                                                                   (인/서명)
                    근로자 : {employee_name}                                                                                   (인/서명)
                    """
    return contract_template

# # 윈도우 시스템 폰트 폴더를 참조하도록 경로를 수정
import re
def validate_name(name):  # sourcery skip: assign-if-exp, boolean-if-exp-identity
    if re.match("^[가-힣a-zA-Z\s]*$", name):
        return True
    else:
        return False

def main():  # sourcery skip: low-code-quality
    hourly_wage = None
    start_hour = None
    end_hour = None
    weekly_working_days = None
    break_time = None

    employer_name = input("고용주의 이름을 입력하세요: ")
    while not validate_name(employer_name):
        print("Invalid input. Please enter only Korean or English alphabets.")
        employer_name = input("고용주의 이름을 입력하세요: ")

    employee_name = input("근로자의 이름을 입력하세요: ")
    while not validate_name(employee_name):
        print("Invalid input. Please enter only Korean or English alphabets.")
        employee_name = input("근로자의 이름을 입력하세요: ")

    job_title = input("직무명을 입력하세요: ")
    
    contract_start = list(map(int, re.split('-|\.', input("계약 시작일을 입력하세요 (월-일, 월.일 형태로): "))))
    contract_end = list(map(int, re.split('-|\.', input("계약 종료일을 입력하세요 (월-일, 월.일 형태로): "))))
    
    while hourly_wage is None:
        hourly_wage_input = input("시급을 입력하세요: ")
        if hourly_wage_input.strip().replace('.', '', 1).isdigit() and 9620 <= float(hourly_wage_input) <= 20000:
            hourly_wage = float(hourly_wage_input)
        else:
            print("시급을 잘못 입력하였습니다. 다시 입력해주세요.")

    while start_hour is None:
        start_hour_input = input("근무 시작 시각을 입력하세요 (24시간 형식, 실수 가능): ")
        if start_hour_input.strip().replace('.', '', 1).isdigit() and 0 <= float(start_hour_input) <= 24:
            start_hour = float(start_hour_input)
        else:
            print("근무 시작 시각을 잘못 입력하였습니다. 다시 입력해주세요.")

    while end_hour is None:
        end_hour_input = input("근무 종료 시각을 입력하세요 (24시간 형식, 실수 가능): ")
        if end_hour_input.strip().replace('.', '', 1).isdigit() and 0 <= float(end_hour_input) <= 24:
            end_hour = float(end_hour_input)
        else:
            print("근무 종료 시각을 잘못 입력하였습니다. 다시 입력해주세요.")

    while weekly_working_days is None:
        weekly_working_days_input = input("주당 근무일수를 입력하세요: ")
        if weekly_working_days_input.strip().isdigit() and 1 <= int(weekly_working_days_input) <= 6:
            weekly_working_days = int(weekly_working_days_input)
        else:
            print("주당 근무일수를 잘못 입력하였습니다. 다시 입력해주세요.")

    while break_time is None:
        break_time_input = input("브레이크 타임을 입력하세요 (0~4 사이의 시간, 실수 가능): ")
        if break_time_input.strip().replace('.', '', 1).isdigit() and 0 <= float(break_time_input) <= 4:
            break_time = float(break_time_input)
        else:
            print("브레이크 타임을 잘못 입력하였습니다. 다시 입력해주세요.")

    contract = generate_contract(hourly_wage, start_hour, end_hour, weekly_working_days, break_time, employer_name, employee_name, job_title, contract_start, contract_end)
    print(contract)
    return contract, employee_name

if __name__ == "__main__":
    contract, employee_name = main()
    
    file_name = f"{current_year}_근로계약서_{employee_name}.pdf"
    save_to_pdf(contract, file_name)
