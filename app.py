from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os


# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database initialization
db = SQLAlchemy(app)

# Marshmallow initialization
ma = Marshmallow(app)


# Hospital Class/Model
class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    foundation_year = db.Column(db.Integer, nullable=False)
    adress = db.Column(db.String(100), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    departments = db.relationship('Department', cascade='all,delete', backref='Hospital')

    def __init__(self, name, foundation_year, adress, capacity):
        self.name = name
        self.foundation_year = foundation_year
        self.adress = adress
        self.capacity = capacity


# Hospital Schema
class HospitalSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'foundation_year', 'adress', 'capacity')


# Hospital schema initialization
hospital_schema = HospitalSchema()
hospitals_schema = HospitalSchema(many=True)


# Create a Hospital
@app.route('/hospital', methods=['POST'])
def app_hospital():
    name = request.json['name']
    foundation_year = request.json['foundation_year']
    adress = request.json['adress']
    capacity = request.json['capacity']

    error_message1 = 'The foundation year must be between 1500 and 2020'
    if ((foundation_year > 2020) or (foundation_year < 1500)):
        return error_message1
    error_message2 = 'The capacity must be between 1 and 5000'
    if ((capacity > 5000) or (capacity < 1)):
        return error_message2
    error_message3 = 'Hospital with this adress already exists'
    hospitals = Hospital.query.all()
    for h in hospitals:
        if (h.adress == adress):
            return error_message3

    new_hospital = Hospital(name, foundation_year, adress, capacity)

    db.session.add(new_hospital)
    db.session.commit()

    return hospital_schema.jsonify(new_hospital)


# Get All Hospitals
@app.route('/hospital', methods=['GET'])
def get_hospitals():
    all_hospitals = Hospital.query.all()
    result = hospitals_schema.dump(all_hospitals)
    return jsonify(result.data)


# Get Single Hospital
@app.route('/hospital/<id>', methods=['GET'])
def get_hospital(id):
    hospital = Hospital.query.get(id)
    return hospital_schema.jsonify(hospital)


# Update a Hospital
@app.route('/hospital/<id>', methods=['PUT'])
def update_hospital(id):
    hospital = Hospital.query.get(id)

    name = request.json['name']
    foundation_year = request.json['foundation_year']
    adress = request.json['adress']
    capacity = request.json['capacity']

    error_message1 = 'The foundation year must be between 1500 and 2020'
    if ((foundation_year > 2020) or (foundation_year < 1500)):
        return error_message1
    error_message2 = 'The capacity must be between 1 and 5000'
    if ((capacity > 5000) or (capacity < 1)):
        return error_message2
    error_message3 = 'Hospital with this adress already exists'
    hospitals = Hospital.query.all()
    for h in hospitals:
        if (h.adress == adress):
            return error_message3

    hospital.name = name
    hospital.foundation_year = foundation_year
    hospital.adress = adress
    hospital.capacity = capacity

    db.session.commit()

    return hospital_schema.jsonify(hospital)


# Delete Hospital
@app.route('/hospital/<id>', methods=['DELETE'])
def delete_hospital(id):
    hospital = Hospital.query.get(id)
    db.session.delete(hospital)
    db.session.commit()
    return hospital_schema.jsonify(hospital)


# Department Class/Model
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    doctors = db.relationship('Doctor', cascade='all,delete', backref='Department')

    def __init__(self, name, hospital_id):
        self.name = name
        self.hospital_id = hospital_id


# Department Schema
class DepartmentSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'hospital_id')


# Department schema initialization
department_schema = DepartmentSchema()
departments_schema = DepartmentSchema(many=True)


# Create a Department
@app.route('/department', methods=['POST'])
def app_department():
    name = request.json['name']
    hospital_id = request.json['hospital_id']

    new_department = Department(name, hospital_id)

    db.session.add(new_department)
    db.session.commit()

    return department_schema.jsonify(new_department)


# Get All Departments
@app.route('/department', methods=['GET'])
def get_departments():
    all_departments = Department.query.all()
    result = departments_schema.dump(all_departments)
    return jsonify(result.data)


# Get Single Department
@app.route('/department/<id>', methods=['GET'])
def get_department(id):
    department = Department.query.get(id)
    return department_schema.jsonify(department)


# Update a Department
@app.route('/department/<id>', methods=['PUT'])
def update_department(id):
    department = Department.query.get(id)

    name = request.json['name']
    hospital_id = request.json['hospital_id']

    department.name = name
    department.hospital_id = hospital_id

    db.session.commit()

    return department_schema.jsonify(department)


