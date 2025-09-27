document.addEventListener('DOMContentLoaded', () => {
    // Get all necessary DOM elements
    const videoFeed = document.getElementById('video-feed');
    const totalTimeDisplay = document.getElementById('total-time');
    const goodTimeDisplay = document.getElementById('good-time');
    const reminderBox = document.getElementById('reminder-box');
    const startBtn = document.getElementById('start-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const endBtn = document.getElementById('end-btn');
    const analysisSection = document.getElementById('analysis-section');

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

    // --- NEW FUNCTIONS FOR CAMERA/BACKEND CONTROL ---

    // Function to get the real posture status from the Flask backend
    async function fetchAndUpdatePostureStatus() {
        try {
            const response = await fetch('/posture_status');
            if (!response.ok) return false;

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
            // Fallback UI for connection errors
            reminderBox.className = 'reminder bad-posture';
            reminderBox.innerHTML = 'Current Status: <strong>Detection Offline</strong>';
            return false;
        }
    }

    // Function to update the main timers using REAL posture detection
    async function updateTimers() {
        totalSeconds++;
        totalTimeDisplay.textContent = formatTime(totalSeconds);

        const isGoodPosture = await fetchAndUpdatePostureStatus();

        if (isGoodPosture) {
            goodPostureSeconds++;
            goodTimeDisplay.textContent = formatTime(goodPostureSeconds);
        }
    }

    // Function to start the camera and posture detection via the backend endpoint
    async function initializeCamera() {
        try {
            reminderBox.innerHTML = 'Current Status: <strong>Starting camera...</strong>';
            const response = await fetch('/start_camera', { method: 'POST' });
            if (!response.ok) {
                throw new Error('Failed to start camera via backend');
            }
            console.log('Camera and posture detection started successfully');
            return true;
        } catch (error) {
            console.error('Error starting camera:', error);
            alert('Unable to start camera. Check your backend server and camera permissions.');
            reminderBox.className = 'reminder bad-posture';
            reminderBox.innerHTML = 'Current Status: <strong>Camera Failed to Start</strong>';
            return false;
        }
    }

    // Function to stop the camera and posture detection via the backend endpoint
    async function stopCamera() {
        try {
            const response = await fetch('/stop_camera', { method: 'POST' });
            if (!response.ok) {
                throw new Error('Failed to stop camera via backend');
            }
            console.log('Camera stopped successfully');
        } catch (error) {
            console.error('Error stopping camera:', error);
        }
    }
    // --- BUTTON HANDLERS WITH CAMERA CONTROL INTEGRATION ---

    startBtn.addEventListener('click', async () => {
        if (isRunning) return;
    
        const calibrationOverlay = document.getElementById('calibration-overlay');
        const countdownEl = document.getElementById('calibration-countdown');
    
        // Show overlay
        calibrationOverlay.classList.remove('hidden');
    
        let countdown = 3;
        countdownEl.textContent = countdown;
    
        // Start live video feed immediately
        const cameraStarted = await initializeCamera();
        if (!cameraStarted) return;
        videoFeed.src = '/video_feed';
    
        // Countdown every second
        const countdownInterval = setInterval(() => {
            countdown--;
            countdownEl.textContent = countdown;
            if (countdown <= 0) clearInterval(countdownInterval);
        }, 1000);
    
        // After 3 seconds, hide overlay, grab frame, start session
        setTimeout(async () => {
            calibrationOverlay.classList.add('hidden');
    
            // Grab a frame for calibration
            await fetch('/calibrate', { method: 'POST' });
    
            // Start session timers
            isRunning = true;
            startBtn.disabled = true;
            pauseBtn.disabled = false;
            endBtn.disabled = false;
            analysisSection.classList.add('hidden');
    
            totalTimer = setInterval(updateTimers, 1000);
        }, 3000);
    });
     

    // PAUSE Button Handler (modified to use the prettier resume/pause logic)
    pauseBtn.addEventListener('click', () => {
        if (isRunning) {
            // PAUSE LOGIC
            isRunning = false;
            clearInterval(totalTimer);
            pauseBtn.textContent = 'RESUME';
            // Optional: You might want to call a /pause_detection endpoint here
            reminderBox.className = 'reminder good-posture';
            reminderBox.innerHTML = 'Current Status: <strong>Session Paused</strong>';
        } else {
            // RESUME LOGIC
            isRunning = true;
            totalTimer = setInterval(updateTimers, 1000);
            pauseBtn.textContent = 'PAUSE';
            // The next updateTimers call will refresh the reminderBox status
        }
    });

    // END Button Handler
    endBtn.addEventListener('click', async () => {
        // 1. Stop all timers
        clearInterval(totalTimer);
        isRunning = false;
        
        // 2. Stop the camera/backend detection
        await stopCamera();

        // 3. Revert the video feed to the static placeholder image
        videoFeed.src = placeholderSrc;
        
        // 4. Reset buttons and UI
        startBtn.disabled = false;
        pauseBtn.disabled = true;
        endBtn.disabled = true;
        pauseBtn.textContent = 'PAUSE'; // Reset pause button text
        
        // 5. Calculate and display analysis
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
            feedbackMessage.style.color = 'var(--success-color)';
        } else if (goodPercentage >= 50) {
            feedbackMessage.textContent = "Good session! Keep trying to maintain your posture next time! 👍";
            feedbackMessage.style.color = 'var(--accent-color)';
        } else {
            feedbackMessage.textContent = "Needs improvement. Let's focus on posture awareness next session. 😔";
            feedbackMessage.style.color = 'var(--danger-color)';
        }

        analysisSection.classList.remove('hidden');

        // 6. Reset session variables
        totalSeconds = 0;
        goodPostureSeconds = 0;
        totalTimeDisplay.textContent = formatTime(0);
        goodTimeDisplay.textContent = formatTime(0);
        reminderBox.className = 'reminder';
        reminderBox.innerHTML = 'Current Status: <strong>Ready to Start</strong>';
    });

    // Optional: Initial status check on page load
    window.addEventListener('load', async () => {
        try {
            const response = await fetch('/posture_status');
            if (response.ok) {
                reminderBox.innerHTML = 'Current Status: <strong>Backend Ready</strong>';
            } else {
                reminderBox.className = 'reminder bad-posture';
                reminderBox.innerHTML = 'Current Status: <strong>Backend/Camera Disconnected</strong>';
            }
        } catch (error) {
            reminderBox.className = 'reminder bad-posture';
            reminderBox.innerHTML = 'Current Status: <strong>Backend Not Connected</strong>';
        }
    });
});

// Closes the existing session and starts new session
function closeAnalysis() {
    const analysisSection = document.getElementById('analysis-section');
    analysisSection.classList.add('hidden');

    // Reset session variables and UI
    totalSeconds = 0;
    goodPostureSeconds = 0;
    totalTimeDisplay.textContent = '00:00:00';
    goodTimeDisplay.textContent = '00:00:00';
    reminderBox.className = 'reminder';
    reminderBox.innerHTML = 'Current Status: <strong>Ready to Start</strong>';

    // Reset buttons
    startBtn.disabled = false;
    pauseBtn.disabled = true;
    pauseBtn.textContent = 'PAUSE';
    endBtn.disabled = true;

    // Reset video feed
    videoFeed.src = placeholderSrc;
}