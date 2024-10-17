from flask import Flask, redirect, render_template, request, send_file, url_for, flash
from flask_mysqldb import MySQL
import matplotlib.pyplot as plt
import io
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired

app = Flask(__name__)
app.secret_key = 'many random bytes'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'MRAK#7899@yk'
app.config['MYSQL_DB'] = 'hudco'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/uploads' 

mysql = MySQL(app)

# PDF Upload Form Class
class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

@app.route('/')
def Index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM employee")
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', employee=data)

# Add employee route
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == "POST":
        emp_id = request.form['emp_id']
        name = request.form['name']
        department = request.form['department']
        designation = request.form['designation']
        salary = request.form['salary']
        phone = request.form['phone']
        gender = request.form['gender']
        experience = request.form['experience']
        education = request.form['education']
        work_hours = request.form['work_hours']
        bonus = request.form['bonus']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO employee (emp_id, name, department, designation, salary, phone, gender, experience_year, education, work_hours, bonus) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (emp_id, name, department, designation, salary, phone, gender, experience, education, work_hours, bonus))
        mysql.connection.commit()
        cur.close()

        flash("Data Inserted Successfully!")
        return redirect(url_for('Index'))  
    return render_template('add_employee.html') 

# Edit employee
@app.route('/edit_employee/<int:emp_id>', methods=['GET', 'POST'])
def edit_employee(emp_id):
    if request.method == 'POST':
        # Handle form submission
        name = request.form['name']
        department = request.form['department']
        designation = request.form['designation']
        salary = request.form['salary']
        phone = request.form['phone']
        gender = request.form['gender']
        experience = request.form['experience']
        education = request.form['education']
        work_hours = request.form['work_hours']

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE employee 
            SET name=%s, department=%s, designation=%s, salary=%s, phone=%s, gender=%s, experience_year=%s, education=%s, work_hours=%s 
            WHERE emp_id=%s
        """, (name, department, designation, salary, phone, gender, experience, education, work_hours, emp_id))
        mysql.connection.commit()
        cur.close()
        flash("Employee details updated successfully!")
        return redirect(url_for('Index'))

    # Fetch employee data
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM employee WHERE emp_id = %s", (emp_id,))
    emp = cur.fetchone()
    cur.close()

    return render_template('edit_employee.html', emp=emp)





# Delete employee
@app.route('/delete_employee/<int:emp_id>', methods=['GET'])
def delete_employee(emp_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM employee WHERE emp_id = %s", (emp_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('Index'))


# -------------------------------------Graph chart -------------------------------
# Bar Chart (Salary by Department)
@app.route('/bar')
def bar_chart():
    # Connect to MySQL 
    cur = mysql.connection.cursor()
    cur.execute("SELECT department, SUM(salary) FROM employee GROUP BY department")
    data = cur.fetchall()
    cur.close()

    # Separate the data into departments and their total salaries
    departments = [row[0] for row in data]  
    salaries = [row[1] for row in data]  

    # Create the pie chart
    plt.figure(figsize=(8, 6)) 
    plt.pie(salaries, labels=departments, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    plt.axis('equal')  
    plt.title("Total Salary by Department (Pie Chart)")

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)  

    return send_file(img, mimetype='image/png')

# Pie Chart (Gender Distribution)
@app.route('/gender_pie')
def gender_pie():
    # Connect to MySQL and fetch gender counts based on department
    cur = mysql.connection.cursor()
    cur.execute("SELECT department, gender, COUNT(*) FROM employee GROUP BY department, gender")
    data = cur.fetchall()
    cur.close()

    # Prepare data for the histogram
    departments = list(set(row[0] for row in data))  # Unique departments
    male_counts = [0] * len(departments)
    female_counts = [0] * len(departments)

    # Fill the counts for each gender
    for row in data:
        department, gender, count = row
        if gender == 'Male':
            male_counts[departments.index(department)] = count
        elif gender == 'Female':
            female_counts[departments.index(department)] = count

    # Create the histogram
    width = 0.35  # Width of the bars
    x = range(len(departments))

    plt.figure(figsize=(10, 7.4))
    plt.bar(x, male_counts, width, label='Male', color='blue')
    plt.bar([p + width for p in x], female_counts, width, label='Female', color='pink')

    plt.xlabel('Departments')
    plt.ylabel('Number of Employees')
    plt.title('Gender Distribution by Department')
    plt.xticks([p + width / 2 for p in x], departments)  # Center x-ticks
    plt.legend()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype='image/png')


# Bar Chart (Work Hours by Department)
@app.route('/work_hours')
def work_hours_chart():
    cur = mysql.connection.cursor()
    cur.execute("SELECT department, SUM(work_hours) FROM employee GROUP BY department")
    data = cur.fetchall()
    cur.close()

    departments = [row[0] for row in data]
    work_hours = [row[1] for row in data]

    plt.figure(figsize=(8, 6))
    plt.bar(departments, work_hours, color='skyblue')
    plt.xlabel("Departments")
    plt.ylabel("Total Work Hours")
    plt.title("Total Work Hours by Department")

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return send_file(img, mimetype='image/png')

# Line Chart (Bonus by Department)
@app.route('/bonus_line')
def bonus_line_chart():
    cur = mysql.connection.cursor()
    cur.execute("SELECT department, SUM(bonus) FROM employee GROUP BY department")
    data = cur.fetchall()
    cur.close()

    departments = [row[0] for row in data]
    bonuses = [row[1] for row in data]

    plt.figure(figsize=(8, 6))
    plt.plot(departments, bonuses, marker='o', linestyle='-', color='blue')
    plt.xlabel("Departments")
    plt.ylabel("Total Bonus")
    plt.title("Total Bonus by Department (Line Chart)")
    plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return send_file(img, mimetype='image/png')

@app.route('/charts')
def graph_page():
    return render_template('graph.html')

# Upload File Route
@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
        flash('File has been uploaded successfully!', 'success')
        return redirect(url_for('upload_file'))
    
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('file_upload.html', form=form, files=uploaded_files)

if __name__ == "__main__":
    app.run(debug=True)
