// static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    // Get all necessary DOM elements
    const videoFeed = document.getElementById('video-feed'); // --- MODIFICATION ---
    const totalTimeDisplay = document.getElementById('total-time');
    const goodTimeDisplay = document.getElementById('good-time');
    const reminderBox = document.getElementById('reminder-box');
    const startBtn = document.getElementById('start-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const endBtn = document.getElementById('end-btn');
    const analysisSection = document.getElementById('analysis-section');

    // --- MODIFICATION ---
    // Store the initial placeholder image source to revert back to it later
    const placeholderSrc = videoFeed.src;

    // Timer variables
    let totalSeconds = 0;
    let goodPostureSeconds = 0;
    let isRunning = false;
    let totalTimer;

    // Helper function to format seconds into HH:MM:SS
    function formatTime(seconds) {
        const h = String(Math.floor(seconds / 3600)).padStart(2, '0');
        const m = String(Math.floor((seconds % 3600) / 60)).padStart(2, '0');
        const s = String(seconds % 60).padStart(2, '0');
        return `${h}:${m}:${s}`;
    }

    // --- MODIFICATION ---
    // New function to get the real posture status from the Flask backend
    async function fetchAndUpdatePostureStatus() {
        try {
            const response = await fetch('/posture_status');
            if (!response.ok) return false; // Handle cases where the server is down

            const data = await response.json();
            const isGoodPosture = data.posture === 'GOOD';

            // Update the Reminder Box UI based on real data
            if (isGoodPosture) {
                reminderBox.className = 'reminder good-posture';
                reminderBox.innerHTML = 'Current Status: <strong>Perfect Posture!</strong>';
            } else {
                reminderBox.className = 'reminder bad-posture';
                reminderBox.innerHTML = 'Current Status: <strong>Adjust Your Posture!</strong>';
            }
            return isGoodPosture;

        } catch (error) {
            console.error("Error fetching posture status:", error);
            return false; // Assume bad posture if there's an error
        }
    }

    // Function to update the main timers
    async function updateTimers() {
        totalSeconds++;
        totalTimeDisplay.textContent = formatTime(totalSeconds);

        // --- REPLACEMENT ---
        // Replace the MOCK DATA block with our new async function call
        const isGoodPosture = await fetchAndUpdatePostureStatus();

        if (isGoodPosture) {
            goodPostureSeconds++;
            goodTimeDisplay.textContent = formatTime(goodPostureSeconds);
        }
    }

    // START Button Handler
    startBtn.addEventListener('click', () => {
        if (isRunning) return;
        isRunning = true;
        
        // --- MODIFICATION ---
        // Start the live video feed!
        videoFeed.src = '/video_feed';

        startBtn.disabled = true;
        pauseBtn.disabled = false;
        endBtn.disabled = false;
        analysisSection.classList.add('hidden');

        totalTimer = setInterval(updateTimers, 1000);
    });

    // PAUSE Button Handler (your logic is great, no changes needed)
    pauseBtn.addEventListener('click', () => {
        // This button now toggles between Pause and Resume
        if (isRunning) {
            isRunning = false;
            clearInterval(totalTimer);
            pauseBtn.textContent = 'RESUME';
        } else {
            isRunning = true;
            totalTimer = setInterval(updateTimers, 1000);
            pauseBtn.textContent = 'PAUSE';
        }
    });

    // END Button Handler
    endBtn.addEventListener('click', () => {
        clearInterval(totalTimer);
        isRunning = false;

        // --- MODIFICATION ---
        // Revert the video feed to the static placeholder image
        videoFeed.src = placeholderSrc;
        
        startBtn.disabled = false;
        pauseBtn.disabled = true;
        endBtn.disabled = true;
        pauseBtn.textContent = 'PAUSE'; // Reset pause button text
        
        const goodPercentage = totalSeconds > 0 
            ? ((goodPostureSeconds / totalSeconds) * 100).toFixed(1) 
            : 0;

        document.getElementById('final-total-time').textContent = formatTime(totalSeconds);
        document.getElementById('final-good-time').textContent = formatTime(goodPostureSeconds);
        document.getElementById('posture-percentage').textContent = `${goodPercentage}%`;

        // ... (your excellent feedback message logic) ...
        const feedbackMessage = document.querySelector('.feedback-message');
        if (goodPercentage >= 80) {
            feedbackMessage.textContent = "Excellent work! Your posture score is fantastic! 🎉";
        } else if (goodPercentage >= 50) {
            feedbackMessage.textContent = "Good session! Keep trying to maintain your posture next time! 👍";
        } else {
            feedbackMessage.textContent = "Needs improvement. Let's focus on posture awareness next session. 😔";
        }
        
        analysisSection.classList.remove('hidden');

        totalSeconds = 0;
        goodPostureSeconds = 0;
        totalTimeDisplay.textContent = formatTime(0);
        goodTimeDisplay.textContent = formatTime(0);
        reminderBox.className = 'reminder';
        reminderBox.innerHTML = 'Current Status: **Ready to Start**';
    });
});