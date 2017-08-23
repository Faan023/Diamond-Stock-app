from diamond import app
from flask import Flask, render_template, json, request,redirect,session,jsonify
from flaskext.mysql import MySQL
# from werkzeug import generate_password_hash, check_password_hash
# from werkzeug.wsgi import LimitedStream
# import uuid
import os
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText




mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'mypassword'
app.config['MYSQL_DATABASE_DB'] = 'mydbname'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def main():
	return render_template('home.html')

# @app.route('/home')
# def home():
#     return render_template('home.html')

@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        return render_template('welcome.html')
    else:
        return render_template('signin.html')


@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _demCode = request.form['inputdemCode']
        _password = request.form['inputPassWord']
        

        
        # connect to mysql

        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_demCode,_password))
        #in my stored procedure it does not allow a registered
        #user to log in unless they had an invoice in the last 6 months
        data = cursor.fetchall()      


        if len(data) > 0:
            # if check_password_hash(data[0][3],_password):
            session['user'] = data[0][1]
            # session['key'] = data[0][2] wanted to use this at a later stage to determine
            # what kind of a user is logged in ex admin user or manager or salesforce member
            return redirect('/welcome')
            
        else:
            return render_template('error.html',error = 'Wrong Demonstrator code or Password.')
            

    except Exception as e:
        return render_template('error.html',error = 'Wrong Demonstrator code or Password.')
    finally:
        cursor.close()
        con.close()

@app.route('/showUserValidation')
def showUserValidation():
    return render_template ('uservalidation.html')

@app.route('/userValidation',methods=['POST','GET'])
def userValidation():
    try:
        _dem_code = request.form['inputdem_code']
        _cell_no = request.form['inputcell_no']
        _id_no = request.form['inputid_no']
        _password = request.form['inputResetPassword']

        if _dem_code and _cell_no  and _id_no  and _password:

            conn = mysql.connect()
            cursor = conn.cursor()

            if len(_dem_code) < 11 :
                return json.dumps("Please enter the dem code in the correct format!")

            if len(_cell_no) != 10:
                return json.dumps("Please enter a valid cellphone number!")


            if len(_id_no) != 13:
                return json.dumps("Please enter a valid ID number!")

            # _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_validate_user',(_dem_code,_cell_no,_id_no,_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps("Password changed succsesfully!")
                # return redirect('/showSignin') #I need the page to redirect after succsesfull user creation to /userHome or to /showSignIn
            else:
                return json.dumps(str(data[0]))

        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()

@app.route('/showSignUp/')
def showSignUp():
	return render_template('signup.html')


@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _dem_code = request.form['inputdem_code']
        _cell_no = request.form['inputcell_no']
        _id_no = request.form['inputid_no']
        _password = request.form['inputPassword']
        # _email = request.form['inputEmail']

        

        # validate the received values
        if _name and _dem_code and _cell_no  and _id_no  and _password:
            
            # All Good, let's call MySQL
            
            conn = mysql.connect()
            cursor = conn.cursor()

            if len(_dem_code) < 11 :
                return json.dumps("Please enter the dem code in the correct format!")

            if len(_cell_no) != 10:
                return json.dumps("Please enter a valid cellphone number!")


            if len(_id_no) != 13:
                return json.dumps("Please enter a valid ID number!")



            # _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser',(_name,_dem_code,_cell_no,_id_no,_password))
            # the stored procedure will not let a salesforce member with
            #a valid number register unless 
            # they had an invoice in the last 6 months
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps("User created succsesfully!")
                #  to do return redirect('/showSignin') #I need the page to redirect after succsesfull user creation to /userHome or to /showSignIn
            else:
                return json.dumps(str(data[0]))

        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()


@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')


@app. route('/welcome')
def welcome():
    if session.get('user'):
        return render_template('welcome.html', data = ('user','key'))
    else:
        return render_template('error.html',error = 'Unauthorized Access')
        

@app.route('/showSpecials')
def showSpecials():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("Select Pr_Code, Description, Price, Qty_left from specials where Available = '1' and Qty_left > 150")
        data = cursor.fetchall()
        return render_template("specials.html", data=data)


    except Exception as e:
        return (str(e))

    finally:
        cursor.close() 
        conn.close()

@app.route('/showSpares')
def showSpares():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("Select Processing_code, Description, Item, `Group`, Cataloque_Code, Price   from spares where Available = '1'")
        data = cursor.fetchall()
        return render_template("spares.html", data=data)


    except Exception as e:
        return (str(e))

    finally:
        cursor.close() 
        conn.close()


