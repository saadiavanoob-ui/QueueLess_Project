/**
 * ============================================================================
 * QueueLess - Internationalization (i18n) & Accessibility (a11y) System
 * ============================================================================
 * Supports:
 * - English (en)
 * - Malayalam (ml) - മലയാളം
 * - Hindi (hi) - हिन्दी
 * - Accessibility: Font Size scaler (Normal, Large, Extra Large)
 * - Accessibility: High Contrast Mode
 * - Realistic Web Audio Airport/Kiosk Chime
 */

const I18N_DICTIONARY = {
  en: {
    brand_tagline: "One Platform. Every Queue.",
    brand_subtitle: "Skip the Wait. Save Your Time.",
    nav_home: "Home",
    nav_institutions: "Institutions",
    nav_features: "Features",
    nav_how_it_works: "How It Works",
    nav_track: "Track Token",
    nav_display: "Live TV Display",
    nav_book: "Book Token",
    nav_admin: "Admin / Staff",
    nav_login: "Login",
    nav_register: "Register",
    nav_dashboard: "My Dashboard",
    nav_logout: "Logout",
    hero_pill: "Next-Gen Smart Token Ecosystem",
    hero_title: "QueueLess",
    hero_desc: "A Universal Smart Queue Management System for Hospitals, Banks, Akshaya Centres, Colleges, Clinics, Railway Enquiry and Government Offices. Generate digital tokens, track queue progression in real time, and arrive right when it's your turn.",
    btn_get_started: "Book Your Token",
    btn_track_token: "Track Live Status",
    search_placeholder: "Search institutions by name, category, or location...",
    stats_total: "Total Tokens Today",
    stats_serving: "Currently Serving",
    stats_waiting: "Waiting in Queue",
    stats_completed: "Served & Completed",
    choose_institution_title: "Universal Institution Selection",
    choose_institution_subtitle: "Select a category or search below to view branches, active counters, and real-time wait estimation.",
    est_wait_label: "Est. Wait Time",
    people_ahead_label: "People Ahead",
    current_serving_label: "Current Serving",
    token_id_label: "TOKEN ID",
    status_waiting: "WAITING",
    status_almost: "ALMOST YOUR TURN",
    status_called: "NOW CALLING",
    status_serving: "NOW SERVING",
    status_completed: "COMPLETED",
    status_skipped: "SKIPPED",
    status_cancelled: "CANCELLED",
    btn_cancel_token: "Cancel Token",
    btn_rate_service: "Rate & Review Service",
    btn_qr_checkin: "Confirm Arrival (QR Check-in)",
    qr_checkin_title: "Quick QR Check-in",
    qr_checkin_desc: "Show this QR code to the counter scanner or enter the 6-character code upon arrival.",
    appointment_type_walkin: "Instant Walk-in Token",
    appointment_type_slot: "Schedule Future Appointment",
    priority_regular: "Regular Queue",
    priority_senior: "Senior Citizen (60+)",
    priority_pwd: "Persons with Disabilities (PwD)",
    priority_pregnant: "Pregnant Women",
    priority_emergency: "Emergency Case",
    offline_badge: "Offline Mode Active",
    font_size: "Font Size",
    contrast_toggle: "High Contrast"
  },
  ml: {
    brand_tagline: "ഒരു പ്ലാറ്റ്‌ഫോം. എല്ലാ ക്യൂവും.",
    brand_subtitle: "കാത്തിരിപ്പ് ഒഴിവാക്കൂ. സമയം ലാഭിക്കൂ.",
    nav_home: "ഹോം",
    nav_institutions: "സ്ഥാപനങ്ങൾ",
    nav_features: "സവിശേഷതകൾ",
    nav_how_it_works: "പ്രവർത്തനം",
    nav_track: "ട്രാക്ക് ടോക്കൺ",
    nav_display: "ലൈവ് ടിവി ഡിസ്പ്ലേ",
    nav_book: "ടോക്കൺ ബുക്ക് ചെയ്യുക",
    nav_admin: "അഡ്മിൻ / സ്റ്റാഫ്",
    nav_login: "ലോഗിൻ",
    nav_register: "രജിസ്റ്റർ",
    nav_dashboard: "ഡാഷ്‌ബോർഡ്",
    nav_logout: "ലോഗൗട്ട്",
    hero_pill: "സ്മാർട്ട് ടോക്കൺ ഇക്കോസിസ്റ്റം",
    hero_title: "ക്യൂലെസ്സ് (QueueLess)",
    hero_desc: "ആശുപത്രികൾ, ബാങ്കുകൾ, അക്ഷയ കേന്ദ്രങ്ങൾ, കോളേജുകൾ, ക്ലിനിക്കുകൾ, റെയിൽവേ എൻക്വയറി, സർക്കാർ ഓഫീസുകൾ എന്നിവയ്ക്കായുള്ള ഏകീകൃത സ്മാർട്ട് ക്യൂ മാനേജ്‌മെന്റ് സിസ്റ്റം. നിങ്ങളുടെ ഫോണിൽ നിന്ന് ഡിജിറ്റൽ ടോക്കൺ എടുക്കൂ, തത്സമയം നിരീക്ഷിക്കൂ.",
    btn_get_started: "ടോക്കൺ ബുക്ക് ചെയ്യുക",
    btn_track_token: "തത്സമയ സ്റ്റാറ്റസ് ട്രാക്ക് ചെയ്യുക",
    search_placeholder: "പേര്, വിഭാഗം അല്ലെങ്കിൽ സ്ഥലം എന്നിവ വഴി സ്ഥാപനങ്ങൾ തിരയുക...",
    stats_total: "ഇന്നത്തെ ആകെ ടോക്കണുകൾ",
    stats_serving: "ഇപ്പോൾ സേവനം നൽകുന്നത്",
    stats_waiting: "ക്യൂവിൽ കാത്തിരിക്കുന്നത്",
    stats_completed: "പൂർത്തിയായവ",
    choose_institution_title: "സ്ഥാപനം തിരഞ്ഞെടുക്കുക",
    choose_institution_subtitle: "ശാഖകൾ, കൗണ്ടറുകൾ, കാത്തിരിപ്പ് സമയം എന്നിവ കാണാൻ സ്ഥാപനം തിരഞ്ഞെടുക്കുക.",
    est_wait_label: "കണക്കാക്കിയ സമയം",
    people_ahead_label: "മുന്നിലുള്ള ആളുകൾ",
    current_serving_label: "ഇപ്പോൾ വിളിക്കുന്ന ടോക്കൺ",
    token_id_label: "ടോക്കൺ നമ്പർ",
    status_waiting: "കാത്തിരിക്കുന്നു",
    status_almost: "താങ്കളുടെ ഊഴം അടുത്തെത്തി",
    status_called: "കൗണ്ടറിലേക്ക് വിളിക്കുന്നു",
    status_serving: "സേവനം നൽകുന്നു",
    status_completed: "സേവനം പൂർത്തിയായി",
    status_skipped: "മാറ്റിവെച്ചു",
    status_cancelled: "റദ്ദാക്കി",
    btn_cancel_token: "ടോക്കൺ റദ്ദാക്കുക",
    btn_rate_service: "അഭിപ്രായം രേഖപ്പെടുത്തുക",
    btn_qr_checkin: "വരവ് സ്ഥിരീകരിക്കുക (QR ചെക്ക്-ഇൻ)",
    qr_checkin_title: "വേഗത്തിലുള്ള QR ചെക്ക്-ഇൻ",
    qr_checkin_desc: "കൗണ്ടറിൽ എത്തുമ്പോൾ ഈ ക്യുആർ കോഡ് കാണിക്കുകയോ 6 അക്ഷര കോഡ് നൽകുകയോ ചെയ്യുക.",
    appointment_type_walkin: "തത്സമയ ടോക്കൺ",
    appointment_type_slot: "മുൻകൂട്ടി സമയം തിരഞ്ഞെടുക്കുക",
    priority_regular: "സാധാരണ ക്യൂ",
    priority_senior: "മുതിർന്ന പൗരന്മാർ (60+)",
    priority_pwd: "ഭിന്നശേഷിക്കാർ (PwD)",
    priority_pregnant: "ഗർഭിണികൾ",
    priority_emergency: "അടിയന്തിര സാഹചര്യം",
    offline_badge: "ഓഫ്‌ലൈൻ മോഡ് സജീവം",
    font_size: "ഫോണ്ട് വലുപ്പം",
    contrast_toggle: "ഹൈ കോൺട്രാസ്റ്റ്"
  },
  hi: {
    brand_tagline: "एक मंच। हर कतार।",
    brand_subtitle: "इंतज़ार छोड़ें। समय बचाएं।",
    nav_home: "होम",
    nav_institutions: "संस्थान",
    nav_features: "विशेषताएं",
    nav_how_it_works: "यह कैसे काम करता है",
    nav_track: "टोकन ट्रैक करें",
    nav_display: "लाइव टीवी डिस्प्ले",
    nav_book: "टोकन बुक करें",
    nav_admin: "एडमिन / स्टाफ",
    nav_login: "लॉगिन",
    nav_register: "रजिस्टर",
    nav_dashboard: "डैशबोर्ड",
    nav_logout: "लॉगआउट",
    hero_pill: "स्मार्ट टोकन प्रबंधन प्रणाली",
    hero_title: "कतारमुक्त (QueueLess)",
    hero_desc: "अस्पतालों, बैंकों, अक्षय केंद्रों, कॉलेजों, क्लीनिकों, रेलवे पूछताछ और सरकारी कार्यालयों के लिए सार्वभौमिक स्मार्ट कतार प्रबंधन प्रणाली। मोबाइल से डिजिटल टोकन प्राप्त करें और वास्तविक समय में कतार ट्रैक करें।",
    btn_get_started: "टोकन बुक करें",
    btn_track_token: "लाइव स्थिति ट्रैक करें",
    search_placeholder: "नाम, श्रेणी या स्थान से संस्थान खोजें...",
    stats_total: "आज के कुल टोकन",
    stats_serving: "वर्तमान सेवा",
    stats_waiting: "कतार में प्रतीक्षारत",
    stats_completed: "पूर्ण किए गए",
    choose_institution_title: "संस्थान चुनें",
    choose_institution_subtitle: "शाखाएं, सक्रिय काउंटर और प्रतीक्षा समय देखने के लिए संस्थान चुनें।",
    est_wait_label: "अनुमानित प्रतीक्षा समय",
    people_ahead_label: "आगे लोग",
    current_serving_label: "वर्तमान टोकन",
    token_id_label: "टोकन नंबर",
    status_waiting: "प्रतीक्षारत",
    status_almost: "आपकी बारी आने वाली है",
    status_called: "काउंटर पर बुलाया गया",
    status_serving: "सेवा जारी",
    status_completed: "पूर्ण",
    status_skipped: "छोड़ दिया",
    status_cancelled: "रद्द किया गया",
    btn_cancel_token: "टोकन रद्द करें",
    btn_rate_service: "रेटिंग और समीक्षा दें",
    btn_qr_checkin: "आगमन की पुष्टि (QR चेक-इन)",
    qr_checkin_title: "त्वरित क्यूआर चेक-इन",
    qr_checkin_desc: "काउंटर पर आगमन पर यह क्यूआर कोड दिखाएं या 6-अंकीय कोड दर्ज करें।",
    appointment_type_walkin: "तत्काल वॉक-इन टोकन",
    appointment_type_slot: "अग्रिम अपॉइंटमेंट बुक करें",
    priority_regular: "सामान्य कतार",
    priority_senior: "वरिष्ठ नागरिक (60+)",
    priority_pwd: "दिव्यांगजन (PwD)",
    priority_pregnant: "गर्भवती महिलाएं",
    priority_emergency: "आपातकालीन स्थिति",
    offline_badge: "ऑफ़लाइन मोड सक्रिय",
    font_size: "फ़ॉन्ट आकार",
    contrast_toggle: "उच्च कंट्रास्ट"
  }
};

