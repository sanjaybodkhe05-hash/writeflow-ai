Java new :

console.log("WriteFlow JS Loaded 🚀");

let speechRate = 1;
let wordsList = [];
let currentIndex = 0;
let isSpeaking = false;
let isPaused = false;

document.addEventListener("DOMContentLoaded", () => {
    // 🔥 FIX 1: Upload button event binding
    const uploadBtn = document.getElementById("uploadBtn");
    if (uploadBtn) {
        uploadBtn.addEventListener("click", uploadPDF);
    }

    // Existing slider logic
    const slider = document.getElementById("speed");
    const display = document.getElementById("speedValue");

    if (slider && display) {
        slider.addEventListener("input", () => {
            speechRate = slider.value;
            display.innerText = slider.value + "x";
        });
    }
});

async function uploadPDF() {
    console.log("BUTTON CLICKED 🔥"); // 🔥 debug

    const fileInput = document.getElementById("pdfFile");

    // 🔥 FIX 2: safe check
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        alert("Please select a PDF first!");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        // 🔥 FIX 3: better error handling
        if (!response.ok) {
            console.error("Server response error:", response.status);
            alert("Server error while uploading!");
            return;
        }

        const data = await response.json();

        if (!data || !data.text) {
            alert("No text received from server!");
            return;
        }

        const words = data.text.split(/\s+/);

        document.getElementById("result").innerHTML = words
            .map(w => `<span class="word">${w}</span>`)
            .join(" ");

        wordsList = document.querySelectorAll(".word");

    } catch (err) {
        console.error("UPLOAD ERROR:", err);
        alert("Upload failed. Backend issue!");
    }
}

function speakText() {
    if (!wordsList.length) {
        alert("No text found!");
        return;
    }

    speechSynthesis.cancel();
    isSpeaking = true;
    isPaused = false;
    currentIndex = 0;

    readNext();
}

function readNext() {
    if (!isSpeaking || isPaused) return;
    if (currentIndex >= wordsList.length) return;

    wordsList.forEach(w => w.classList.remove("highlight"));

    const word = wordsList[currentIndex];
    word.classList.add("highlight");
    word.scrollIntoView({ behavior: "smooth", block: "center" });

    const utterance = new SpeechSynthesisUtterance(word.innerText);
    utterance.rate = speechRate;

    utterance.onend = () => {
        currentIndex++;
        readNext();
    };

    speechSynthesis.speak(utterance);
}

function pauseSpeech() {
    isPaused = true;
    speechSynthesis.pause();
}

function resumeSpeech() {
    isPaused = false;
    speechSynthesis.resume();
    if (!speechSynthesis.speaking) readNext();
}

function stopSpeech() {
    speechSynthesis.cancel();
    isSpeaking = false;
    isPaused = false;
    currentIndex = 0;

    wordsList.forEach(w => w.classList.remove("highlight"));
}
