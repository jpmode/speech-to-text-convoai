# Speech-to-Text with Sentiment Analysis

A Flask-based web application that enables users to record audio, replay the recorded audio, and generate a transcribed text file. The transcribed text undergoes sentiment analysis, categorizing it as positive, neutral, or negative.
> **Note:** For detailed instructions on deploying this application using Docker and Google Cloud Run, please refer to the [**Deployment Instructions**](DEPLOYMENT.md) page. 
## Tech Stack
- **Programming Language:** Python  
- **Framework:** Flask  
- **Machine Learning:** Vertex AI (Google Speech-to-Text, GenerativeModel for sentiment analysis)  
- **Deployment (Previously Hosted):** Docker, Google Cloud Run  
- **Cloud Storage:** Google Cloud Storage  
- **Environment Management:** Python dotenv  

## Features
- Record and replay user audio
- Transcribe speech into text
- Analyze sentiment of the transcribed text (Positive, Neutral, Negative)
- Runs locally on Flask (http://127.0.0.1:8080)

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/jpmode/speech-to-text-convoai.git
cd speech-to-text-convoai