@app.route('/showDiamondLog')
def showDiamondLog():
    return render_template('diamondindex.html')

@app.route('/validateStaffLogin',methods=['POST'])
def validateStaffLogin():
    try:
        _user_name = request.form['inputUserName']
        _password = request.form['inputPassWord']

         # connect to mysql

        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validate_staff',(_user_name,_password))
        data = cursor.fetchall()      


        if len(data) > 0:
            # if check_password_hash(data[0][3],_password):
            session['user'] = str(data[0][1]) 
            session['type'] = str(data[0][6])
            return redirect('/welcome')
            # if session['type'] == 'admin':
            #     return redirect('/diamondAdmin')

            # else:
            #     return redirect('/diamondHome')
            
            # else:
            #     return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong User name code or Password.')
            

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()



@app.route('/showContact')
def showContact():
    return render_template('contact.html')

@app.route('/showJoin/')
def showJoin():
    return render_template('contact_join.html')


@app.route('/join',methods=['POST','GET'])
def join():
    try:
        name = request.form['inputname']
        id_no = request.form['inputId']
        tel_no = request.form['inputTelNo']
        email = request.form['inputEmail']
        area = request.form['inputArea']


        if name and id_no and tel_no and email and area:
 
 
            fromaddr = "myemailadress"
            toaddr = "tosomeemailadress"

            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = "New demonstrator application"
     

            body = ("I would like to join Tupperware as a demonstrator." +'\n'
                    + "My name is: " + name +'\n'
                    + "My ID number is: " + id_no +'\n'
                    + "My telephone number is: " + tel_no  +'\n'
                    + "My email adress is: " + email +'\n' 
                    + '\n'
                    + "The area that I live or work in is: " + area  +'\n' 
                    + '\n'                               
                    + "Thank you")

            msg.attach(MIMEText(body, 'plain'))
     
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(fromaddr, "mypassword")
            text = msg.as_string()
            return json.dumps("Thank you, your information was recorded, we will be in touch soon!")
            server.sendmail(fromaddr, toaddr, text)

       
        else:
            return render_template('error.html',error = 'Please enter all required fields.')
            

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:       
            server.quit()

@app.route('/showDefective')
def showDefective():
    return render_template('contact_defective.html')

@app.route('/defective',methods=['POST','GET'])
def defective():
    try:
        name = request.form['inputname']
        tel_no = request.form['inputTelNo']
        email = request.form['inputEmail']
        grr = request.form['inputGRR']
        add_info = request.form['inputAddInfo']


        if name and tel_no:

 
            fromaddr = "myemailadress"
            toaddr = "tosomeemailadress"

            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = "Defective Query"


            body = ("I have the following query about defectives." +'\n'
            + "My name is: " + name +'\n'
            + "My telephone number is: " + tel_no  +'\n'
            + "My email adress is: " + email +'\n' 
            + '\n'
            + "My GRR number is: " + grr +'\n'
            + add_info  +'\n' 
            + '\n'                               
            + "Thank you")

            msg.attach(MIMEText(body, 'plain'))
     
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(fromaddr, "mypassword")
            text = msg.as_string()           
            server.sendmail(fromaddr, toaddr, text)
            return json.dumps("Thank you, your information was recorded, we will be in touch soon!")

       
        else:
            return render_template('error.html',error = 'Please enter all required fields.')
            

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:       
            server.quit()

@app.route('/showSparesQuery')
def showSparesQuery():
    return render_template('contact_spares.html')

@app.route('/sparesQuery',methods=['POST','GET'])
def sparesQuery():
    try:
        name = request.form['inputname']
        tel_no = request.form['inputTelNo']
        email = request.form['inputEmail']
        mould = request.form['inputMouldNo']
        add_info = request.form['inputAddInfo']


        if name and tel_no :


            fromaddr = "my email adress"
            toaddr = "someemailadress"

            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = "Spares Query"


            body = ("I have the following query about Spares." +'\n'
            + "My name is: " + name +'\n'
            + "My telephone number is: " + tel_no  +'\n'
            + "My email adress is: " + email +'\n' 
            + '\n'
            + "Mould number is: " + mould +'\n'
            + add_info  +'\n' 
            + '\n'                               
            + "Thank you")

            msg.attach(MIMEText(body, 'plain'))
     
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(fromaddr, "mypassword")
            text = msg.as_string()           
            server.sendmail(fromaddr, toaddr, text)
            return json.dumps("Thank you, your information was recorded, we will be in touch soon!")

       
        else:
            return render_template('error.html',error = 'Please enter all required fields.')
            

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:       
            server.quit()