# Delete Department
@app.route('/department/<id>', methods=['DELETE'])
def delete_department(id):
    department = Department.query.get(id)
    db.session.delete(department)
    db.session.commit()
    return department_schema.jsonify(department)


# Treatment Table
Treatment = db.Table('Treatment',
    db.Column('doctor_id', db.Integer, db.ForeignKey('doctor.id')),
    db.Column('patient_id', db.Integer, db.ForeignKey('patient.id'))
)


# Doctor Class/Model
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_year = db.Column(db.Integer, nullable=False)
    start_year = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    patients = db.relationship('Patient', cascade='all,delete', secondary=Treatment)

    def __init__(self, name, birth_year, start_year, gender, department_id):
        self.name = name
        self.birth_year = birth_year
        self.start_year = start_year
        self.gender = gender
        self.department_id = department_id


# Doctor Schema
class DoctorSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'birth_year', 'start_year', 'gender', 'department_id')


# Doctor schema initialization
doctor_schema = DoctorSchema()
doctors_schema = DoctorSchema(many=True)


# Create a Doctor
@app.route('/doctor', methods=['POST'])
def app_doctor():
    name = request.json['name']
    birth_year = request.json['birth_year']
    start_year = request.json['start_year']
    gender = request.json['gender']
    department_id = request.json['department_id']

    new_doctor = Doctor(name, birth_year, start_year, gender, department_id)

    db.session.add(new_doctor)
    db.session.commit()

    return doctor_schema.jsonify(new_doctor)


# Get All Doctors
@app.route('/doctor', methods=['GET'])
def get_doctors():
    all_doctors = Doctor.query.all()
    result = doctors_schema.dump(all_doctors)
    return jsonify(result.data)


# Get Single Doctor
@app.route('/doctor/<id>', methods=['GET'])
def get_doctor(id):
    doctor = Doctor.query.get(id)
    return doctor_schema.jsonify(doctor)


# Update a Doctor
@app.route('/doctor/<id>', methods=['PUT'])
def update_doctor(id):
    doctor = Doctor.query.get(id)

    name = request.json['name']
    birth_year = request.json['birth_year']
    start_year = request.json['start_year']
    gender = request.json['gender']
    department_id = request.json['department_id']

    doctor.name = name
    doctor.birth_year = birth_year
    doctor.start_year = start_year
    doctor.gender = gender
    doctor.department_id = department_id

    db.session.commit()

    return doctor_schema.jsonify(doctor)


# Delete Doctor
@app.route('/doctor/<id>', methods=['DELETE'])
def delete_doctor(id):
    doctor = Doctor.query.get(id)
    db.session.delete(doctor)
    db.session.commit()
    return doctor_schema.jsonify(doctor)


# Patient Class/Model
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_year = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(100), nullable=False)

    def __init__(self, name, birth_year, weight, height, gender):
        self.name = name
        self.birth_year = birth_year
        self.weight = weight
        self.height = height
        self.gender = gender


# Patient Schema
class PatientSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'birth_year', 'weight', 'height', 'gender')


# Patient schema initialization
patient_schema = PatientSchema()
patients_schema = PatientSchema(many=True)


# Create a Patient
@app.route('/patient', methods=['POST'])
def app_patient():
    name = request.json['name']
    birth_year = request.json['birth_year']
    weight = request.json['weight']
    height = request.json['height']
    gender = request.json['gender']

    new_patient = Patient(name, birth_year, weight, height, gender)

    db.session.add(new_patient)
    db.session.commit()

    return patient_schema.jsonify(new_patient)


# Get All Patients
@app.route('/patient', methods=['GET'])
def get_patients():
    all_patients = Patient.query.all()
    result = patients_schema.dump(all_patients)
    return jsonify(result.data)


# Get Single Patient
@app.route('/patient/<id>', methods=['GET'])
def get_patient(id):
    patient = Patient.query.get(id)
    return patient_schema.jsonify(patient)


# Update a Patient
@app.route('/patient/<id>', methods=['PUT'])
def update_patient(id):
    patient = Patient.query.get(id)

    name = request.json['name']
    birth_year = request.json['birth_year']
    weight = request.json['weight']
    height = request.json['height']
    gender = request.json['gender']

    patient.name = name
    patient.birth_year = birth_year
    patient.weight = weight
    patient.height = height
    patient.gender = gender

    db.session.commit()

    return patient_schema.jsonify(patient)


# Delete Patient
@app.route('/patient/<id>', methods=['DELETE'])
def delete_patient(id):
    patient = Patient.query.get(id)
    db.session.delete(patient)
    db.session.commit()
    return patient_schema.jsonify(patient)


# Run server
if __name__ == '__main__':
    app.run(debug=True)
