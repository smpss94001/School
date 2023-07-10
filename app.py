import re
import random
from typing_extensions import Self
from flask import Flask, request, template_rendered
from flask import url_for, redirect, flash
from flask import render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from numpy import identity, product
import random, string
from sqlalchemy import null
import cx_Oracle

## Oracle 連線
cx_Oracle.init_oracle_client(lib_dir="C:/Users/user/OneDrive/Desktop/instantclient-basic-windows.x64-21.3.0.0.0/instantclient_21_3") # init Oracle instant client 位置
connection = cx_Oracle.connect('Group14', 'group1444', cx_Oracle.makedsn('140.117.69.58', 1521, 'orcl')) # 連線資訊
cursor = connection.cursor()

## Flask-Login : 確保未登入者不能使用系統
app = Flask(__name__)
app.secret_key = 'Your Key'  
login_manager = LoginManager(app)
login_manager.login_view = 'login' # 假如沒有登入的話，要登入會導入 login 這個頁面

class User(UserMixin):
    
    pass

@login_manager.user_loader
def user_loader(userid):  
    user = User()
    user.id = userid
    cursor.prepare('SELECT * FROM USERS WHERE USERID = :id ')
    cursor.execute(None, {'id':userid})
    data = cursor.fetchone()
    user.role = data[0]
    user.name = data[1]
    return user 

# 主畫面
@app.route('/')
def index():
    return render_template('index.html')

# 登入頁面
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':

        account = request.form['account']
        password = request.form['password']

        cursor.prepare('SELECT ACCOUNT,PASSWORD,USERID FROM USERS WHERE ACCOUNT = :id ')
        cursor.execute(None, {'id': account})

        data = cursor.fetchall() # 抓去這個帳號的資料

        # 但是可能他輸入的是沒有的，所以下面我們 try 看看抓不抓得到
        try:
            DB_password = data[0][1] # true password
            user_id = data[0][2] # user_id

        # 抓不到的話 flash message '沒有此帳號' 給頁面
        except:
            flash('*沒有此帳號')
            return redirect(url_for('login'))

        if( DB_password == password ):
            user = User()
            user.id = user_id
            login_user(user)

            if( identity == 'user'):
                return redirect(url_for('selection'))
            else:
                return redirect(url_for('selection'))
        
        # 假如密碼不符合 則會 flash message '密碼錯誤' 給頁面
        else:
            flash('*密碼錯誤，請再試一次')
            return redirect(url_for('login'))

    
    return render_template('login.html')

# 系統選單
@app.route('/selection', methods=['GET', 'POST'])
@login_required # 使用者登入後才可以看
def selection():
 
    return render_template('selection.html', user=current_user.name)

#學生頁面
@app.route('/student', methods=['GET', 'POST'])
@login_required
def student():
    
    if 'student_delete' in request.values: #要刪除

        pid = request.values.get('student_delete')

        # 看看 RECORD 裡面有沒有需要這筆產品的資料
        cursor.prepare('SELECT * FROM STUDENT WHERE SID = :sid')
        cursor.execute(None, {'sid':pid})
        data = cursor.fetchone() #可以抓一筆就好了，假如有的話就不能刪除
        
        if(data != None):
            flash('faild')
        else:
            cursor.prepare('DELETE FROM STUDENT WHERE NAME = :id ')
            cursor.execute(None, {'id': pid})
            connection.commit() # 把這個刪掉

    elif 'student_edit' in request.values: #要修改
            pid = request.values.get('student_edit')
            return redirect(url_for('student_edit', pid=pid))

    student_data = student_d()
    
    return render_template('student.html', student_data=student_data, user=current_user.name)
    
def student_d():
    sql = 'SELECT * FROM STUDENT,CRAMSCHOOL_BRANCH WHERE STUDENT.BID = CRAMSCHOOL_BRANCH.BID ORDER BY student.sid'
    cursor.execute(sql)
    student_row = cursor.fetchall()
    student_data = []
    for i in student_row:
        student = {
            '學生學號': i[0],
            '學生姓名': i[5],
            '就讀國中': i[1],
            '錄取高中': i[2],
            '會考總分': i[12],
            '註冊日期': i[4],
            '註冊分部': i[14], 
        }
        student_data.append(student)
    return student_data