let currentLanguage = localStorage.getItem('queueless_lang') || 'en';
let currentFontSize = localStorage.getItem('queueless_font_size') || 'normal';
let isHighContrast = localStorage.getItem('queueless_high_contrast') === 'true';

// Initialize i18n & a11y on document ready
document.addEventListener('DOMContentLoaded', () => {
  applyLanguage(currentLanguage);
  applyFontSize(currentFontSize);
  applyHighContrast(isHighContrast);
});

function setLanguage(lang) {
  if (!I18N_DICTIONARY[lang]) lang = 'en';
  currentLanguage = lang;
  localStorage.setItem('queueless_lang', lang);
  applyLanguage(lang);
}

function applyLanguage(lang) {
  const dict = I18N_DICTIONARY[lang] || I18N_DICTIONARY.en;
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key]) {
      if (el.tagName === 'INPUT' && el.getAttribute('placeholder')) {
        el.setAttribute('placeholder', dict[key]);
      } else {
        el.textContent = dict[key];
      }
    }
  });

  const langSelect = document.getElementById('langSelect');
  if (langSelect) langSelect.value = lang;
}

function t(key) {
  const dict = I18N_DICTIONARY[currentLanguage] || I18N_DICTIONARY.en;
  return dict[key] || key;
}

// Accessibility Controls
function setFontSize(size) {
  currentFontSize = size;
  localStorage.setItem('queueless_font_size', size);
  applyFontSize(size);
}

