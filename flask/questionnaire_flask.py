from flask import Flask, render_template , request
import pandas as pd
from sqlalchemy import create_engine
import pymysql

app = Flask(__name__)

dict = {}

@app.route("/apply" ,  methods=['GET', 'POST'])

def index():

    if request.method == 'GET':
        userID = request.args.get('userID')   #?userID=123456789aabbcc
        dict['userID'] = userID

    if request.method == 'POST':
        dict['username'] = request.form.get('username')
        dict['gender'] = request.form.get('gender')
        dict['age'] = request.form.get('age')
        dict['height'] = request.form.get('height')
        dict['weight'] = request.form.get('weight')
        dict['exercise'] = request.form.get('exercise')
        dict['job'] = str(request.form.getlist('job'))  # 多選list
        dict['style'] = str(request.form.getlist('style'))
        print(dict)
        df = pd.DataFrame([dict])
        # connect = create_engine('mysql+pymysql://root:ceb102@18.183.16.220:3306/ceb102_project?charset=utf8mb4')
        # df.to_sql(name='會員資料', con=connect, if_exists='append',index=False)


        return render_template("thank.html")

    return render_template("questionnaire.html")



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)


