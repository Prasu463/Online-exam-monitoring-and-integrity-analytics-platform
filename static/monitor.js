// ==============================
// ExamGuard Monitoring Script
// ==============================

let warnings = 0;
const maxWarnings = 3;

// ------------------------------
// Update Warning Counter
// ------------------------------

function updateWarnings(reason) {

    warnings++;

    document.getElementById("warningCount").innerHTML =
        warnings + " / " + maxWarnings;

    alert("Warning: " + reason);

    if (warnings >= maxWarnings) {

        alert("Maximum warnings reached.\nExam will be submitted.");

        document.querySelector("form").submit();
    }

}

// ------------------------------
// Disable Right Click
// ------------------------------

document.addEventListener("contextmenu", function (e) {

    e.preventDefault();

    updateWarnings("Right Click is Disabled");

});

// ------------------------------
// Disable Copy
// ------------------------------

document.addEventListener("copy", function (e) {

    e.preventDefault();

    updateWarnings("Copy is Not Allowed");

});

// ------------------------------
// Disable Paste
// ------------------------------

document.addEventListener("paste", function (e) {

    e.preventDefault();

    updateWarnings("Paste is Not Allowed");

});

// ------------------------------
// Disable Cut
// ------------------------------

document.addEventListener("cut", function (e) {

    e.preventDefault();

    updateWarnings("Cut is Not Allowed");

});

// ------------------------------
// Detect Tab Switching
// ------------------------------

document.addEventListener("visibilitychange", function () {

    if (document.hidden) {

        updateWarnings("Tab Switching Detected");

    }

});

// ------------------------------
// Full Screen Detection
// ------------------------------

document.addEventListener("fullscreenchange", function () {

    if (!document.fullscreenElement) {

        updateWarnings("Exited Full Screen");

    }

});

// ------------------------------
// Start Full Screen Automatically
// ------------------------------

window.onload = function () {

    if (document.documentElement.requestFullscreen) {

        document.documentElement.requestFullscreen();

    }

};

// ------------------------------
// Countdown Timer
// ------------------------------

let time = 60 * 60;

const timer = document.getElementById("timer");

setInterval(function () {

    let minutes = Math.floor(time / 60);
    let seconds = time % 60;

    timer.innerHTML =
        String(minutes).padStart(2, '0') +
        ":" +
        String(seconds).padStart(2, '0');

    if (time <= 0) {

        alert("Time Up!");

        document.querySelector("form").submit();

    }

    time--;

}, 1000);