from flask import Flask, render_template, request, send_file, send_from_directory, Response, make_response

# from models.database import db.session
from datetime import datetime
import ast
import json
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import chromedriver_binary
from selenium.common.exceptions import NoSuchElementException
import mojimoji
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4, portrait
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
import base64

# Flaskオブジェクトの生成
app = Flask(__name__)

from app.models import db, Course
# 最初のページ
@app.route("/")
def index():
    # 基本的にはDBには授業内容が入っているので，データの作成をする必要はない
    getDB = False
    # もしDBの中身を全件取得して
    getDB = Course.query.all()
    # 空だった場合は
    if getDB == []:
        # データの作成をする必要がある
        getDB = True
    # データを作成するための表示にする
    return render_template("index.html",
                            getDB=getDB,
                            errorMsg="",
                            classroom=["A", "B", "C", "D", "E", "F"],
                            language=["フランス", "ドイツ", "スペイン", "中国", "ロシア", "韓国"])

# リセット押下時
@app.route("/", methods=["post"])
def reset():
    return render_template("index.html",
                            getDB=False,
                            errorMsg="",
                            classroom=["A", "B", "C", "D", "E", "F"],
                            language=["フランス", "ドイツ", "スペイン", "中国", "ロシア", "韓国"])

@app.route("/save")
def no_save():
    return render_template("index.html",
                            getDB=False,
                            errorMsg="",
                            classroom=["A", "B", "C", "D", "E", "F"],
                            language=["フランス", "ドイツ", "スペイン", "中国", "ロシア", "韓国"])

# PDF保存時
@app.route("/save", methods=["post"])
def make():
    if request.form.get("save") != None:
        pdf_data = request.form.get("save")
        dic_pdf_data = ast.literal_eval(pdf_data)
        first = ast.literal_eval(dic_pdf_data["first"])
        second = ast.literal_eval(dic_pdf_data["second"])
        response = make_response()
        downloadFileName = str(datetime.now()) + '.pdf'
        pdf_canvas = canvas.Canvas('./test.pdf',  pagesize=portrait(A4))
        print_string(pdf_canvas, dic_pdf_data["classroom"],
                     dic_pdf_data["language"], dic_pdf_data["count"], first, second)
        pdf_canvas.save()
        response.data = open("./test.pdf", "rb").read()
        response.headers['Content-Disposition'] = 'attachment; filename=' + \
            downloadFileName
        os.remove("./test.pdf")
        return response

# 履歴書フォーマット作成
def print_string(pdf_canvas, classroom, language, count, first, second):
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))  # フォント

    # クラス，第二外国語，単位数
    font_size = 12  # フォントサイズ
    pdf_canvas.setFont('HeiseiKakuGo-W5', font_size)
    pdf_canvas.drawString(70, 750, 'クラス：' + classroom)  # 書き出し(横位置, 縦位置, 文字)
    pdf_canvas.drawString(140, 750, '第二外国語：' + language)  # 書き出し(横位置, 縦位置, 文字)
    pdf_canvas.drawString(450, 750, '単位数：' + count)  # 書き出し(横位置, 縦位置, 文字)

    # 前期の時間割表
    first_data = [
        ['前', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'],
        ['1', '', '', '', '', '', ''],
        ['2', '', '', '', '', '', ''],
        ['3', '', '', '', '', '', ''],
        ['4', '', '', '', '', '', ''],
        ['5', '', '', '', '', '', '']
    ]

    # 入力されていたデータを追加
    for n, f in enumerate(first):
        for i in range(5):
            ans = ""
            if "Integrated" not in first[f][i]:
                a = 5
            else:
                a = 10
            for k, j in enumerate(first[f][i]):
                if k > 1 and k % a == 0:
                    ans += j + "\n"
                else:
                    ans += j
            first_data[i+1][n+1] = ans

    # 書き出す
    table = Table(first_data, colWidths=(10*mm, 25*mm, 25*mm, 25*mm, 25*mm, 25*mm, 25*mm),
                  rowHeights=(10*mm, 20*mm, 20*mm, 20*mm, 20*mm, 20*mm))
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'HeiseiKakuGo-W5', 10),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    table.wrapOn(pdf_canvas, 25*mm, 145*mm)
    table.drawOn(pdf_canvas, 25*mm, 145*mm)

    # 後期の時間割表
    second_data = [
        ['後', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'],
        ['1', '', '', '', '', '', ''],
        ['2', '', '', '', '', '', ''],
        ['3', '', '', '', '', '', ''],
        ['4', '', '', '', '', '', ''],
        ['5', '', '', '', '', '', '']
    ]

    # 入力されていたデータを追加
    for n, f in enumerate(second):
        for i in range(5):
            ans = ""
            if "Integrated" not in second[f][i]:
                a = 5
            else:
                a = 10
            for k, j in enumerate(second[f][i]):
                if k > 1 and k % a == 0:
                    ans += j + "\n"
                else:
                    ans += j
            second_data[i+1][n+1] = ans

    # 書き出す
    table = Table(second_data, colWidths=(10*mm, 25*mm, 25*mm, 25*mm, 25*mm, 25*mm, 25*mm),
                  rowHeights=(10*mm, 20*mm, 20*mm, 20*mm, 20*mm, 20*mm))
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'HeiseiKakuGo-W5', 11),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    table.wrapOn(pdf_canvas, 25*mm, 25*mm)
    table.drawOn(pdf_canvas, 25*mm, 25*mm)

    pdf_canvas.showPage()

