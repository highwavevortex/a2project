# IMPORTS
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import mongoengine
import csv
import os
# import models
from mongoengine import Document, EmbeddedDocument
from mongoengine.connection import connect
from mongoengine.fields import StringField, EmailField, ListField, EmbeddedDocumentField, ImageField, DateTimeField

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

# SETUP
mongoengine.connect()
app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
DATA_UPLOAD_FOLDER = './data-uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATA_UPLOAD_FOLDER'] = DATA_UPLOAD_FOLDER

app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)

# EMBEDDED DOCUMENT MODELS
class SchoolAdmin(EmbeddedDocument):
    # roleID = 0
    username = StringField(required=True)

class Staff(EmbeddedDocument):
    # roleID = 1
    dob = StringField(required=True) # unsure if correct
    address = StringField(required=True)
    postcode = StringField(required=True)
    gender = StringField(required=True) # can pick from M/F/NB/O
    phoneNo = StringField(required=True)
    medicalNotes = StringField(required=True)

class Teacher(EmbeddedDocument):
    # roleID = 2
    dob = StringField(required=True) # unsure if correct
    address = StringField(required=True)
    postcode = StringField(required=True)
    gender = StringField(required=True) # can pick from M/F/NB/O
    phoneNo = StringField(required=True)
    medicalNotes = StringField(required=True)
    subjectsTeaching = StringField(required=True) # should pick from a list of subjects
    formTutoring = StringField(required=True) # should pick from a list of forms

class Student(EmbeddedDocument):
    # roleID = 3
    image = ImageField(required=False) # unsure if correct
    dob = StringField(required=True) # unsure if correct
    address = StringField(required=True)
    postcode = StringField(required=True)
    gender = StringField(required=True) # can pick from M/F/NB/O
    phoneNo = StringField(required=True)
    upn = StringField(required=True)
    fileOpened = DateTimeField(required=True)
    guardianName = StringField(required=True)
    guardianPhone = StringField(required=True)
    yearGroup = StringField(required=True) # pick from list of years
    form = StringField(required=True) # pick from list of forms
    # tutor = need to pull from list of teacher objectIDs 
    medicalNotes = StringField(required=True)
    # have list of subjects in an array?
    
# DOCUMENT MODELS
class User(Document):
    schoolName = StringField(required=True)
    forename = StringField(required=True)
    surname = StringField(required=True)
    email = EmailField(required=True)
    passwordHash = StringField(required=True)

    # Embedded Documents
    schoolAdmin = EmbeddedDocumentField(SchoolAdmin)
    staff = EmbeddedDocumentField(Staff)
    teacher = EmbeddedDocumentField(Teacher)
    student = EmbeddedDocumentField(Student)

# CHECK FOR ALLOWED FILE EXTENSION
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# SPLITS CSV AT COMMAS
def is_csv(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'csv'}

# STORE CSV DATA IN DATABASE
def store_data_in_db(filename, user_class):
    userArray = []
    with open(os.path.join(DATA_UPLOAD_FOLDER, filename)) as csvfile:   
        reader = csv.DictReader(csvfile)
        for row in reader:
            userArray.append(dict(row))
    for user in userArray:
        if user_class == 'staff':
            User(schoolName=user['schoolName'], \
                forename=user['forename'], \
                surname=user['surname'], \
                email=user['email'], \
                passwordHash=user['passwordHash'], \
                staff=Staff( \
                    dob=user['dob'], \
                    address=user['address'], \
                    postcode=user['postcode'], \
                    gender=user['gender'], \
                    phoneNo=user['phoneNo'], \
                    medicalNotes=user['medicalNotes']\
                ), \
                schoolAdmin=None, teacher=None, student=None).save()
            return True
        elif user_class == 'teacher':
            User(schoolName=user['schoolName'], \
                forename=user['forename'], \
                surname=user['surname'], \
                email=user['email'], \
                passwordHash=user['passwordHash'], \
                teacher=Teacher( \
                    dob=user['dob'], \
                    address=user['address'], \
                    postcode=user['postcode'], \
                    gender=user['gender'], \
                    phoneNo=user['phoneNo'], \
                    medicalNotes=user['medicalNotes'], \
                    subjectsTeaching=user['subjectsTeaching'], \
                    formTutoring=user['formTutoring']\
                ), \
                schoolAdmin=None, staff=None, student=None).save()
            return True

        elif user_class == 'student':
            User(schoolName=user['schoolName'], \
                forename=user['forename'], \
                surname=user['surname'], \
                email=user['email'], \
                passwordHash=user['passwordHash'], \
                student=Student( \
                    image=user['image'], \
                    dob=user['dob'], \
                    address=user['address'], \
                    postcode=user['postcode'], \
                    gender=user['gender'], \
                    phoneNo=user['phoneNo'], \
                    upn=user['upn'], \
                    fileOpened=user['fileOpened'], \
                    guardianName=user['guardianName'], \
                    guardianPhone=user['guardianPhone'], \
                    yearGroup=user['yearGroup'], \
                    form=user['form'], \
                    medicalNotes=user['medicalNotes']\
                ), \
                schoolAdmin=None, staff=None, teacher=None).save()
            return True
    # TODO convert user array into user objects and save to db - populate embedded documents

