from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
from dotenv import load_dotenv 
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import storage

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Assign variables from environment
PROJECT_ID = os.getenv("PROJECT_ID")
BUCKET_NAME = os.getenv("BUCKET_NAME")
APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")

# Use the variables as before
app.secret_key = APP_SECRET_KEY

# Configure upload folders
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# save to google bucket
def upload_to_gcs(file, destination_blob_name):
    """Uploads a file to Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    # Reset the file stream to the beginning
    file.seek(0)
    
    # Upload file to GCS
    blob.upload_from_file(file, content_type=file.content_type)
    print(f"Uploaded {destination_blob_name} to GCS bucket {BUCKET_NAME}.")
    
    # Return the GCS URI for the uploaded file
    return f"gs://{BUCKET_NAME}/{destination_blob_name}"


# force delete local files in upload folder
@app.route('/clear', methods=['POST'])
def clear_files():
    folder = app.config['UPLOAD_FOLDER']
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    flash('All files cleared successfully.')
    return redirect('/')

@app.route('/', methods=['GET'])
def index():
    recorded_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.wav')]
    text_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.txt')]
    return render_template('index.html', recorded_files=recorded_files, text_files=text_files)

@app.route('/upload', methods=['POST'])
def upload_audio():
    print("Received request for upload") 
    print("Upload route accessed")  # Debug output to check if the route is hit

    # Check if the audio data is in the request
    if 'audio_data' not in request.files:
        print("No audio data found")  # Debug output
        flash('No audio data')
        return redirect(request.url)

    file = request.files['audio_data']
    
    # Check if the file has a name
    if file.filename == '':
        print("No selected file")  # Debug output
        flash('No selected file')
        return redirect(request.url)

    # If the file is present, save it
    if file:
        # Create a unique filename
        filename = datetime.now().strftime("%Y%m%d-%I%M%S%p") + '.wav'
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        print(f"file path {file_path}")

        # Upload to GCS directly
        gcs_uri = upload_to_gcs(file, filename)
        print(f"File uploaded to GCS: {gcs_uri}")

        # Process the file with Vertex AI (local processing instead of GCS upload)
        # vertexai_prompt(file_path, filename)
        vertexai_prompt(gcs_uri, filename)

        # Debug output to confirm the file is saved: 
        print(f"Saved file: {filename}")  

    return redirect('/')  # Redirect to the homepage after success

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        return "File not found", 404

# USING VERTEX AI FOR TRANSCRIPTION AND SENTIMENT:
vertexai.init(project='project03-convoai-mjeanpierre', location="us-central1")

model = GenerativeModel("gemini-1.5-flash-001")

# using model to transcribe audio and get sentiment
# saving output and posting to app using text file 
# Ensure the vertexai_prompt function is designed to accept the local file path


def vertexai_prompt(gcs_uri, local_filename):
    prompt = """
    Please provide an exact transcript for the audio, followed by sentiment analysis.

    Your response should follow the format:

    Text: USERS SPEECH TRANSCRIPTION

    Sentiment Analysis: positive|neutral|negative
    """
    # Make sure to include mime_type as "audio/wav"
    try:
        audio_file = Part.from_uri(gcs_uri, mime_type="audio/wav")
        contents = [audio_file, prompt]
        print(f"audio file: {audio_file}")
        response = model.generate_content(contents)
        print(response.text)
        
        # Save the transcript to a .txt file
        text_filename = os.path.splitext(local_filename)[0] + ".txt"
        text_path = os.path.join(app.config['UPLOAD_FOLDER'], text_filename)
        with open(text_path, 'w') as text_file:
            text_file.write(response.text)
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        


        
if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))  # Use the port from the environment or default to 8080
    app.run(host='0.0.0.0', port=port, debug=True)  # Listen on all interfaces (0.0.0.0)

