# 필수 라이브러리
'''
0. Flask : 웹서버를 시작할 수 있는 기능. app이라는 이름으로 플라스크를 시작한다
1. render_template : html파일을 가져와서 보여준다
'''
from flask import Flask, render_template, request, redirect, url_for
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
#  DB 기본 코드
import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    writer = db.Column(db.String(100), nullable=False)
    img_url = db.Column(db.String(10000), nullable=False)

    def __repr__(self):
        return f'{self.title} {self.writer} 추천 by {self.username}'

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    url = "https://www.yes24.com/Product/Category/BestSeller?categoryNumber=001&pageNumber=1&pageSize=24"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    yes_data = []
    bestList = soup.select('.bSGoodsSecArea #yesBestList .itemUnit')

    for best in bestList:
        title_tag = best.select_one('.item_info .info_row.info_name .gd_name')
        writer_tag = best.select_one('.item_info .info_row.info_pubGrp .info_auth a')
        img_tag = best.select_one('.item_img .img_canvas .img_item .img_grp .img_bdr .lazy')
        
        if title_tag and writer_tag and img_tag:
            title = title_tag.text.strip()
            writer = writer_tag.text.strip()
            img_url = img_tag['data-original'] if 'data-original' in img_tag.attrs else img_tag['src']
            
            yes_data.append({
                'title': title,
                'writer': writer,
                'img_url': img_url,
            })

    return render_template('main.html', data=yes_data)




@app.route("/read/")
def read():
    read_list = Book.query.all()
    return render_template('read.html', data=read_list)

@app.route("/read/add_book/")
def add_book():
    # form에서 보낸 데이터 받아오기
    title_receive = request.args.get("title")
    writer_receive = request.args.get("writer")
    img_receive = request.args.get("img_url")

    #  데이터를 디비에 저장하기
    book = Book(title=title_receive, writer=writer_receive, img_url=img_receive)
    db.session.add(book)
    db.session.commit()
    return redirect(url_for('read', title=title_receive))

# 삭제
@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        title = book.title
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for('read'))


if __name__ == "__main__":
    app.run(debug=True)