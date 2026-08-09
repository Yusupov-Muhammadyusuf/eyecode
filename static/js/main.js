let mediaRecorder;
let audioChunks = [];
let isRecording = false;

const recordBtn = document.getElementById('recordBtn');
const transcriptionText = document.getElementById('transcriptionText');
const codeEditor = document.getElementById('codeEditor');
const languageSelect = document.getElementById('languageSelect');
const spokenLanguage = document.getElementById('spokenLanguage');
const consoleOutput = document.getElementById('consoleOutput');
const runCodeBtn = document.getElementById('runCodeBtn');

document.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && e.target.tagName !== 'TEXTAREA' && e.target.tagName !== 'SELECT') {
        e.preventDefault();
        toggleRecording();
    }
});

recordBtn.addEventListener('click', toggleRecording);

async function toggleRecording() {
    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                await sendAudioToBackend(audioBlob);
            };

            mediaRecorder.start();
            isRecording = true;
            recordBtn.innerHTML = `<i class="bi bi-stop-fill"></i> Stop Recording`;
            recordBtn.classList.replace('btn-outline-danger', 'btn-danger');
            transcriptionText.textContent = "Recording audio... Speak now...";
        } catch (err) {
            alert("Microphone permission denied or error occurred!");
            console.error(err);
        }
    } else {
        mediaRecorder.stop();
        isRecording = false;
        recordBtn.innerHTML = `<i class="bi bi-mic-fill"></i> Start Recording`;
        recordBtn.classList.replace('btn-danger', 'btn-outline-danger');
        transcriptionText.textContent = "Processing audio, please wait...";
    }
}

async function sendAudioToBackend(blob) {
    const formData = new FormData();
    formData.append('file', blob, 'voice_command.webm');
    formData.append('language', languageSelect.value);
    formData.append('spoken_language', spokenLanguage.value);

    try {
        const response = await fetch("/api/convert", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            transcriptionText.textContent = data.transcription;
            codeEditor.value = data.code;
            consoleOutput.textContent = "Code successfully generated!";
        } else {
            transcriptionText.textContent = "An error occurred.";
            consoleOutput.textContent = "Error: " + data.error;
        }
    } catch (err) {
        console.error(err);
        consoleOutput.textContent = "Server connection error!";
    }
}

runCodeBtn.addEventListener('click', async () => {
    const codeToRun = codeEditor.value;
    
    if (!codeToRun.trim()) {
        consoleOutput.textContent = "No code to execute!";
        return;
    }

    consoleOutput.textContent = ">>> Executing Code...\nPlease wait...";

    try {
        const response = await fetch("/api/run-code", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ code: codeToRun })
        });

        const result = await response.json();

        if (result.success) {
            consoleOutput.textContent = ">>> Executing Code:\n" + codeToRun + "\n\n--- Output ---\n" + result.output + "\n[Status: Execution Successful]";
        } else {
            consoleOutput.textContent = ">>> Executing Code:\n" + codeToRun + "\n\n--- Error ---\n" + result.output + "\n[Status: Execution Failed]";
        }
    } catch (err) {
        console.error(err);
        consoleOutput.textContent = "Failed to connect to the server for code execution.";
    }
});