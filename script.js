console.log("JS LOADED SUCCESSFULLY 🚀");

async function uploadPDF() {
    let fileInput = document.getElementById("pdfFile");
    let file = fileInput.files[0];

    if (!file) {
        alert("Please select a PDF first!");
        return;
    }

    let formData = new FormData();
    formData.append("file", file);

    try {
        let response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            alert("Error uploading PDF!");
            return;
        }

        let data = await response.json();

        let words = data.text.split(/\s+/);

        document.getElementById("result").innerHTML = words
            .map(word => `<span class="word">${word}</span>`)
            .join(" ");

    } catch (err) {
        alert("Server not running or CORS issue!");
        console.error(err);
    }
}

// 🔥 STATE
let isSpeaking = false;
let isPaused = false;
let speechRate = 1;
let currentIndex = 0;
let wordsList = [];
let selectedVoice = null;
let currentUtterance = null;

// 🔥 LOAD VOICES (SAFE)
function loadVoices() {
    let voices = speechSynthesis.getVoices();

    if (!voices.length) return;

    selectedVoice = voices.find(v =>
        v.lang === "en-IN" || v.name.includes("Indian")
    ) || voices[0];
}

speechSynthesis.onvoiceschanged = loadVoices;

// 🔥 INIT SLIDER
document.addEventListener("DOMContentLoaded", () => {
    let slider = document.getElementById("speed");
    let display = document.getElementById("speedValue");

    if (slider) {
        slider.addEventListener("input", () => {
            speechRate = slider.value;
            display.innerText = slider.value + "x";
        });
    }

    loadVoices();
});

// 🔥 START
function speakText() {
    let resultDiv = document.getElementById("result");
    wordsList = resultDiv.querySelectorAll(".word");

    if (!wordsList.length) {
        alert("No text to read!");
        return;
    }

    speechSynthesis.cancel();

    isSpeaking = true;
    isPaused = false;
    currentIndex = 0;

    readNext();
}

// 🔥 CORE ENGINE (FIXED)
function readNext() {
    if (!isSpeaking) return;
    if (isPaused) return;
    if (currentIndex >= wordsList.length) return;

    // clean previous highlight
    wordsList.forEach(w => w.classList.remove("highlight"));

    let word = wordsList[currentIndex];
    word.classList.add("highlight");

    word.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

    currentUtterance = new SpeechSynthesisUtterance(word.innerText);

    currentUtterance.voice = selectedVoice;
    currentUtterance.rate = parseFloat(speechRate);
    currentUtterance.pitch = 1;

    currentUtterance.onend = () => {
        currentIndex++;
        readNext();
    };

    speechSynthesis.speak(currentUtterance);
}

// 🔥 PAUSE (FIXED)
function pauseSpeech() {
    if (!isSpeaking) return;
    isPaused = true;
    speechSynthesis.pause();
}

// 🔥 RESUME (MAIN FIX)
function resumeSpeech() {
    if (!isSpeaking) return;

    if (speechSynthesis.paused) {
        isPaused = false;
        speechSynthesis.resume();
    } else {
        // safety fallback (prevents glitch)
        isPaused = false;
        readNext();
    }
}

// 🔥 STOP
function stopSpeech() {
    speechSynthesis.cancel();
    isSpeaking = false;
    isPaused = false;
    currentIndex = 0;

    wordsList.forEach(w => w.classList.remove("highlight"));
}