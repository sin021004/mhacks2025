// Get all necessary DOM elements
const totalTimeDisplay = document.getElementById('total-time');
const goodTimeDisplay = document.getElementById('good-time');
const reminderBox = document.getElementById('reminder-box');
const startBtn = document.getElementById('start-btn');
const pauseBtn = document.getElementById('pause-btn');
const endBtn = document.getElementById('end-btn');
const analysisSection = document.getElementById('analysis-section');

// Timer variables
let totalSeconds = 0;
let goodPostureSeconds = 0;
let isRunning = false;
let totalTimer; // Interval for the main timer
let postureUpdateInterval; // Interval for checking posture status

// Helper function to format seconds into HH:MM:SS
function formatTime(seconds) {
    const h = String(Math.floor(seconds / 3600)).padStart(2, '0');
    const m = String(Math.floor((seconds % 3600) / 60)).padStart(2, '0');
    const s = String(seconds % 60).padStart(2, '0');
    return `${h}:${m}:${s}`;
}

// Function to update the main timers
function updateTimers() {
    totalSeconds++;
    totalTimeDisplay.textContent = formatTime(totalSeconds);

    // ----------------------------------------------------
    // MOCK DATA SIMULATION LOGIC:
    // **TEST CASE 1: Simulate random good posture ~70% of the time**
    const isGoodPosture = Math.random() < 0.7; 
    
    // **TEST CASE 2: Simulate 5 seconds good, 5 seconds bad (for predictability)**
    // const isGoodPosture = (totalSeconds % 10) < 5; 
    // ----------------------------------------------------

    if (isGoodPosture) {
        goodPostureSeconds++;
        goodTimeDisplay.textContent = formatTime(goodPostureSeconds);
        
        // Update the Reminder Box for GOOD POSTURE
        reminderBox.className = 'reminder good-posture';
        reminderBox.innerHTML = 'Current Status: **Perfect Posture!**';
    } else {
        // Update the Reminder Box for BAD POSTURE
        reminderBox.className = 'reminder bad-posture';
        reminderBox.innerHTML = 'Current Status: **Slouching! Adjust your back!**';
    }
}

// START Button Handler
startBtn.addEventListener('click', () => {
    if (isRunning) return;

    isRunning = true;
    
    // Enable/Disable buttons
    startBtn.disabled = true;
    pauseBtn.disabled = false;
    endBtn.disabled = false;
    analysisSection.classList.add('hidden'); // Hide analysis on start

    // Start the main timer (updates every second)
    totalTimer = setInterval(updateTimers, 1000);
});

// PAUSE Button Handler
pauseBtn.addEventListener('click', () => {
    if (!isRunning) return;
    
    isRunning = false;

    // Enable/Disable buttons
    startBtn.disabled = false;
    pauseBtn.disabled = true;

    // Pause the timers
    clearInterval(totalTimer);
});

// END Button Handler
endBtn.addEventListener('click', () => {
    // Stop all timers
    clearInterval(totalTimer);
    isRunning = false;
    
    // Reset buttons
    startBtn.disabled = false;
    pauseBtn.disabled = true;
    endBtn.disabled = true;
    
    // Calculate and display analysis
    const goodPercentage = totalSeconds > 0 
        ? ((goodPostureSeconds / totalSeconds) * 100).toFixed(1) 
        : 0;

    document.getElementById('final-total-time').textContent = formatTime(totalSeconds);
    document.getElementById('final-good-time').textContent = formatTime(goodPostureSeconds);
    document.getElementById('posture-percentage').textContent = `${goodPercentage}%`;

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
    
    // Show analysis
    analysisSection.classList.remove('hidden');

    // **Optional: Reset for a new session**
    totalSeconds = 0;
    goodPostureSeconds = 0;
    totalTimeDisplay.textContent = formatTime(0);
    goodTimeDisplay.textContent = formatTime(0);
    reminderBox.className = 'reminder good-posture';
    reminderBox.innerHTML = 'Current Status: **Ready to Start**';
});