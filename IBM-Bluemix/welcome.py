# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from flask import Flask, jsonify,request,make_response,render_template
from cloudant.client import Cloudant
import hashlib,time
from cloudant.error import CloudantException
from base64 import b64encode
app = Flask(__name__)

#authorization
username=[USERNAME],
password= [PASSWPRD],
host= [HOST],
port= 443,
url=[]
#connection
client = Cloudant(username, password, url=url)
client.connect()

#create database
database = None

try:
    database = client['dba']  # opening database
except:
    pass

if (database == None):
    database = client.create_database('dba')

@app.route('/')
def home():
    return render_template('index.html')

#upload
@app.route('/uploads', methods=['POST'])
def upload():
    file = request.files['file']
    filename = file.filename
    file_content = file.read()
    size=len(file_content)
    hasher = hashlib.sha1(file_content)
    hash_value = hasher.hexdigest()

    client.connect()

    session = client.session()
    latest_ver = 0
    database = client['dba']
    end_point = '{0}/{1}'.format(client.server_url, 'database/_all_docs')
    params = {'include_docs': 'true'}
    response = client.r_session.get(end_point, params=params)

    for each_file in database:
        if filename == each_file['f_upload']:
            if latest_ver < each_file['version']:
                latest_ver = each_file['version']
                latest_doc = each_file

    from datetime import datetime
    timestr = str(datetime.now())
    data = {
        'f_upload': filename,
        'f_Size':size,
        'f_hashval': hash_value,
        'f_content': file_content,
        'version': latest_ver + 1,
        'f_modified': timestr
    }
    if latest_ver == 0:
        doc = database.create_document(data)
    else:
        if latest_doc['f_hashval'] == hash_value:
            print ("File already exists \n")
        else:
            doc = database.create_document(data)

    return app.send_static_file('index.html')




      # uploaded_file_content = b64encode(file.read())
    # data = {'file_name': file_name,
    #          '_attachments': {file_name : {'data': uploaded_file_content}}}
    # database.create_document(data)


@app.route('/delete', methods=['POST'])
def delete():
    client.connect()
    session = client.session()
    latest_ver = 0
    database = client['dba']

    filename = request.form['filename']
    #fileversion = request.form['fileversion']
    for each_file in database:
        if filename == each_file['f_upload'] :
                #and str(fileversion) == str(each_file['version']):
            each_file.delete()
            msg = "File Deleted Successfully"
            return msg
    #         return """
    #         <!doctype html>
    #         <title>File Deleted</title>
    #         <h1>%s</h1>
    #
    #         """ % msg
    # msg = "File Name or version mismatch"
    # return """
    #         <!doctype html>
    #         <title>File Delete Failed</title>
    #         <h1>%s</h1>
    #
    #         """ % msg


@app.route('/list', methods=['GET'])
def getList():
    temp= ''
    client.connect()
    session = client.session()
    database = client['dba']
    for each_file in database:
     temp += str(each_file['f_upload']) + '  ' + str(each_file['f_Size']) + '  '+ str(each_file['f_modified'])+ '<br>'
     return temp
# #download
# @app.route('/download', methods=['POST'])
# def download():
# 	file_name = request.form['filename']
# 	for document in database:
# 		if (document['file_name'] == file_name):
# 			file = document.get_attachment(file_name, attachment_type='binary')
# 			response = make_response(file)
# 			response.headers["Content-Disposition"] = "attachment; filename=%s"%file_name
# 			return response
# 		else:
# 			response = 'File not found'
# 	return response
@app.route('/myapp')
def WelcomeToMyapp():
    return 'Welcome again to my app running on Bluemix!'

@app.route('/api/people')
def GetPeople():
    list = [
        {'name': 'John', 'age': 28},
        {'name': 'Bill', 'val': 26}
    ]
    return jsonify(results=list)

@app.route('/api/people/<name>')
def SayHello(name):
    message = {
        'message': 'Hello ' + name
    }
    return jsonify(results=message)

port = os.getenv('PORT', '8080')
if __name__ == "__main__":
	#app.run()
    app.run(host='0.0.0.0', port=int(port))