#老師頁面
@app.route('/teacher', methods=['GET', 'POST'])
@login_required # 使用者登入後才可以看
def teacher():
    
    if 'teacher_delete' in request.values: #要刪除

        tid = request.values.get('teacher_delete')
        # 看看 RECORD 裡面有沒有需要這個老師的資料
        cursor.prepare('SELECT * FROM TEACHER WHERE TID =:pid')
        cursor.execute(None, {'pid':tid})
        data = cursor.fetchone() #可以抓一筆就好了，假如有的話就不能刪除
        
        if(data != None):
            flash('faild')
        else:
            cursor.prepare('DELETE FROM TEACHER WHERE NAME = :id ')
            cursor.execute(None, {'id': tid})
            connection.commit() # 把這個刪掉

    elif 'teacher_edit' in request.values: #要修改
            pid = request.values.get('teacher_edit')
            return redirect(url_for('teacher_edit', pid=pid))

    teacher_data = teacher_d()

    return render_template('teacher.html', teacher_data=teacher_data, user=current_user.name)

def teacher_d():
    sql = 'SELECT * FROM TEACHER ORDER BY TID'
    cursor.execute(sql)
    teacher_row = cursor.fetchall()
    teacher_data = []
    for i in teacher_row:
        teacher = {
            '教師編號': i[0],
            '教師手機': i[1],
            '教師姓名': i[2],
            
        }
        teacher_data.append(teacher)
    return teacher_data

#課程頁面
@app.route('/course', methods=['GET', 'POST'])
@login_required
def course():
    
    if 'course_delete' in request.values: #要刪除

        pid = request.values.get('course_delete')

        # 看看有沒有需要這個課程的資料
        cursor.prepare('SELECT * FROM COURSE WHERE NAME = :name')
        cursor.execute(None, {'name':pid})
        data = cursor.fetchone() #可以抓一筆就好了，假如有的話就不能刪除
        
        if(data != None):
            flash('faild')
        else:
            cursor.prepare('DELETE FROM IS_ASSIGNED_TO WHERE CID = :pid ')
            cursor.execute(None, {'pid': pid})
            cursor.prepare('DELETE FROM COURSE WHERE CID = :pid ')
            cursor.execute(None, {'pid': pid})
            connection.commit() # 把這個刪掉

    elif 'course_edit' in request.values: #要修改
            pid = request.values.get('course_edit')
            return redirect(url_for('course_edit', pid=pid))

    course_data = course_d()
    
    return render_template('course.html', course_data=course_data, user=current_user.name)
    
def course_d():
    sql = 'SELECT * FROM COURSE, IS_ASSIGNED_TO,CLASSROOM WHERE COURSE.CID = IS_ASSIGNED_TO.CID AND CLASSROOM.ROOMID = IS_ASSIGNED_TO.ROOMID ORDER BY COURSE.cid'
    cursor.execute(sql)
    course_row = cursor.fetchall()
    course_data = []
    for i in course_row:
        course = {
            '課程編號': i[0],
            '課程名稱': i[2],
            '教室編號': i[3],
            '教室名稱': i[7],
            
        }
        course_data.append(course)
    return course_data

@app.route('/classroom', methods=['GET', 'POST'])
@login_required
def classroom():  
    
    classroom_data = classroom_d()
    
    return render_template('classroom.html', classroom_data=classroom_data, user=current_user.name)
    
