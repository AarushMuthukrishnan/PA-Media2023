import os
import requests
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)

@app.route("/")
def home():
   return render_template('home.html')

@app.route("/todolist")
def todo():
    return render_template('todolist.html')

@app.route("/aboutme")
def aboutme():
    return render_template("aboutme.html")

headers = {
    "authorization": "e71c089456284f9cb1c2680f712766a2",
    "content-type": "application/json"
}

def upload_to_AssemblyAI(audio_file):

    transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
    upload_endpoint = 'https://api.assemblyai.com/v2/upload'

    print('uploading')
    upload_response = requests.post(
        upload_endpoint,
        headers=headers, data=audio_file
    )

    audio_url = upload_response.json()['upload_url']
    print('done')

    json = {
        "audio_url": audio_url,
        "auto_chapters": True
    }

    response = requests.post(transcript_endpoint, json=json, headers=headers)
    print(response.json())

    polling_endpoint = transcript_endpoint + "/" + response.json()['id']
    return polling_endpoint

def convertMillis(start_ms):
    seconds = int((start_ms / 1000) % 60)
    minutes = int((start_ms / (1000 * 60)) % 60)
    hours = int((start_ms / (1000 * 60 * 60)) % 24)
    btn_txt = ''
    if hours > 0:
        btn_txt += f'{hours:02d}:{minutes:02d}:{seconds:02d}'
    else:
        btn_txt += f'{minutes:02d}:{seconds:02d}'
    return btn_txt

@app.route('/meeting-minutes', methods=['GET', 'POST'])
def index():
    global polling_endpoint
    if request.method == 'POST':
        file = request.files['audio_file']
        if file:
            # Save the file to disk
            file.save('audio_file.mp3')

            # Process the file using your existing code
            with open('audio_file.mp3', 'rb') as f:
                uploaded_file = f.read()
            polling_endpoint = upload_to_AssemblyAI(uploaded_file)

            status = 'submitted'
            while status != 'completed':
                polling_response = requests.get(polling_endpoint, headers=headers)
                status = polling_response.json()['status']

                if status == 'completed':
                    # Process the response and display the meeting notes
                    chapters = polling_response.json()['chapters']
                    # ...

                    # Render the template with the meeting notes
                    return render_template('meeting_notes.html', chapters=chapters)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
