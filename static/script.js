const recordButton = document.getElementById('record');
const stopButton = document.getElementById('stop');
const timerDisplay = document.getElementById('timer');

let mediaRecorder;
let audioChunks = [];
let startTime;

// Function to format time for the timer display
function formatTime(time) {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

// Start recording when the record button is clicked
recordButton.addEventListener('click', () => {
    audioChunks = []; // Reset audio chunks
    navigator.mediaDevices.getUserMedia({ audio: true })  // Remove sampleRate for testing
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' }); // Using a supported MIME type
            mediaRecorder.start();

            // Start timer display
            startTime = Date.now();
            let timerInterval = setInterval(() => {
                const elapsedTime = Math.floor((Date.now() - startTime) / 1000);
                timerDisplay.textContent = formatTime(elapsedTime);
            }, 1000);

            mediaRecorder.ondataavailable = e => {
                audioChunks.push(e.data);
            };

            mediaRecorder.onstop = () => {
                clearInterval(timerInterval); // Clear the timer
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' }); // Keep as webm for upload
                const formData = new FormData();
                formData.append('audio_data', audioBlob, 'recorded_audio.webm'); // Use webm extension

                // Fetch API to upload audio
                fetch('/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    console.log('Audio uploaded successfully');
                    location.reload(); // Refresh the page
                })
                .catch(error => {
                    console.error('Error uploading audio:', error);
                });
            };
        })
        .catch(error => {
            console.error('Error accessing microphone:', error);
        });

    recordButton.disabled = true;  // Disable record button
    stopButton.disabled = false;    // Enable stop button
});

// Stop recording when the stop button is clicked
stopButton.addEventListener('click', () => {
    if (mediaRecorder) {
        mediaRecorder.stop(); // Stop the media recorder
    }

    recordButton.disabled = false; // Enable record button
    stopButton.disabled = true;     // Disable stop button
});

// Initially disable the stop button
stopButton.disabled = true;