def classroom_d():
    sql = 'SELECT * FROM COURSE, IS_ASSIGNED_TO,CLASSROOM, cramschool_branch WHERE COURSE.CID = IS_ASSIGNED_TO.CID AND CLASSROOM.ROOMID = IS_ASSIGNED_TO.ROOMID AND COURSE.BID = cramschool_branch.bid'
    cursor.execute(sql)
    classroom_row = cursor.fetchall()
    classroom_data = []
    for i in classroom_row:
        classroom = {
            '課程代號': i[0],
            '教室代號': i[3],
            '分部代號': i[1],
            '分部名稱': i[10],
            '分部地址': i[11],
            
        }
        classroom_data.append(classroom)
    return classroom_data


# 學生修改頁面
@app.route('/student_edit', methods=['GET', 'POST'])
@login_required
def student_edit():

    if request.method == 'POST':
        pid = request.values.get('pid')
        new_name = request.values.get('name')
        new_price = request.values.get('score')
        new_junior = request.values.get('junior')
        new_senior = request.values.get('senior')
        new_branch = request.values.get('branch')
        cursor.prepare('UPDATE STUDENT SET NAME=:name, TOTAL=:score ,JUNIORSCHOOL =:junior, HIGHSCHOOL =:senior,BID = :branch WHERE SID=:pid')
        cursor.execute(None, {'name':new_name, 'score':new_price,'pid':pid,'junior':new_junior,'senior':new_senior,'branch':new_branch })
        connection.commit()
        
        return redirect(url_for('student'))

    else:
        student = show_info()
        return render_template('student_edit.html', data= student)


def show_info():
    pid = request.args['pid']
    cursor.prepare('SELECT * FROM STUDENT WHERE SID = :id ')
    cursor.execute(None, {'id': pid})

    data = cursor.fetchone() #password
    pname = data[5]
    price = data[12]
    junior = data[1]
    senior = data[2]
    branch = data[3]
    date = data[4]

    student = {
        '學生學號': pid,
        '學生姓名': pname,
        '就讀國中': junior,
        '錄取高中': senior,
        '註冊日期': date,
        '註冊分部': branch,
        '總分': price,
    }
    return student

# 學生新增頁面
@app.route('/student_add', methods=['GET', 'POST'])
def student_add():

    if request.method == 'POST':
    
        cursor.prepare('SELECT * FROM STUDENT WHERE SID=:pid')
        data = ""

        while ( data != None): #裡面沒有才跳出回圈

            number = str(random.randrange( 1000000000, 9000000000))
            pid = number #隨機編號
            cursor.execute(None, {'pid':pid})
            data = cursor.fetchone()
            
        cursor.prepare('SELECT * FROM STUDENT WHERE SDATE=:sdate')
        student1 = ""

        while ( student1 != None): #裡面沒有才跳出回圈

            number1 = datetime.utcnow()
            s_date = number1 #隨機編號
            cursor.execute(None, {'sdate':s_date})
            student1 = cursor.fetchone()
        new_name = request.values.get('name')
        new_score = request.values.get('score')
        new_junior = request.values.get('junior')
        new_senior = request.values.get('senior')
        new_branch = request.values.get('branch')
        s_ch = request.values.get('ch')
        s_eng = request.values.get('eng')
        s_math = request.values.get('math')
        s_sci = request.values.get('sci')
        s_so = request.values.get('so')
        s_com = request.values.get('com')

        cursor.prepare('INSERT INTO STUDENT VALUES (:pid,:junior,:senior,:branch,:sdate,:name,:ch,:eng,:math,:sci,:so,:com,:score)')
        cursor.execute(None, {'pid':pid,'name':new_name,'score':new_score,'junior':new_junior,'senior':new_senior,'branch':new_branch,'sdate':s_date,'ch':s_ch,'eng':s_eng,'math':s_math,'sci':s_sci,'so':s_so,'com':s_com})
        connection.commit()

        return redirect(url_for('student'))

    return render_template('student_add.html')