@app.route("/import")
def no_import():
    return render_template("index.html",
                            getDB=False,
                            errorMsg="",
                            classroom=["A", "B", "C", "D", "E", "F"],
                            language=["フランス", "ドイツ", "スペイン", "中国", "ロシア", "韓国"])

# データインポート時
@app.route("/import", methods=["post"])
def data_import():
    selectBtn = []
    getDB = []
    time = [1, 2, 3, 4, 5]
    errorMsg = ""
    if 'uploadFile' not in request.files:
        errorMsg = "ファイルが選択されていません．"
    else:
        file = request.files['uploadFile']
        fileData = file.read().decode()
        if '{' in fileData:
            dic = ast.literal_eval(fileData)
            first = ast.literal_eval(dic["first"])
            second = ast.literal_eval(dic["second"])
            return render_template("course.html",
                                    first=first,
                                    second=second,
                                    count=dic["count"],
                                    selectBtn=selectBtn,
                                    getDB=getDB,
                                    time=time, 
                                    classroom=dic["classroom"],
                                    language=dic["language"])
        else:
            errorMsg = "入力したファイルが正しくありません．再度お試しください．"
    return render_template("index.html",
                            getDB=False,
                            errorMsg=errorMsg,
                            classroom=["A", "B", "C", "D", "E", "F"],
                            language=["フランス", "ドイツ", "スペイン", "中国", "ロシア", "韓国"])

@app.route("/export")
def no_export():
    return render_template("index.html",
                            getDB=False,
                            errorMsg="",
                            classroom=["A", "B", "C", "D", "E", "F"],
                            language=["フランス", "ドイツ", "スペイン", "中国", "ロシア", "韓国"])

@app.route("/export", methods=["post"])
def data_export():
    if request.form.get("export") != None:
        export_data = request.form.get("export")
        response = make_response()
        response.data = export_data
        downloadFileName = str(datetime.now()) + '.txt'
        response.headers['Content-Disposition'] = 'attachment; filename=' + \
            downloadFileName
        return response
    return render_template("index.html",
                            getDB=False,
                            errorMsg="",
                            classroom=["A", "B", "C", "D", "E", "F"],
                            language=["フランス", "ドイツ", "スペイン", "中国", "ロシア", "韓国"])

@app.route("/get")
def no_get():
    return render_template("index.html", getDB=False, errorMsg="", classroom=["A", "B", "C", "D", "E", "F"], language=["フランス", "ドイツ", "スペイン", "中国", "ロシア", "韓国"])