function applyFontSize(size) {
  document.documentElement.classList.remove('font-normal', 'font-large', 'font-xlarge');
  if (size === 'large') {
    document.documentElement.classList.add('font-large');
  } else if (size === 'xlarge') {
    document.documentElement.classList.add('font-xlarge');
  } else {
    document.documentElement.classList.add('font-normal');
  }
}

function toggleHighContrast() {
  isHighContrast = !isHighContrast;
  localStorage.setItem('queueless_high_contrast', isHighContrast ? 'true' : 'false');
  applyHighContrast(isHighContrast);
}

function applyHighContrast(enabled) {
  if (enabled) {
    document.body.classList.add('high-contrast');
  } else {
    document.body.classList.remove('high-contrast');
  }
}

/**
 * Synthesizes an authentic kiosk airport sound chime via Web Audio API.
 * Clean, pleasant two-tone chime (587.33 Hz D5 -> 880 Hz A5).
 */
function playKioskChime() {
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();

    function playTone(freq, startTime, duration) {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, startTime);
      gain.gain.setValueAtTime(0, startTime);
      gain.gain.linearRampToValueAtTime(0.25, startTime + 0.05);
      gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(startTime);
      osc.stop(startTime + duration);
    }

    const now = ctx.currentTime;
    playTone(587.33, now, 0.45);        // D5 note
    playTone(880.00, now + 0.35, 0.65); // A5 note
  } catch (err) {
    console.warn('Audio chime unsupported or blocked by browser autoplay policy:', err);
  }
}

