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

    // Chart Variables
    let breakdownChart = null;
    let overTimeChart = null;

    let postureReasons = {
        "Shoulder Tilted to Left": 0,
        "Shoulder Tilted to Right": 0,
        "Forward Head Detected": 0,
        "Slouch Detected": 0,
    };

    let timestamps = [];
    let goodPercentages = [];

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

    async function updateTimers() {
        totalSeconds++;
        totalTimeDisplay.textContent = formatTime(totalSeconds);

        // Get the buddy UI elements
        const buddyMessageEl = document.getElementById('buddy-message');
        const buddyFaceEl = document.getElementById('buddy-face');
        
        try {
            const response = await fetch('/posture_status');
            if (!response.ok) return;
    
            const data = await response.json();
            const isGoodPosture = data.posture === 'GOOD';
            const postureMessage = data.reason || (isGoodPosture ? 'Perfect Posture!' : 'Adjust Your Posture!');
    
            // Update timers
            if (isGoodPosture) {
                goodPostureSeconds++;
                goodTimeDisplay.textContent = formatTime(goodPostureSeconds);
            }

            // Update buddy UI
            buddyMessageEl.textContent = postureMessage;
            if (isGoodPosture) {
                buddyFaceEl.className = 'buddy-face happy';
                buddyFaceEl.textContent = '😊'; // Happy Face
            } else {
                buddyFaceEl.className = 'buddy-face sad';
                buddyFaceEl.textContent = '😟'; // Concerned Face
            }
    
            // Update reminder box
            reminderBox.className = isGoodPosture ? 'reminder good-posture' : 'reminder bad-posture';
            reminderBox.innerHTML = `Current Status: <strong>${isGoodPosture ? 'Perfect Posture!' : 'Adjust Your Posture!'}</strong>`;
    
            // Update posture reason counts
            if (data.reason && postureReasons.hasOwnProperty(data.reason)) {
                postureReasons[data.reason]++;
            }
    
            // Update Line Chart Data (for end analysis)
            const percentage = totalSeconds > 0 ? (goodPostureSeconds / totalSeconds) * 100 : 0;
            timestamps.push(totalSeconds);
            goodPercentages.push(percentage.toFixed(1));
    
        } catch (err) {
            console.error("Error fetching posture status:", err);
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
     
    pauseBtn.addEventListener('click', async () => { // **NOTE: Made function async**
        if (isRunning) {
            // PAUSE LOGIC
            isRunning = false;
            clearInterval(totalTimer);
            pauseBtn.textContent = 'RESUME';
            
            // 1. Send signal to backend to stop processing/stream
            await stopCamera(); 
            
            // 2. Change video feed to static placeholder
            videoFeed.src = placeholderSrc; 
            
            reminderBox.className = 'reminder good-posture';
            reminderBox.innerHTML = 'Current Status: <strong>Session Paused</strong>';
            
        } else {
            // RESUME LOGIC
            
            // 1. Start camera/detection *before* starting the timer
            const cameraStarted = await initializeCamera();
            if (!cameraStarted) return;
            videoFeed.src = '/video_feed';

            // 2. Start session timers
            isRunning = true;
            totalTimer = setInterval(updateTimers, 1000);
            pauseBtn.textContent = 'PAUSE';
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
        pauseBtn.textContent = 'PAUSE'; 
        
        // 5. Calculate and display analysis
        const goodPercentage = totalSeconds > 0 
            ? ((goodPostureSeconds / totalSeconds) * 100).toFixed(1) 
            : 0;

        document.getElementById('final-total-time').textContent = formatTime(totalSeconds);
        document.getElementById('final-good-time').textContent = formatTime(goodPostureSeconds);
        document.getElementById('posture-percentage').textContent = `${goodPercentage}%`;

        const statCircle = document.querySelector('.analysis-stats .stat-circle');
        if (statCircle) {
            // The CSS variable --percentage controls the conic-gradient fill.
            // We use the raw number (not with a '%' or 'deg' unit) here.
            statCircle.style.setProperty('--percentage', goodPercentage);
}

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

        // Include AI feedback
        const aiFeedbackEl = document.getElementById('ai-feedback');
        try {
            const response = await fetch('/get_analysis_text'); 
            
            if (response.ok) {
                const feedbackText = await response.text();
                aiFeedbackEl.textContent = feedbackText.trim();
            } else {
                aiFeedbackEl.textContent = "Could not load AI feedback (Server Error).";
                console.error('Failed to fetch analysis text:', response.status);
            }
        } catch (error) {
            aiFeedbackEl.textContent = "Could not load AI feedback (Network Error).";
            console.error('Network error fetching analysis text:', error);
        }
        
        // PIE CHART: Posture Breakdown
        const breakdownCtx = document.getElementById('posture-breakdown-chart').getContext('2d');
        
        // Destroy previous instance to avoid error if END is pressed multiple times
        if (breakdownChart) breakdownChart.destroy(); 

        breakdownChart = new Chart(breakdownCtx, {
            type: 'pie',
            data: {
                labels: Object.keys(postureReasons),
                datasets: [{
                    data: Object.values(postureReasons),
                    backgroundColor: ['#FF6384','#36A2EB','#FFCE56','#FF8C00']
                }]
            }
        });

        // LINE CHART: Posture Over Time
        const overTimeCtx = document.getElementById('posture-over-time-chart').getContext('2d');

        // Destroy previous instance to avoid error if END is pressed multiple times
        if (overTimeChart) overTimeChart.destroy(); 
        
        overTimeChart = new Chart(overTimeCtx, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: '% Good Posture',
                    data: goodPercentages,
                    borderColor: '#36A2EB',
                    fill: false,
                    tension: 0.1
                }]
            },
            options: { 
                scales: { 
                    y: { min: 0, max: 100, title: { display: true, text: 'Percentage (%)' } },
                    x: { title: { display: true, text: 'Time (s)' } }
                },
                maintainAspectRatio: false
            }
        });

        // 6. Reset session variables
        totalSeconds = 0;
        goodPostureSeconds = 0;
        totalTimeDisplay.textContent = formatTime(0);
        goodTimeDisplay.textContent = formatTime(0);
        reminderBox.className = 'reminder';
        reminderBox.innerHTML = 'Current Status: <strong>Ready to Start</strong>';
        postureReasons = {
            "Shoulder Tilted to Left": 0,
            "Shoulder Tilted to Right": 0,
            "Forward Head Detected": 0,
            "Slouch Detected": 0,
        };
        timestamps = [];
        goodPercentages = [];
        
        // NOTE: The next time the end button is pressed, the charts will be destroyed
        // and recreated with the new data, so no need to explicitly update/reset them here.
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