@app.route("/get", methods=["post"])
def get():
    db.session.query(Course).delete()
    db.session.commit()

    test = ["社会数理入門Ⅰ", "社会数理入門Ⅱ", "数理情報Ⅰ",
            "数理情報Ⅱ", "ウェルカム・レクチャー", "キャリアデザイン・セミナー"]
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('chromedriver', options=options)
    driver.implicitly_wait(10)

    for i in test:
        CourseTitle = i
        driver.get("http://syllabus.aoyama.ac.jp/")

        driver.find_element_by_id('CPH1_KM').send_keys(CourseTitle)

        driver.find_element_by_id('CPH1_btnKensaku').click()

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        result = int(soup.select("#CPH1_lblHitMsg")[0].getText())
        if (result != 0):
            for i in range(result):
                test = soup.select(
                    "#CPH1_gvw_kensaku_lblJigen_" + str(i))[0].get_text()
                a = test.find("[")
                b = test.find("]")
                c = test.find("（")
                db_campus = test[a+1:b-a]
                db_day = test[b+1:b+2]
                db_time = mojimoji.zen_to_han(test[b+2:b+3])
                db_semester = test[c+1:c+2]

                db_title = soup.select(
                    "#CPH1_gvw_kensaku_lblKamoku_" + str(i))[0].get_text()
                db_instructer = soup.select(
                    "#CPH1_gvw_kensaku_lblKyouin_" + str(i))[0].get_text()
                db_detail = "http://syllabus.aoyama.ac.jp/" + \
                    soup.select("#CPH1_gvw_kensaku_lnkShousai_" +
                                str(i))[0].get("href")
                content = Course(db_day, db_time, db_campus, db_semester,
                                db_title, db_instructer, db_detail)
                db.session.add(content)
                db.session.commit()

    test2 = ["フレッシャーズ・セミナー", "自己理解", "現代社会の諸問題", "科学・技術の視点", "歴史と人間"]
    for i in test2:
        CourseTitle = i

        driver.get("http://syllabus.aoyama.ac.jp/")
        driver.find_element_by_id('CPH1_KM').send_keys(CourseTitle)

        driver.find_element_by_id('CPH1_rptYB_YB_0').click()

        driver.find_element_by_id('CPH1_btnKensaku').click()

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        result = int(soup.select("#CPH1_lblHitMsg")[0].getText())
        if (result != 0):
            for i in range(result):
                test = soup.select(
                    "#CPH1_gvw_kensaku_lblJigen_" + str(i))[0].get_text()
                a = test.find("[")
                b = test.find("]")
                c = test.find("（")
                db_campus = test[a+1:b-a]
                db_day = test[b+1:b+2]
                db_time = mojimoji.zen_to_han(test[b+2:b+3])
                db_semester = test[c+1:c+2]

                db_title = soup.select(
                    "#CPH1_gvw_kensaku_lblKamoku_" + str(i))[0].get_text()
                db_instructer = soup.select(
                    "#CPH1_gvw_kensaku_lblKyouin_" + str(i))[0].get_text()
                db_detail = "http://syllabus.aoyama.ac.jp/" + \
                    soup.select("#CPH1_gvw_kensaku_lnkShousai_" +
                                str(i))[0].get("href")
                content = Course(db_day, db_time, db_campus, db_semester, db_title, db_instructer, db_detail)
                db.session.add(content)
                db.session.commit()

        driver.find_element_by_id('CPH1_rptYB_YB_0').click()
        driver.find_element_by_id('CPH1_rptYB_YB_1').click()
        driver.find_element_by_id('CPH1_btnKensaku').click()

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        result = int(soup.select("#CPH1_lblHitMsg")[0].getText())
        if (result != 0):
            for i in range(result):
                test = soup.select(
                    "#CPH1_gvw_kensaku_lblJigen_" + str(i))[0].get_text()
                a = test.find("[")
                b = test.find("]")
                c = test.find("（")
                db_campus = test[a+1:b-a]
                db_day = test[b+1:b+2]
                db_time = mojimoji.zen_to_han(test[b+2:b+3])
                db_semester = test[c+1:c+2]

                db_title = soup.select(
                    "#CPH1_gvw_kensaku_lblKamoku_" + str(i))[0].get_text()
                db_instructer = soup.select(
                    "#CPH1_gvw_kensaku_lblKyouin_" + str(i))[0].get_text()
                db_detail = "http://syllabus.aoyama.ac.jp/" + \
                    soup.select("#CPH1_gvw_kensaku_lnkShousai_" +
                                str(i))[0].get("href")
                content = Course(db_day, db_time, db_campus, db_semester, db_title, db_instructer, db_detail)
                db.session.add(content)
                db.session.commit()

        driver.find_element_by_id('CPH1_rptYB_YB_1').click()
        driver.find_element_by_id('CPH1_rptYB_YB_2').click()

        driver.find_element_by_id('CPH1_btnKensaku').click()

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        result = int(soup.select("#CPH1_lblHitMsg")[0].getText())
        if (result != 0):
            for i in range(result):
                test = soup.select(
                    "#CPH1_gvw_kensaku_lblJigen_" + str(i))[0].get_text()
                a = test.find("[")
                b = test.find("]")
                c = test.find("（")
                db_campus = test[a+1:b-a]
                db_day = test[b+1:b+2]
                db_time = mojimoji.zen_to_han(test[b+2:b+3])
                db_semester = test[c+1:c+2]

                db_title = soup.select(
                    "#CPH1_gvw_kensaku_lblKamoku_" + str(i))[0].get_text()
                db_instructer = soup.select(
                    "#CPH1_gvw_kensaku_lblKyouin_" + str(i))[0].get_text()
                db_detail = "http://syllabus.aoyama.ac.jp/" + \
                    soup.select("#CPH1_gvw_kensaku_lnkShousai_" +
                                str(i))[0].get("href")
                content = Course(db_day, db_time, db_campus, db_semester, db_title, db_instructer, db_detail)
                db.session.add(content)
                db.session.commit()

        driver.find_element_by_id('CPH1_rptYB_YB_2').click()
        driver.find_element_by_id('CPH1_rptYB_YB_3').click()

        driver.find_element_by_id('CPH1_btnKensaku').click()

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        result = int(soup.select("#CPH1_lblHitMsg")[0].getText())
        if (result != 0):
            for i in range(result):
                test = soup.select(
                    "#CPH1_gvw_kensaku_lblJigen_" + str(i))[0].get_text()
                a = test.find("[")
                b = test.find("]")
                c = test.find("（")
                db_campus = test[a+1:b-a]
                db_day = test[b+1:b+2]
                db_time = mojimoji.zen_to_han(test[b+2:b+3])
                db_semester = test[c+1:c+2]

                db_title = soup.select(
                    "#CPH1_gvw_kensaku_lblKamoku_" + str(i))[0].get_text()
                db_instructer = soup.select(
                    "#CPH1_gvw_kensaku_lblKyouin_" + str(i))[0].get_text()
                db_detail = "http://syllabus.aoyama.ac.jp/" + \
                    soup.select("#CPH1_gvw_kensaku_lnkShousai_" +
                                str(i))[0].get("href")
                content = Course(db_day, db_time, db_campus, db_semester, db_title, db_instructer, db_detail)
                db.session.add(content)
                db.session.commit()

        driver.find_element_by_id('CPH1_rptYB_YB_3').click()
        driver.find_element_by_id('CPH1_rptYB_YB_4').click()

        driver.find_element_by_id('CPH1_btnKensaku').click()

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        result = int(soup.select("#CPH1_lblHitMsg")[0].getText())
        if (result != 0):
            for i in range(result):
                test = soup.select(
                    "#CPH1_gvw_kensaku_lblJigen_" + str(i))[0].get_text()
                a = test.find("[")
                b = test.find("]")
                c = test.find("（")
                db_campus = test[a+1:b-a]
                db_day = test[b+1:b+2]
                db_time = mojimoji.zen_to_han(test[b+2:b+3])
                db_semester = test[c+1:c+2]

                db_title = soup.select(
                    "#CPH1_gvw_kensaku_lblKamoku_" + str(i))[0].get_text()
                db_instructer = soup.select(
                    "#CPH1_gvw_kensaku_lblKyouin_" + str(i))[0].get_text()
                db_detail = "http://syllabus.aoyama.ac.jp/" + \
                    soup.select("#CPH1_gvw_kensaku_lnkShousai_" +
                                str(i))[0].get("href")
                content = Course(db_day, db_time, db_campus, db_semester, db_title, db_instructer, db_detail)
                db.session.add(content)
                db.session.commit()

    CourseTitle = "健康・スポーツ演習"

    # 前期月
    for i in range(2):
        driver.get("http://syllabus.aoyama.ac.jp/")
        semester_element = driver.find_element_by_id('CPH1_GKB')
        semester_select_element = Select(semester_element)
        driver.find_element_by_id('CPH1_rptCP_CP_' + str(i)).click()
        semester_select_element.select_by_value('1.1.12')
        driver.find_element_by_id('CPH1_rptYB_YB_0').click()

        driver.find_element_by_id('CPH1_KM').send_keys(CourseTitle)
        driver.find_element_by_id('CPH1_btnKensaku').click()

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        result = int(soup.select("#CPH1_lblHitMsg")[0].getText())
        if (result != 0):
            for i in range(result):
                test = soup.select(
                    "#CPH1_gvw_kensaku_lblJigen_" + str(i))[0].get_text()
                a = test.find("[")
                b = test.find("]")
                c = test.find("（")
                db_campus = test[a+1:b-a]
                db_day = test[b+1:b+2]
                db_time = mojimoji.zen_to_han(test[b+2:b+3])
                db_semester = test[c+1:c+2]
                db_title = soup.select(
                    "#CPH1_gvw_kensaku_lblKamoku_" + str(i))[0].get_text()
                db_instructer = soup.select(
                    "#CPH1_gvw_kensaku_lblKyouin_" + str(i))[0].get_text()
                db_detail = "http://syllabus.aoyama.ac.jp/" + \
                    soup.select("#CPH1_gvw_kensaku_lnkShousai_" +
                                str(i))[0].get("href")
                content = Course(db_day, db_time, db_campus, db_semester, db_title, db_instructer, db_detail)
                db.session.add(content)
                db.session.commit()

    # 後期月
    for i in range(2):
        driver.get("http://syllabus.aoyama.ac.jp/")
        semester_element = driver.find_element_by_id('CPH1_GKB')
        semester_select_element = Select(semester_element)
        driver.find_element_by_id('CPH1_rptCP_CP_' + str(i)).click()
        semester_select_element.select_by_value('1.2.12')
        driver.find_element_by_id('CPH1_rptYB_YB_0').click()

        driver.find_element_by_id('CPH1_KM').send_keys(CourseTitle)
        driver.find_element_by_id('CPH1_btnKensaku').click()

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        result = int(soup.select("#CPH1_lblHitMsg")[0].getText())
        if (result != 0):
            for i in range(result):
                test = soup.select(
                    "#CPH1_gvw_kensaku_lblJigen_" + str(i))[0].get_text()
                a = test.find("[")
                b = test.find("]")
                c = test.find("（")
                db_campus = test[a+1:b-a]
                db_day = test[b+1:b+2]
                db_time = mojimoji.zen_to_han(test[b+2:b+3])
                db_semester = test[c+1:c+2]
                db_title = soup.select(
                    "#CPH1_gvw_kensaku_lblKamoku_" + str(i))[0].get_text()
                db_instructer = soup.select(
                    "#CPH1_gvw_kensaku_lblKyouin_" + str(i))[0].get_text()
                db_detail = "http://syllabus.aoyama.ac.jp/" + \
                    soup.select("#CPH1_gvw_kensaku_lnkShousai_" +
                                str(i))[0].get("href")
                content = Course(db_day, db_time, db_campus, db_semester, db_title, db_instructer, db_detail)
                db.session.add(content)
                db.session.commit()

    # 前期火
    for i in range(2):
        driver.get("http://syllabus.aoyama.ac.jp/")
        semester_element = driver.find_element_by_id('CPH1_GKB')
        semester_select_element = Select(semester_element)
        driver.find_element_by_id('CPH1_rptCP_CP_' + str(i)).click()
        semester_select_element.select_by_value('1.1.12')
        driver.find_element_by_id('CPH1_rptYB_YB_1').click()

        driver.find_element_by_id('CPH1_KM').send_keys(CourseTitle)
        driver.find_element_by_id('CPH1_btnKensaku').click()

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        result = int(soup.select("#CPH1_lblHitMsg")[0].getText())
        if (result != 0):
            for i in range(result):
                test = soup.select(
                    "#CPH1_gvw_kensaku_lblJigen_" + str(i))[0].get_text()
                a = test.find("[")
                b = test.find("]")
                c = test.find("（")
                db_campus = test[a+1:b-a]
                db_day = test[b+1:b+2]
                db_time = mojimoji.zen_to_han(test[b+2:b+3])
                db_semester = test[c+1:c+2]
                db_title = soup.select(
                    "#CPH1_gvw_kensaku_lblKamoku_" + str(i))[0].get_text()
                db_instructer = soup.select(
                    "#CPH1_gvw_kensaku_lblKyouin_" + str(i))[0].get_text()
                db_detail = "http://syllabus.aoyama.ac.jp/" + \
                    soup.select("#CPH1_gvw_kensaku_lnkShousai_" +
                                str(i))[0].get("href")
                content = Course(db_day, db_time, db_campus, db_semester, db_title, db_instructer, db_detail)
                db.session.add(content)
                db.session.commit()

    # 後期火
    for i in range(2):
        driver.get("http://syllabus.aoyama.ac.jp/")
        semester_element = driver.find_element_by_id('CPH1_GKB')
        semester_select_element = Select(semester_element)
        driver.find_element_by_id('CPH1_rptCP_CP_' + str(i)).click()
        semester_select_element.select_by_value('1.2.12')
        driver.find_element_by_id('CPH1_rptYB_YB_1').click()

        driver.find_element_by_id('CPH1_KM').send_keys(CourseTitle)
        driver.find_element_by_id('CPH1_btnKensaku').click()

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        result = int(soup.select("#CPH1_lblHitMsg")[0].getText())
        if (result != 0):
            for i in range(result):
                test = soup.select(
                    "#CPH1_gvw_kensaku_lblJigen_" + str(i))[0].get_text()
                a = test.find("[")
                b = test.find("]")
                c = test.find("（")
                db_campus = test[a+1:b-a]
                db_day = test[b+1:b+2]
                db_time = mojimoji.zen_to_han(test[b+2:b+3])
                db_semester = test[c+1:c+2]
                db_title = soup.select(
                    "#CPH1_gvw_kensaku_lblKamoku_" + str(i))[0].get_text()
                db_instructer = soup.select(
                    "#CPH1_gvw_kensaku_lblKyouin_" + str(i))[0].get_text()
                db_detail = "http://syllabus.aoyama.ac.jp/" + \
                    soup.select("#CPH1_gvw_kensaku_lnkShousai_" +
                                str(i))[0].get("href")
                content = Course(db_day, db_time, db_campus, db_semester, db_title, db_instructer, db_detail)
                db.session.add(content)
                db.session.commit()

    # 前期水
    for i in range(2):
        driver.get("http://syllabus.aoyama.ac.jp/")
        semester_element = driver.find_element_by_id('CPH1_GKB')
        semester_select_element = Select(semester_element)
        driver.find_element_by_id('CPH1_rptCP_CP_' + str(i)).click()
        semester_select_element.select_by_value('1.1.12')
        driver.find_element_by_id('CPH1_rptYB_YB_2').click()

        driver.find_element_by_id('CPH1_KM').send_keys(CourseTitle)
        driver.find_element_by_id('CPH1_btnKensaku').click()

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        result = int(soup.select("#CPH1_lblHitMsg")[0].getText())
        if (result != 0):
            for i in range(result):
                test = soup.select(
                    "#CPH1_gvw_kensaku_lblJigen_" + str(i))[0].get_text()
                a = test.find("[")
                b = test.find("]")
                c = test.find("（")
                db_campus = test[a+1:b-a]
                db_day = test[b+1:b+2]
                db_time = mojimoji.zen_to_han(test[b+2:b+3])
                db_semester = test[c+1:c+2]
                db_title = soup.select(
                    "#CPH1_gvw_kensaku_lblKamoku_" + str(i))[0].get_text()
                db_instructer = soup.select(
                    "#CPH1_gvw_kensaku_lblKyouin_" + str(i))[0].get_text()
                db_detail = "http://syllabus.aoyama.ac.jp/" + \
                    soup.select("#CPH1_gvw_kensaku_lnkShousai_" +
                                str(i))[0].get("href")
                content = Course(db_day, db_time, db_campus, db_semester, db_title, db_instructer, db_detail)
                db.session.add(content)
                db.session.commit()

    # 後期水
    for i in range(2):
        driver.get("http://syllabus.aoyama.ac.jp/")
        semester_element = driver.find_element_by_id('CPH1_GKB')
        semester_select_element = Select(semester_element)
        driver.find_element_by_id('CPH1_rptCP_CP_' + str(i)).click()
        semester_select_element.select_by_value('1.2.12')
        driver.find_element_by_id('CPH1_rptYB_YB_2').click()

        driver.find_element_by_id('CPH1_KM').send_keys(CourseTitle)
        driver.find_element_by_id('CPH1_btnKensaku').click()

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        result = int(soup.select("#CPH1_lblHitMsg")[0].getText())
        if (result != 0):
            for i in range(result):
                test = soup.select(
                    "#CPH1_gvw_kensaku_lblJigen_" + str(i))[0].get_text()
                a = test.find("[")
                b = test.find("]")
                c = test.find("（")
                db_campus = test[a+1:b-a]
                db_day = test[b+1:b+2]
                db_time = mojimoji.zen_to_han(test[b+2:b+3])
                db_semester = test[c+1:c+2]
                db_title = soup.select(
                    "#CPH1_gvw_kensaku_lblKamoku_" + str(i))[0].get_text()
                db_instructer = soup.select(
                    "#CPH1_gvw_kensaku_lblKyouin_" + str(i))[0].get_text()
                db_detail = "http://syllabus.aoyama.ac.jp/" + \
                    soup.select("#CPH1_gvw_kensaku_lnkShousai_" +
                                str(i))[0].get("href")
                content = Course(db_day, db_time, db_campus, db_semester, db_title, db_instructer, db_detail)
                db.session.add(content)
                db.session.commit()

    # 前期木
    for i in range(2):
        driver.get("http://syllabus.aoyama.ac.jp/")
        semester_element = driver.find_element_by_id('CPH1_GKB')
        semester_select_element = Select(semester_element)
        driver.find_element_by_id('CPH1_rptCP_CP_' + str(i)).click()
        semester_select_element.select_by_value('1.1.12')
        driver.find_element_by_id('CPH1_rptYB_YB_3').click()

        driver.find_element_by_id('CPH1_KM').send_keys(CourseTitle)
        driver.find_element_by_id('CPH1_btnKensaku').click()

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        result = int(soup.select("#CPH1_lblHitMsg")[0].getText())
        if (result != 0):
            for i in range(result):
                test = soup.select(
                    "#CPH1_gvw_kensaku_lblJigen_" + str(i))[0].get_text()
                a = test.find("[")
                b = test.find("]")
                c = test.find("（")
                db_campus = test[a+1:b-a]
                db_day = test[b+1:b+2]
                db_time = mojimoji.zen_to_han(test[b+2:b+3])
                db_semester = test[c+1:c+2]
                db_title = soup.select(
                    "#CPH1_gvw_kensaku_lblKamoku_" + str(i))[0].get_text()
                db_instructer = soup.select(
                    "#CPH1_gvw_kensaku_lblKyouin_" + str(i))[0].get_text()
                db_detail = "http://syllabus.aoyama.ac.jp/" + \
                    soup.select("#CPH1_gvw_kensaku_lnkShousai_" +
                                str(i))[0].get("href")
                content = Course(db_day, db_time, db_campus, db_semester, db_title, db_instructer, db_detail)
                db.session.add(content)
                db.session.commit()

    # 後期木
    for i in range(2):
        driver.get("http://syllabus.aoyama.ac.jp/")
        semester_element = driver.find_element_by_id('CPH1_GKB')
        semester_select_element = Select(semester_element)
        driver.find_element_by_id('CPH1_rptCP_CP_' + str(i)).click()
        semester_select_element.select_by_value('1.2.12')
        driver.find_element_by_id('CPH1_rptYB_YB_3').click()

        driver.find_element_by_id('CPH1_KM').send_keys(CourseTitle)
        driver.find_element_by_id('CPH1_btnKensaku').click()

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        result = int(soup.select("#CPH1_lblHitMsg")[0].getText())
        if (result != 0):
            for i in range(result):
                test = soup.select(
                    "#CPH1_gvw_kensaku_lblJigen_" + str(i))[0].get_text()
                a = test.find("[")
                b = test.find("]")
                c = test.find("（")
                db_campus = test[a+1:b-a]
                db_day = test[b+1:b+2]
                db_time = mojimoji.zen_to_han(test[b+2:b+3])
                db_semester = test[c+1:c+2]
                db_title = soup.select(
                    "#CPH1_gvw_kensaku_lblKamoku_" + str(i))[0].get_text()
                db_instructer = soup.select(
                    "#CPH1_gvw_kensaku_lblKyouin_" + str(i))[0].get_text()
                db_detail = "http://syllabus.aoyama.ac.jp/" + \
                    soup.select("#CPH1_gvw_kensaku_lnkShousai_" +
                                str(i))[0].get("href")
                content = Course(db_day, db_time, db_campus, db_semester, db_title, db_instructer, db_detail)
                db.session.add(content)
                db.session.commit()

    # 前期金
    for i in range(2):
        driver.get("http://syllabus.aoyama.ac.jp/")
        semester_element = driver.find_element_by_id('CPH1_GKB')
        semester_select_element = Select(semester_element)
        driver.find_element_by_id('CPH1_rptCP_CP_' + str(i)).click()
        semester_select_element.select_by_value('1.1.12')
        driver.find_element_by_id('CPH1_rptYB_YB_4').click()

        driver.find_element_by_id('CPH1_KM').send_keys(CourseTitle)
        driver.find_element_by_id('CPH1_btnKensaku').click()

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        result = int(soup.select("#CPH1_lblHitMsg")[0].getText())
        if (result != 0):
            for i in range(result):
                test = soup.select(
                    "#CPH1_gvw_kensaku_lblJigen_" + str(i))[0].get_text()
                a = test.find("[")
                b = test.find("]")
                c = test.find("（")
                db_campus = test[a+1:b-a]
                db_day = test[b+1:b+2]
                db_time = mojimoji.zen_to_han(test[b+2:b+3])
                db_semester = test[c+1:c+2]
                db_title = soup.select(
                    "#CPH1_gvw_kensaku_lblKamoku_" + str(i))[0].get_text()
                db_instructer = soup.select(
                    "#CPH1_gvw_kensaku_lblKyouin_" + str(i))[0].get_text()
                db_detail = "http://syllabus.aoyama.ac.jp/" + \
                    soup.select("#CPH1_gvw_kensaku_lnkShousai_" +
                                str(i))[0].get("href")
                content = Course(db_day, db_time, db_campus, db_semester, db_title, db_instructer, db_detail)
                db.session.add(content)
                db.session.commit()

    # 後期金
    for i in range(2):
        driver.get("http://syllabus.aoyama.ac.jp/")
        semester_element = driver.find_element_by_id('CPH1_GKB')
        semester_select_element = Select(semester_element)
        driver.find_element_by_id('CPH1_rptCP_CP_' + str(i)).click()
        semester_select_element.select_by_value('1.2.12')
        driver.find_element_by_id('CPH1_rptYB_YB_4').click()

        driver.find_element_by_id('CPH1_KM').send_keys(CourseTitle)
        driver.find_element_by_id('CPH1_btnKensaku').click()

        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        result = int(soup.select("#CPH1_lblHitMsg")[0].getText())
        if (result != 0):
            for i in range(result):
                test = soup.select(
                    "#CPH1_gvw_kensaku_lblJigen_" + str(i))[0].get_text()
                a = test.find("[")
                b = test.find("]")
                c = test.find("（")
                db_campus = test[a+1:b-a]
                db_day = test[b+1:b+2]
                db_time = mojimoji.zen_to_han(test[b+2:b+3])
                db_semester = test[c+1:c+2]
                db_title = soup.select(
                    "#CPH1_gvw_kensaku_lblKamoku_" + str(i))[0].get_text()
                db_instructer = soup.select(
                    "#CPH1_gvw_kensaku_lblKyouin_" + str(i))[0].get_text()
                db_detail = "http://syllabus.aoyama.ac.jp/" + \
                    soup.select("#CPH1_gvw_kensaku_lnkShousai_" +
                                str(i))[0].get("href")
                content = Course(db_day, db_time, db_campus, db_semester, db_title, db_instructer, db_detail)
                db.session.add(content)
                db.session.commit()
    return render_template("index.html",
                            getDB=False,
                            errorMsg="",
                            classroom=["A", "B", "C", "D", "E", "F"],
                            language=["フランス", "ドイツ", "スペイン", "中国", "ロシア", "韓国"])