# ROUTES
@app.route('/registerSchool')
def register_school():
    userID = request.args.get('id', None)
    user = User.objects(id=userID).first()
    user.schoolAdmin = SchoolAdmin(username='ellie')
    user.save()
    return 'done'

# EXAMPLE ROUTE
@app.route('/test', methods=['POST']) # route + methods (client is POSTING data to server)
@jwt_required
def test(): # definition and parameters (currently empty)
    current_user_id = get_jwt_identity()
    # res = request.json # variable for json request
    user = User.objects(id=current_user_id).first()
    body = "Hello " +  user.forename # pulls data for 'name' and sets it to body with "Hello "
    return jsonify({"msg": body}), 200 # returns data and a 200 OK code

# ADMIN REGISTRATION ROUTE
@app.route('/register', methods=['POST'])
def register():
    res = request.json
    
    if res['schoolName'] and res['forename'] and res['surname'] and res['email'] and res['passwordHash']:
        User(schoolName = res['schoolName'],forename = res['forename'], surname = res['surname'], email = res['email'], passwordHash = res['passwordHash']).save()
        return jsonify({"msg": "User Registered"}), 200
    
    else:
        jsonify({"err": "Invalid request data to register"}), 400

# CURL TEST FOR REGISTRATION
'''
curl --request POST \
    --url http://localhost:5000/register \
    --header 'content-type: application/json' \
    --data '{
        "schoolName": "Uckfield College",
        "forename": "Ellie",
        "surname": "Anstis",
        "email": "14ecanstis@uckfield.college",
        "passwordHash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
    }'
'''

# GENERAL LOG IN ROUTE
@app.route('/login', methods=['POST'])
def login():
    res = request.json

    user = User.objects(email=res['email'], passwordHash=res['passwordHash']).first()
    print(user.passwordHash)

    if user: # is = type comparison
        access_token = create_access_token(identity=str(user.id))
        return jsonify({"token": access_token}), 200
    else:
        return jsonify({"err": "Incorrect Credentials"}), 400

# CURL TEST FOR LOGGING IN
'''
curl --request POST \
    --url http://localhost:5000/login \
    --header 'content-type: application/json' \
    --data '{
        "email": "14ecanstis@uckfield.college",
        "passwordHash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
    }'
'''

# ROUTE FOR UPLOADING DATA
@app.route('/upload-school-data/<schoolid>/<userclass>', methods=['POST']) # e.g. upload-school-data/fu38f0llnf/staff
@jwt_required
def upload_school_data(schoolid, userclass):
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first() # finds users in db with specified ID
    
    if user.schoolAdmin is None:
        return jsonify({"err": "Unotharised to use this endpoint"})
    
    if 'file' not in request.files:
        return jsonify({"err": "no file attached"})
    file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        
    if file.filename == '':
        return jsonify({"err": "files must have a file name"})

    if file and is_csv(file.filename):
        filename = secure_filename(file.filename) # gets rid of security attacks/threats
        file.save(os.path.join(app.config['DATA_UPLOAD_FOLDER'], filename)) # save to upload folder
        # TODO implement further logic - it is being implamented in the store_data_in_db function
        result = store_data_in_db(file.filename, userclass)
        if result == False:
            return jsonify({"err": "couldnt parse data"}), 500
        else:
            return jsonify({"msg": "data uploaded successfully"})

# CREATE SIGN UP LINK

'''
generate string of x amount of characters

create string such as http://classroom/login/<uniqueString>
'''

@app.route('/<schoolID>/register/<objectID>', methods=['GET', 'POST'])
def registerUser(schoolID, objectID, current_user_id):
    user = User.objects(id=current_user_id).first()
    passHash = request.set(passHash)
    user.password = passHash
    user.save()
    return jsonify({"msg": "user registered"})

# RUNS THE PROGRAM
if __name__ == "__main__":
    app.run(debug = True)