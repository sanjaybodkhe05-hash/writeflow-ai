console.log("WriteFlow JS Loaded 🚀");

let speechRate = 1;
let wordsList = [];
let currentIndex = 0;
let isSpeaking = false;
let isPaused = false;

document.addEventListener("DOMContentLoaded", () => {
    const slider = document.getElementById("speed");
    const display = document.getElementById("speedValue");

    slider.addEventListener("input", () => {
        speechRate = slider.value;
        display.innerText = slider.value + "x";
    });
});

async function uploadPDF() {
    const fileInput = document.getElementById("pdfFile");

    if (!fileInput || !fileInput.files.length) {
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

        if (!response.ok) {
            throw new Error("Upload failed");
        }

        const data = await response.json();

        if (!data.text) {
            throw new Error("No text received");
        }

        const words = data.text.split(/\s+/);

        document.getElementById("result").innerHTML = words
            .map(w => `<span class="word">${w}</span>`)
            .join(" ");

        wordsList = document.querySelectorAll(".word");

    } catch (err) {
        console.error(err);
        alert("Upload failed. Check backend!");
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