@app.route("/course")
def no_course():
    return render_template("index.html",
                            getDB=False,
                            errorMsg="",
                            classroom=["A", "B", "C", "D", "E", "F"],
                            language=["フランス", "ドイツ", "スペイン", "中国", "ロシア", "韓国"])

@app.route("/course", methods=['GET', 'POST'])
def output():
    if request.method == 'POST':
        class_name = request.form.get("select_class")
        language_name = request.form.get("select_language")
        count = 26
        time = [1, 2, 3, 4, 5]
        getDB = []
        if class_name != None:
            first = {
                "mon": ["", "", "", "", ""],
                "tue": ["", "○コミュニケーション基礎", "", "○社会情報体験演習", "○社会情報体験演習"],
                "wed": ["", "", "", "", ""],
                "thu": ["", "", "", "", ""],
                "fri": ["", "", "○情報科学概論", "", ""],
                "sat": ["", "", "", "", ""]
            }
            second = {
                "mon": ["", "", "○人間科学概論", "", ""],
                "tue": ["", "", "", "○統計入門", "○統計入門"],
                "wed": ["", "", "", "", ""],
                "thu": ["", "", "", "", ""],
                "fri": ["○コンピューティング実習", "○コンピューティング実習", "○社会科学概論", "", ""],
                "sat": ["", "", "", "", ""]
            }
            if class_name == "A" or class_name == "B" or class_name == "C":
                second["thu"][0] = "○キリスト教概論Ⅰ"
                first["mon"][3] = "○Integrated EnglishⅠ"
                first["thu"][4] = "○Integrated EnglishⅠ"
                second["mon"][3] = "○Integrated EnglishⅡ"
                second["thu"][4] = "○Integrated EnglishⅡ"
            else:
                second["thu"][1] = "○キリスト教概論Ⅰ"
                first["mon"][4] = "○Integrated EnglishⅠ"
                first["thu"][3] = "○Integrated EnglishⅠ"
                second["mon"][4] = "○Integrated EnglishⅡ"
                second["thu"][3] = "○Integrated EnglishⅡ"
            if language_name == "ロシア":
                first["sat"][0] = "○" + language_name + "語Ⅰ(A)-1"
                first["sat"][1] = "○" + language_name + "語Ⅰ(B)-1"
                second["sat"][0] = "○" + language_name + "語Ⅰ(A)-2"
                second["sat"][1] = "○" + language_name + "語Ⅰ(B)-2"
            elif language_name == "韓国":
                first["tue"][2] = "○" + language_name + "語Ⅰ(B)-1"
                first["thu"][2] = "○" + language_name + "語Ⅰ(A)-1"
                second["tue"][2] = "○" + language_name + "語Ⅰ(B)-2"
                second["thu"][2] = "○" + language_name + "語Ⅰ(A)-2"
            else:
                first["tue"][2] = "○" + language_name + "語Ⅰ(A)-1"
                first["thu"][2] = "○" + language_name + "語Ⅰ(B)-1"
                second["tue"][2] = "○" + language_name + "語Ⅰ(A)-2"
                second["thu"][2] = "○" + language_name + "語Ⅰ(B)-2"
            return render_template("course.html", 
                                    first=first,
                                    second=second,
                                    count=count,
                                    getDB=getDB,
                                    time=time,
                                    classroom=class_name,
                                    language=language_name)
        else:
            if request.form.get("selectTime") != None:
                select_time_name = request.form.get("selectTime")
                dic_select_time_name = ast.literal_eval(select_time_name)

                first = ast.literal_eval(dic_select_time_name["first"])
                second = ast.literal_eval(dic_select_time_name["second"])
                class_name = dic_select_time_name["classroom"]
                language_name = dic_select_time_name["language"]
                count = dic_select_time_name["count"]
                time = [1, 2, 3, 4, 5]
                getDB = []

                selectBtn = dic_select_time_name["request"].split("/")
                semester, day, times = 0, 0, 0
                if (selectBtn[0] == "first"):
                    semester = "前"
                else:
                    semester = "後"

                if (selectBtn[1] == "mon"):
                    day = "月"
                elif (selectBtn[1] == "tue"):
                    day = "火"
                elif (selectBtn[1] == "wed"):
                    day = "水"
                elif (selectBtn[1] == "thu"):
                    day = "木"
                elif (selectBtn[1] == "fri"):
                    day = "金"
                else:
                    day = "土"

                times = selectBtn[2]
                selectBtn[2] = int(selectBtn[2])

                select_class_db = Course.query.filter_by(
                    semester=semester, day=day, time=times).all()

                for i in select_class_db:
                    getDB.append({"title": i.title, "instructer": i.instructer,
                                  "detail": i.detail, "campus": i.campus})
            elif request.form.get("selectLecture") != None:
                select_lecture_name = request.form.get("selectLecture")
                dic_select_lecture_name = ast.literal_eval(select_lecture_name)

                first = ast.literal_eval(dic_select_lecture_name["first"])
                second = ast.literal_eval(dic_select_lecture_name["second"])
                class_name = dic_select_lecture_name["classroom"]
                language_name = dic_select_lecture_name["language"]
                count = eval(dic_select_lecture_name["count"])
                time = [1, 2, 3, 4, 5]
                getDB = []
                selectBtn = eval(dic_select_lecture_name["request"])

                if (selectBtn[0] == "first"):
                    first[selectBtn[1]][int(
                        selectBtn[2])-1] = dic_select_lecture_name["title"]
                else:
                    second[selectBtn[1]][int(
                        selectBtn[2])-1] = dic_select_lecture_name["title"]
                selectBtn[2] = int(selectBtn[2])
            return render_template("course.html",
                                    first = first,
                                    second = second,
                                    count = count,
                                    selectBtn = selectBtn,
                                    getDB = getDB,
                                    time = time,
                                    classroom=class_name,
                                    language=language_name)
    # おまじない
if __name__ == "__main__":
    app.run(debug=True)
