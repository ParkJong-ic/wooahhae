from pymongo import MongoClient
import jwt
import datetime
import hashlib
import certifi
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

client = MongoClient('mongodb+srv://test:sparta@cluster0.lucisbi.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=certifi.where())
db = client.wooahhae

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/pics"

SECRET_KEY = 'SPARTA'

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"email": payload["email"]})
        return render_template('main.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/main', methods=['GET'])
def main():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"email": payload["email"]})
        posts = list(db.posting.find({}, {'_id': False}))
        return render_template('main.html', user_info=user_info, posts=posts, name=user_info["name"])
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("main.html"))

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    email_receive = request.form['email_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'email': email_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'email': email_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '이메일/비밀번호가 일치하지 않습니다.'})

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    email_receive = request.form['email_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    name_receive = request.form['name_give']
    nickname_receive = request.form['nickname_give']
    tel_receive = request.form['tel_give']
    address_receive = request.form['address_give']
    doc = {
        "email": email_receive,
        "password": password_hash,
        "name": name_receive,
        "nickname": nickname_receive,
        "tel": tel_receive,
        "address": address_receive
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    email_receive = request.form['email_give']
    exists = bool(db.users.find_one({"email": email_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route("/posting", methods=["POST"])
def web_posting_post():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"email": payload["email"]})
        content_receive = request.form["content_give"]
        anonymous_receive = request.form['anonymous_give']
        writer_receive = request.form['writer_give']
        address_receive = request.form['address_give']
        file = request.files["file_give"]
        extension = file.filename.split('.')[-1]

        write_count = list(db.write_count.find({}, {'_id': False}))[0]['count'] + 1

        today = datetime.now()
        mytime = today.strftime('%Y년%m월%d일%H시%M분%S초')

        filename = f'file-{mytime}'

        save_to = f'static/pics/{filename}.{extension}'
        file.save(save_to)
        doc = {
            'num': write_count,
            'content': content_receive,
            'file': f'{filename}.{extension}',
            'anonymous': anonymous_receive,
            'writer': writer_receive,
            'address': address_receive
        }

        db.posting.insert_one(doc)
        db.write_count.update_one({'count': int(write_count - 1)}, {'$set': {'count': write_count}})
        return jsonify({"result": "success", 'msg': '포스팅 성공'})
        return render_template('main.html')
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("main.html"))

    return jsonify({'msg': '저장 완료!'})

# @app.route('/posting', methods=['GET'])
# def list():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         user_info = db.users.find_one({"email": payload["email"]})
#         return render_template('write.html', user_info=user_info)
#         post_list = list(db.posting.find({}, {'_id': True}))
#         return jsonify({'lists': post_list})
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("main.html"))

# 다시 짜야됨

@app.route('/write')
def write():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"email": payload["email"]})
        return render_template('write.html', user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("main.html"))

# @app.route('/detail')
# def detail():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         user_info = db.users.find_one({"email": payload["email"]})
#         return render_template('detail.html', user_info=user_info)
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("main.html"))


@app.route('/detail/<int:num>', methods=["GET"])
def web_detail_get(num):
    data = db.posting.find_one({'num': num}, {'_id': False})
    content = data['content']
    file = data['file']
    anonymous = data['anonymous']
    writer = data['writer']
    address = data['address']
    num = data['num']

    index = [content, file, anonymous, writer, address, num]

    # posts = list(db.posting.find({}, {"_id": False}))
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"email": payload["email"]})
        return render_template('detail.html', user_info=user_info, index=index, name=user_info["name"])
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("main.html"))

@app.route("/detail_post", methods=["POST"])
def web_comment_post():
    num_receive = request.form['num_give']
    comment_receive = request.form['comment_give']
    doc = {
        'num': num_receive,
        'comment': comment_receive
           }
    db.comment.insert_one(doc)
    return jsonify({'msg': '입력 완료!'})

@app.route("/detail", methods=["GET"])
def web_comment_get():
    comments = list(db.comment.find({}, {'_id': False}))
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return jsonify({"comments": comments})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("main.html"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
