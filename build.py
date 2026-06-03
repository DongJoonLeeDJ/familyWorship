import calendar
from datetime import datetime
import json
from pathlib import Path
import shutil
import yaml

# 폴더 설정
DATA_DIR = Path("data")
ARCHIVE_DIR = Path("archive")

# 템플릿 읽기
template = Path("template.html").read_text(encoding="utf-8")

# archive 폴더 생성
ARCHIVE_DIR.mkdir(exist_ok=True)

# YAML 파일
yml_file = sorted(DATA_DIR.glob("*.yml"))[0]

data = yaml.safe_load(yml_file.read_text(encoding="utf-8"))

html = template

# 질문 리스트 생성
questions_html = "\n".join(
    [f"<li>{q}</li>" for q in data.get("questions", [])]
)

data["questions_html"] = questions_html

# 변수 치환
for key, value in data.items():
    placeholder = "{{ " + key + " }}"
    html = html.replace(placeholder, str(value))

# 줄바꿈 처리
#html = html.replace("\n", "<br />")

# 출력 파일명
output_name = str(data['date']) + ".html"

output_path = ARCHIVE_DIR / output_name

# HTML 저장
output_path.write_text(html, encoding="utf-8")

print(f"Generated: {output_path}")

# 최신 파일 찾기
latest_file = sorted(ARCHIVE_DIR.glob("*.html"))[-1]

# latest.html 갱신
shutil.copy(latest_file, "latest.html")

print(f"Updated latest.html -> {latest_file.name}")

# #index.html 생성
# =========================
# 달력용 데이터 생성
# =========================

html_files = sorted(
    ARCHIVE_DIR.glob("*.html")
)

worships = {}

for f in html_files:
    worships[f.stem] = f"./archive/{f.name}"

years = sorted({
    date[:4]
    for date in worships.keys()
})


# 날짜 -> 파일명 매핑
date_map = {}

for f in html_files:
    try:
        d = datetime.strptime(f.stem, "%Y-%m-%d")
        date_map[d.date()] = f.name
    except:
        pass

# 가장 최근 예배 기준 월
latest_date = max(date_map.keys())

year = latest_date.year
month = latest_date.month

cal = calendar.Calendar(firstweekday=6)  # 일요일 시작

weeks = cal.monthdayscalendar(year, month)

rows = []

for week in weeks:

    cells = []

    for day in week:

        if day == 0:
            cells.append("<td></td>")
            continue

        current = datetime(year, month, day).date()

        if current in date_map:

            filename = date_map[current]

            if current == latest_date:
                cells.append(
                    f'<td class="today">'
                    f'<a href="./archive/{filename}">{day}</a>'
                    f'</td>'
                )
            else:
                cells.append(
                    f'<td>'
                    f'<a href="./archive/{filename}">{day}</a>'
                    f'</td>'
                )

        else:
            cells.append(f"<td>{day}</td>")

    rows.append("<tr>" + "".join(cells) + "</tr>")

calendar_html = "\n".join(rows)

# =========================
# index.html 생성
# =========================

