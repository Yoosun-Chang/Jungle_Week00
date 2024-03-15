from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
from flask_bcrypt import Bcrypt
import jwt
import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretKey'
app.config['BCRYPT_LEVEL'] = 10

SECRET_KEY = 'SPARTA'

bcrypt = Bcrypt(app)


client = MongoClient('mongodb+srv://sparta:jungle@cluster0.ehjqrgg.mongodb.net/?retryWrites=true&w=majority')

db = client.dbjungle

# db.jungle_person_test.delete_many({})

@app.route('/')
def home():
    token_receive = request.cookies.get('token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)
        return redirect(url_for('test'))
    except jwt.ExpiredSignatureError:
        return render_template('loginpage.html')
    except jwt.exceptions.DecodeError:
        return render_template('loginpage.html')

# msg = request.args.get("msg")
# return render_template('index.html', msg=msg)

@app.route('/registerpage', methods=['GET'])
def registerpage():
    return render_template('register.html')

@app.route('/trylogin', methods=['POST'])
def trylogin():
    id = request.form['id']
    if (db.jungle_person_test.find_one({"id": id }) == None):
        return jsonify({'result': 'no_id'})
    
    pwd = request.form['pwd']

    find_user = db.jungle_person_test.find_one({'id': id})
    is_same = bcrypt.check_password_hash(find_user['pwd_hash'],pwd)

    if (not is_same):
        return jsonify({'result': 'no_pwd'})
    
    payload = {
            'id': id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=300)
        }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    return jsonify({'result': 'success', 'token':  token})

@app.route('/register', methods=['POST'])
def register():
    id = request.form['id']
    duplicated_id = db.jungle_person_test.find_one({"id": id })
    if (duplicated_id != None):
        return jsonify({'result': 'duplicated_id'})
    
    pwd = request.form['pwd']
    pwd_hash = bcrypt.generate_password_hash(pwd)
    nickname = request.form['nickname']

    user = {'id': id, 'pwd_hash': pwd_hash, 'nickname': nickname}

    db.jungle_person_test.insert_one(user)

    return jsonify({'result': 'success'})

@app.route('/test')
def test():
    token_receive = request.cookies.get('token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.jungle_person_test.find_one({"id": payload['id']})
        return render_template('test.html', nickname=user_info["nickname"], id=payload['id'])
    except jwt.ExpiredSignatureError:
        return redirect(url_for('home'))
    except jwt.exceptions.DecodeError:
        return redirect(url_for('home'))
    
@app.route('/result', methods=['POST'])
def get_result():
    array = request.form.getlist('res[]')
    print(array)
    # 연산에 사용될 행렬
    operations = [
        [1, 2, 1, 1, -1, -1],
        [-1, -1, -1, -1, 2, 1],
        [2, -1, 1, -1, -1, 1],
        [1, 2, -1, -1, -1, -1],
        [1, -1, -1, -1, 0, 0],
        [1, 1, 0, 0, 1, 1],
        [1, 2, -1, -1, 1, 1],
        [1, 1, 1, -2, -1, -1]
    ]
    # 개발자들의 초기 값 설정
    developers = [0, 0, 0, 0, 0, 0]
    developer_numbers = [1, 2, 3, 4, 5, 6]  # 개발자 번호

    # 배열을 순회하면서 각 개발자들의 값을 조정
    for i, val in enumerate(array):
        operation = operations[i % len(operations)]  # 연산 행렬을 순환하도록 인덱스 계산
        if val == 'A':
            for j in range(len(developers)):
                developers[j] += operation[j]
        elif val == 'B':
            for j in range(len(developers)):
                developers[j] += operation[j] * (-1)  # 'B'의 경우 연산의 부호를 반전하여 적용

    # 결과 출력 및 최고 점수를 가진 개발자 찾기
    max_score_index = developers.index(max(developers))
    result_dev_number = developer_numbers[max_score_index]
    print(result_dev_number)

    token_receive = request.cookies.get('token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.jungle_person_test.find_one({"id": payload['id']})
        db.jungle_person_test.update_one({"_id": user_info["_id"]}, {"$set": {"result": result_dev_number}})
        return jsonify({'result': 'success', 'result_num': result_dev_number})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("home", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("home", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/dev<int:dev_num>')
def dev(dev_num):
    user = '정글러'
    token_receive = request.cookies.get('token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.jungle_person_test.find_one({"id": payload['id']})
        user = user_info['nickname']
        return render_template(f'dev{dev_num}.html', user = user)
    except jwt.ExpiredSignatureError:
        return render_template(f'dev{dev_num}.html', user = user)
    except jwt.exceptions.DecodeError:
        return render_template(f'dev{dev_num}.html', user = user)

@app.route('/chart')
def chart():
    developers = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
    jungler = db.jungle_person_test.find({'result': {"$gt": 0}})
    for i in jungler:
        developers[i['result']] += 1
        print(developers)
        
    return render_template('chart.html', developers = developers)

if __name__ == '__main__':  
    app.run('0.0.0.0',port=5000,debug=True)