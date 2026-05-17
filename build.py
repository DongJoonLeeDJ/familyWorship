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
html = html.replace("\n", "<br />")

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

# index.html 생성
# html_files = sorted(
#     ARCHIVE_DIR.glob("*.html"),
#     reverse=True
# )

# links = "\n".join([
#     f'<li><a href="/archive/{f.name}">{f.stem}</a></li>'
#     for f in html_files
# ])

# index_html = f"""
# <!DOCTYPE html>
# <html lang="ko">
# <head>
#   <meta charset="UTF-8" />
#   <meta name="viewport" content="width=device-width, initial-scale=1.0" />

#   <title>가정예배 아카이브</title>

#   <link rel="stylesheet" href="/assets/style.css">
# </head>

# <body>

# <div class="sheet">

#   <h1>가정예배 아카이브</h1>

#   <p>
#     <a href="/latest.html">✨ 최신 예배 바로가기</a>
#   </p>

#   <ul>
#     {links}
#   </ul>

# </div>

# </body>
# </html>
# """

# Path("index.html").write_text(
#     index_html,
#     encoding="utf-8"
# )

# print("Generated index.html")