index_html = f"""
<!DOCTYPE html>
<html lang="ko">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>가정예배</title>

<link rel="stylesheet" href="./assets/style.css">

<style>

.calendar {{
    width:100%;
    border-collapse:collapse;
}}

.calendar th,
.calendar td {{
    border:1px solid #ddd;
    text-align:center;
    padding:10px;
}}

.nav-area {{
    display:flex;
    justify-content:center;
    align-items:center;
    gap:16px;
    margin:20px 0;
}}

.nav-btn {{
    background:#4f7cff;
    color:white;
    border:none;
    border-radius:10px;
    padding:10px 18px;
    cursor:pointer;
    font-size:15px;
    font-weight:600;
    transition:0.2s;
}}

.nav-btn:hover {{
    transform:translateY(-1px);
    opacity:0.9;
}}

.month-title {{
    min-width:180px;
    text-align:center;
    font-size:1.3rem;
    font-weight:bold;
}}

.month-btn {{

    margin:3px;

    padding:6px 12px;

    border:none;

    border-radius:8px;

    cursor:pointer;

    background:#f0f0f0;
}}

.year-buttons{{
    display:flex;
    justify-content:center;
    flex-wrap:wrap;
    gap:8px;
    margin-bottom:15px;
}}

.year-btn{{

    border:none;

    border-radius:999px;

    padding:8px 16px;

    cursor:pointer;

    background:#eceff4;

    font-weight:600;

    transition:0.2s;
}}

.year-btn:hover{{
    transform:translateY(-1px);
}}

.year-btn.active{{
    background:#4f7cff;
    color:white;
}}

</style>

</head>

<body>

<div class="sheet">

<h1>가정예배</h1>

<p>
<a href="./latest.html">✨ 오늘의 예배</a>
</p>

<div class="nav-area">

<button id="prevBtn" class="nav-btn"
        onclick="prevMonth()">
    ◀ 이전달
</button>


<div id="yearButtons" class="year-buttons"></div>

<div id="monthButtons" class="month-buttons"></div>

<div id="monthTitle"
     class="month-title">
</div>

<button id="nextBtn" class="nav-btn"
        onclick="nextMonth()">
    다음달 ▶
</button>

</div>

<table class="calendar">

<thead>
<tr>
<th>일</th>
<th>월</th>
<th>화</th>
<th>수</th>
<th>목</th>
<th>금</th>
<th>토</th>
</tr>
</thead>

<tbody id="calendarBody">
</tbody>

</table>

</div>

<script>

const worships = {json.dumps(worships, ensure_ascii=False)};

const years =
    Object.keys(worships)
    .map(x => x.substring(0,4));

const uniqueYears =
    [...new Set(years)].sort();

let currentYear = 2026;
let currentMonth = 6;

const dates = Object.keys(worships);

const latest = dates.sort().slice(-1)[0];

const first = dates[0];

const minYear =
    parseInt(first.substring(0,4));

const minMonth =
    parseInt(first.substring(5,7));

const maxYear =
    parseInt(latest.substring(0,4));

const maxMonth =
    parseInt(latest.substring(5,7));

currentYear = parseInt(latest.substring(0,4));
currentMonth = parseInt(latest.substring(5,7));

function renderCalendar() {{

    const body = document.getElementById("calendarBody");
    const title = document.getElementById("monthTitle");

    body.innerHTML = "";

    title.textContent =
        currentYear + "년 " + currentMonth + "월";

    const firstDay =
        new Date(currentYear,currentMonth-1,1);

    const start =
        firstDay.getDay();

    const lastDate =
        new Date(currentYear,currentMonth,0).getDate();

    let row = document.createElement("tr");

    for(let i=0;i<start;i++) {{
        row.appendChild(document.createElement("td"));
    }}

    for(let day=1;day<=lastDate;day++) {{

        const td =
            document.createElement("td");

        const key =
            currentYear + "-" +
            String(currentMonth).padStart(2,'0') + "-" +
            String(day).padStart(2,'0');

        if(worships[key]) {{
        
            td.classList.add("has-worship");
        
            if(key === latest){{
                td.classList.add("latest");
            }}
        
            td.innerHTML =
                '<a href="' +
                worships[key] +
                '">' +
                day +
                '</a>';
        }}
        else {{
            td.textContent = day;
        }}

        row.appendChild(td);

        if((start + day) % 7 === 0) {{
            body.appendChild(row);
            row = document.createElement("tr");
        }}
    }}
    updateNavButtons();
    body.appendChild(row);
}}

function prevMonth() {{

    currentMonth--;

    if(currentMonth < 1) {{
        currentMonth = 12;
        currentYear--;
    }}

    buildYearButtons();
    buildMonthButtons();
    renderCalendar();
}}

function nextMonth() {{

    currentMonth++;

    if(currentMonth > 12) {{
        currentMonth = 1;
        currentYear++;
    }}

    buildYearButtons();
    buildMonthButtons();
    renderCalendar();
}}

renderCalendar();
function updateNavButtons() {{

    const prevBtn =
        document.getElementById("prevBtn");

    const nextBtn =
        document.getElementById("nextBtn");

    prevBtn.disabled =
        (currentYear === minYear &&
         currentMonth === minMonth);

    nextBtn.disabled =
        (currentYear === maxYear &&
         currentMonth === maxMonth);
}}

function buildYearButtons(){{

    const area =
        document.getElementById("yearButtons");

    area.innerHTML = "";

    uniqueYears.forEach(year=>{{

        const btn =
            document.createElement("button");

        btn.className = "year-btn";

        if(parseInt(year) === currentYear){{
            btn.classList.add("active");
        }}

        btn.textContent = year;

        btn.onclick = ()=>{{

            currentYear =
                parseInt(year);

            buildYearButtons();
            buildMonthButtons();
            renderCalendar();
        }};

        area.appendChild(btn);
    }});
}}

function buildMonthButtons() {{

    const area =
        document.getElementById("monthButtons");

    area.innerHTML = "";

    for(let m=1;m<=12;m++) {{

        const btn =
            document.createElement("button");

        btn.className = "month-btn";

        if(m === currentMonth){{
            btn.classList.add("active");
        }}

        btn.textContent =
            String(m).padStart(2,'0');

        btn.onclick = ()=>{{

            currentMonth = m;

            buildMonthButtons();

            renderCalendar();
        }};

        area.appendChild(btn);
    }}
}}

buildYearButtons();
buildMonthButtons();
renderCalendar();

</script>

</body>

</html>
"""
Path("index.html").write_text(
    index_html,
    encoding="utf-8"
)

print("Generated calendar index.html")