/**
 * Text-to-Speech Announcement supporting English, Malayalam, Hindi
 */
function announceTokenVoice(tokenNumber, counterNumber, customerName = '') {
  playKioskChime();
  setTimeout(() => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();

    let announcementText = `Attention. Token ${tokenNumber}, please proceed to Counter ${counterNumber}.`;
    let speechLang = 'en-US';

    if (currentLanguage === 'ml') {
      announcementText = `ശ്രദ്ധിക്കുക. ടോക്കൺ ${tokenNumber}, കൗണ്ടർ ${counterNumber}-ലേക്ക് ദയവായി വരിക.`;
      speechLang = 'ml-IN';
    } else if (currentLanguage === 'hi') {
      announcementText = `कृपया ध्यान दें। टोकन ${tokenNumber}, कृपया काउंटर ${counterNumber} पर जाएं।`;
      speechLang = 'hi-IN';
    }

    const utterance = new SpeechSynthesisUtterance(announcementText);
    utterance.rate = 0.92;
    utterance.pitch = 1.0;
    utterance.lang = speechLang;
    window.speechSynthesis.speak(utterance);
  }, 600);
}

window.I18n = {
  setLanguage,
  applyLanguage,
  t,
  setFontSize,
  toggleHighContrast,
  playKioskChime,
  announceTokenVoice
};
