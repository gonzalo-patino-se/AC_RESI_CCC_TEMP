console.log('Session timeout script loaded');

// Get session timeout from Django settings (in seconds)
const SESSION_TIMEOUT_SECONDS = parseInt(document.querySelector('meta[name="session-timeout"]').getAttribute('content')) || 300;
const SESSION_TIMEOUT_MS = SESSION_TIMEOUT_SECONDS * 1000;

let logoutTimer;
let countdownInterval;

// Create countdown display
function createCountdownDisplay() {
  const display = document.createElement('div');
  display.id = 'session-countdown-display';
  display.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: rgba(0, 0, 0, 0.8);
    color: #fff;
    padding: 15px 20px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: bold;
    z-index: 9998;
    min-width: 120px;
    text-align: center;
    display: none;
  `;
  display.innerHTML = `
    <div style="color: #ffc107; font-size: 14px;">Session expires in:</div>
    <div id="countdown-timer" style="font-size: 28px; color: #ffc107; margin-top: 5px;">300</div>
    <div style="font-size: 12px; color: #999; margin-top: 5px;">seconds</div>
  `;
  document.body.appendChild(display);
  return display;
}

const countdownDisplay = createCountdownDisplay();

function showCountdownDisplay() {
  countdownDisplay.style.display = 'block';
}

function hideCountdownDisplay() {
  countdownDisplay.style.display = 'none';
}

function showWarningPopup() {
  // Create popup
  const popup = document.createElement('div');
  popup.id = 'session-warning-popup';
  popup.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: #fff3cd;
    border: 2px solid #ffc107;
    border-radius: 8px;
    padding: 30px;
    z-index: 9999;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    max-width: 400px;
  `;
  
  popup.innerHTML = `
    <h2 style="color: #856404; margin-top: 0;">Session Expiring Soon</h2>
    <p style="color: #856404; font-size: 16px;">
      Your session will expire in <strong id="countdown">60</strong> seconds.
    </p>
    <p style="color: #856404; font-size: 14px;">Move your mouse or press a key to stay logged in.</p>
    <button id="stay-logged-in" style="
      background: #ffc107;
      border: none;
      padding: 10px 20px;
      border-radius: 5px;
      cursor: pointer;
      font-size: 14px;
      font-weight: bold;
    ">Stay Logged In</button>
  `;
  
  document.body.appendChild(popup);
  
  // Countdown in popup
  let timeLeft = SESSION_TIMEOUT_SECONDS;
  document.getElementById('countdown').textContent = timeLeft;
  
  countdownInterval = setInterval(() => {
    timeLeft--;
    document.getElementById('countdown').textContent = timeLeft;
    console.log(`⏱️ ${timeLeft}s`);
    
    if (timeLeft <= 0) {
      clearInterval(countdownInterval);
      console.log('Session expired, redirecting to login');
      window.location.href = '/accounts/login/';
    }
  }, 1000);
  
  // Stay logged in button
  document.getElementById('stay-logged-in').addEventListener('click', () => {
    popup.remove();
    clearInterval(countdownInterval);
    resetLogoutTimer();
    hideCountdownDisplay();
    console.log('✅ Session reset, user stayed logged in');
  });
}

function resetLogoutTimer() {
  clearTimeout(logoutTimer);
  hideCountdownDisplay();
  console.log('⏳ Session timer reset - next logout in ' + SESSION_TIMEOUT_SECONDS + ' seconds');
  
  logoutTimer = setTimeout(function() {
    console.log('⚠️ Showing session expiration warning');
    showCountdownDisplay();
    showWarningPopup();
  }, SESSION_TIMEOUT_MS);
}

// Reset timer on user activity
document.addEventListener('mousedown', resetLogoutTimer);
document.addEventListener('keypress', resetLogoutTimer);
document.addEventListener('scroll', resetLogoutTimer);

// Start timer on page load
console.log('🚀 Session timeout initialized: ' + SESSION_TIMEOUT_SECONDS + ' seconds');
resetLogoutTimer();