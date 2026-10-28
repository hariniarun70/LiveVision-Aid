const video = document.getElementById("video");
const status = document.getElementById("status");
const startBtn = document.getElementById("startBtn");

let audioEnabled = false;

// 🧠 memory
let lastCommand = "";
let lastTime = 0;
const COOLDOWN = 2000; // fast updates

// 🎥 BACK CAMERA
navigator.mediaDevices.getUserMedia({
    video: { facingMode: { ideal: "environment" } }
})
.then(stream => video.srcObject = stream)
.catch(() => {
    navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => video.srcObject = stream);
});

// 🔊 Enable audio
startBtn.addEventListener("click", () => {
    audioEnabled = true;

    const startSpeech = new SpeechSynthesisUtterance("Navigation started");
    window.speechSynthesis.speak(startSpeech);
});

// 🔊 CONVERT TO SHORT COMMAND
function simplify(text) {
    text = text.toLowerCase();

    // extract object name
    let object = "";
    const words = text.split(" ");

    for (let w of words) {
        if (!["stop,", "on", "your", "move", "left,", "right,", "ahead,", "go", "straight"].includes(w)) {
            object = w;
            break;
        }
    }

    // navigation mapping
    if (text.includes("stop")) return `${object} ahead stop`;
    if (text.includes("left")) return `${object} left`;
    if (text.includes("right")) return `${object} right`;
    if (text.includes("clear") || text.includes("straight")) return "Path clear";

    return text;
}

// 🔊 SPEAK FUNCTION
function speak(text) {
    if (!audioEnabled) return;

    const command = simplify(text);
    const now = Date.now();

    // avoid fast repetition
    if (command === lastCommand && (now - lastTime < COOLDOWN)) return;

    lastCommand = command;
    lastTime = now;

    window.speechSynthesis.cancel();

    const utter = new SpeechSynthesisUtterance(command);

    utter.lang = "en-US";
    utter.rate = 0.8; // slow smooth
    utter.pitch = 1;

    window.speechSynthesis.speak(utter);
}

const canvas = document.createElement("canvas");

// 🔁 Detection loop
setInterval(() => {

    if (!video.videoWidth) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    canvas.toBlob(blob => {

        let formData = new FormData();
        formData.append("frame", blob);

        fetch("/detect", {
            method: "POST",
            body: formData
        })
        .then(res => res.json())
        .then(data => {

            status.innerText = data.result;

            // 🔊 speak short dynamic command
            speak(data.result);

        });

    }, "image/jpeg");

}, 1500);