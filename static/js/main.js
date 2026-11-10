/**
 * ============================================================================
 * QueueLess - Main Client-Side Utility JavaScript
 * ============================================================================
 * Beginner-friendly JavaScript providing UI helpers:
 * - Mobile navigation menu toggle
 * - Toast notification banner
 * - Voice speech announcement for token calling (Web Speech API)
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Menu Toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('show-mobile');
        });
    }

    // 2. Smooth scrolling for internal anchor links (e.g. #about, #features)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId && targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
});

/**
 * Displays a lightweight toast notification in the bottom-right corner.
 * @param {string} message - Text to display
 * @param {string} type - 'success', 'info', or 'error'
 */
function showToast(message, type = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Choose icon based on type
    let icon = 'fa-check-circle';
    if (type === 'error') icon = 'fa-exclamation-circle';
    if (type === 'info') icon = 'fa-info-circle';

    toast.innerHTML = `
        <i class="fa-solid ${icon}" style="color: ${type === 'error' ? '#ef4444' : '#059669'};"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Auto remove after 3.8 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3800);
}

/**
 * Text-to-speech announcement for college exhibition demo!
 * Speaks aloud: "Token HOSP-102, please proceed to Counter 1"
 */
function speakAnnouncement(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel(); // Stop any pending speech
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.95; // Slightly slower, clear cadence
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
    }
}
