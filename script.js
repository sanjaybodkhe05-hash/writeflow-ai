console.log("WriteFlow JS Loaded 🚀");

let speechRate = 1;
let wordsList = [];
let currentIndex = 0;
let isSpeaking = false;
let isPaused = false;

// 🔥 GUARANTEED BUTTON BINDING
window.onload = () => {
    console.log("WINDOW LOADED ✅");

    const uploadBtn = document.getElementById("uploadBtn");

    if (uploadBtn) {
        uploadBtn.onclick = uploadPDF;
        console.log("Upload button connected ✅");
    } else {
        console.log("Upload button NOT found ❌");
    }

    const slider = document.getElementById("speed");
    const display = document.getElementById("speedValue");

    if (slider && display) {
        slider.addEventListener("input", () => {
            speechRate = slider.value;
            display.innerText = slider.value + "x";
        });
    }
};

async function uploadPDF() {
    console.log("BUTTON CLICKED 🔥");

    const fileInput = document.getElementById("pdfFile");

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

        if (!response.ok) {
            console.error("Server error:", response.status);
            alert("Server error while uploading!");
            return;
        }

        const data = await response.json();

        if (!data || !data.text) {
            alert("No text received!");
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

// 🔥 SPEECH FUNCTIONS
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

// 🔥 SIGNUP FUNCTION
async function signup() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (!email || !password) {
        alert("Enter email & password!");
        return;
    }

    const formData = new FormData();
    formData.append("email", email);
    formData.append("password", password);

    try {
        const res = await fetch("/signup", {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        alert(data.message || data.error);

    } catch (err) {
        console.error(err);
        alert("Signup failed!");
    }
}

// 🔥 FIXED LOGIN FUNCTION (REAL API CALL)
async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (!email || !password) {
        alert("Enter email & password!");
        return;
    }

    const formData = new FormData();
    formData.append("email", email);
    formData.append("password", password);

    try {
        const res = await fetch("/login", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        console.log("LOGIN RESPONSE:", data);

        if (data.message) {
            alert(data.message);
        } else {
            alert(data.error);
        }

    } catch (err) {
        console.error(err);
        alert("Login failed!");
    }
}

// 🔥 GLOBAL ACCESS (IMPORTANT)
window.signup = signup;
window.login = login;
