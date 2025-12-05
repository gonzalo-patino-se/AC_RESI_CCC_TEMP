// Auto-logout when session expires (5 minutes = 300 seconds)
const SESSION_TIMEOUT = 300 * 1000; // milliseconds

let logoutTimer;

function resetLogoutTimer() {
  clearTimeout(logoutTimer);
  logoutTimer = setTimeout(function() {
    window.location.href = '/accounts/login/';
  }, SESSION_TIMEOUT);
}

// Reset timer on user activity
document.addEventListener('mousedown', resetLogoutTimer);
document.addEventListener('keypress', resetLogoutTimer);
document.addEventListener('scroll', resetLogoutTimer);

// Start timer on page load
resetLogoutTimer();