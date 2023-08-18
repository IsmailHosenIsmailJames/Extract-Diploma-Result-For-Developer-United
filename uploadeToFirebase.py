#################### Firebase database #######################################
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Fetch the service account key JSON file contents
cred = credentials.Certificate('C:/Users/mdism/extract diploma result/developersunited-firebase-adminsdk-jx3em-7880ffac1c.json')
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {'databaseURL': "https://developersunited-default-rtdb.asia-southeast1.firebasedatabase.app/"})