# 老師修改頁面
@app.route('/teacher_edit', methods=['GET', 'POST'])
@login_required
def teacher_edit():

    if request.method == 'POST':
        pid = request.values.get('pid')
        new_name = request.values.get('name')
        new_phone = request.values.get('phone')
        cursor.prepare('UPDATE TEACHER SET PHONE=:phone ,NAME = :name WHERE TID=:pid')
        cursor.execute(None, {'name':new_name, 'phone':new_phone,'pid':pid})
        connection.commit()
        
        return redirect(url_for('teacher'))

    else:
        teacher = show_info_teacher()
        return render_template('teacher_edit.html', data_t=teacher)
    
def show_info_teacher():
    pid = request.args['pid']
    cursor.prepare('SELECT * FROM TEACHER WHERE TID = :id ')
    cursor.execute(None, {'id': pid})

    data = cursor.fetchone() #password
    
    phone = data[1]
    name = data[2]
    
    teacher = {
        '教師編號': pid,
        '教師手機': phone,
        '教師姓名': name
    }
    return teacher

# 老師新增頁面
@app.route('/teacher_add', methods=['GET', 'POST'])
def teacher_add():

    if request.method == 'POST':
    
        cursor.prepare('SELECT * FROM TEACHER WHERE TID=:pid')
        data = ""

        while ( data != None): #裡面沒有才跳出回圈

            number = str(random.randrange( 1000000000, 9000000000))
            pid = number #隨機編號
            cursor.execute(None, {'pid':pid})
            data = cursor.fetchone()
            
            
        new_name = request.values.get('name')
        new_phone = request.values.get('phone')
        
        cursor.prepare('INSERT INTO TEACHER VALUES (:pid,:phone,:name)')
        cursor.execute(None, {'pid':pid,'phone':new_phone,'name':new_name})
        connection.commit()

        return redirect(url_for('teacher'))

    return render_template('teacher_add.html')

# 課程修改頁面
@app.route('/course_edit', methods=['GET', 'POST'])
@login_required
def course_edit():

    if request.method == 'POST':
        pid = request.values.get('pid')
        new_cname = request.values.get('name')
        new_roomid = request.values.get('roomid')
  
        cursor.prepare('UPDATE COURSE SET NAME =:name WHERE CID = :pid')
        cursor.execute(None, {'pid':pid,'name':new_cname})
        cursor.prepare('UPDATE IS_ASSIGNED_TO SET ROOMID =:roomid WHERE CID = :pid')
        cursor.execute(None, {'pid':pid,'roomid':new_roomid})

        connection.commit()
        
        return redirect(url_for('course'))

    else:
        course = show_info_course()
        return render_template('course_edit.html', data_c=course)
    
def show_info_course():
    pid = request.args['pid']
    cursor.prepare('SELECT * FROM (SELECT Course.cid , course.name,is_assigned_to.roomid FROM COURSE, IS_ASSIGNED_TO WHERE COURSE.CID = IS_ASSIGNED_TO.CID) WHERE CID = :id ')
    cursor.execute(None, {'id': pid})

    data = cursor.fetchone() #password
    
    cname = data[1]
    roomid = data[2]
    
    course = {
        '課程編號': pid,
        '課程名稱': cname,
        '教室編號': roomid,
    }
    return course

#老師情況
@app.route('/teacher_state', methods=['GET', 'POST'])
@login_required # 使用者登入後才可以看
def teacher_state():
    
    teacher_s = show_info_teacher_s()
    number = float(random.uniform( 5.0, 7.0))
    num2 = round(number,1)        
    
    return render_template('teacher_state.html', data_ts=teacher_s, user=current_user.name,num2=num2)

def show_info_teacher_s():
    pid = request.args['pid']
    cursor.prepare('SELECT NAME FROM COURSE,TEACHES WHERE COURSE.CID = TEACHES.CID AND TEACHES.TID = :id')
    cursor.execute(None, {'id': pid})

    data_ts = cursor.fetchone() #password
    sub = data_ts[0]
    
    teacher_s = {
        '科目': sub,    
    }
    return teacher_s

@app.route('/logout')  
def logout():

    logout_user()  
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.debug = True #easy to debug
    app.secret_key = "Your Key"
    app.run()

