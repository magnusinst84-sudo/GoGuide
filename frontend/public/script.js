// GoGuide Interactive Functionality

// Coordinated high-precision smooth scroll helper powered by GSAP ScrollToPlugin
function smoothScrollTo(target, duration = 0.9, onComplete = null) {
  const targetEl = typeof target === 'string' ? document.querySelector(target) : target;
  if (!targetEl) return;

  if (typeof gsap !== 'undefined' && typeof ScrollToPlugin !== 'undefined') {
    if (typeof ScrollTrigger !== 'undefined') {
      ScrollTrigger.refresh();
    }
    gsap.to(window, {
      scrollTo: {
        y: targetEl,
        autoKill: false,
      },
      duration: duration,
      ease: 'power2.inOut',
      overwrite: 'auto',
      onComplete: () => {
        if (typeof ScrollTrigger !== 'undefined') {
          ScrollTrigger.refresh();
        }
        if (onComplete) onComplete();
      },
    });
  } else {
    targetEl.scrollIntoView({ behavior: 'smooth' });
    if (onComplete) setTimeout(onComplete, 800);
  }
}
window.smoothScrollTo = smoothScrollTo;

document.addEventListener('DOMContentLoaded', () => {
  // Reset questionnaire state on fresh page load to ensure clean start
  function clearQuestionnaireStorage() {
    const keysToKeep = [
      'goguide_theme', 
      'goguide_user_name', 
      'goguide_user_email', 
      'goguide_is_logged_in'
    ];
    const keysToRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('goguide_') && !keysToKeep.includes(key)) {
        keysToRemove.push(key);
      }
    }
    keysToRemove.forEach(k => localStorage.removeItem(k));
  }
  clearQuestionnaireStorage();

  // 1. FAQ Accordion interaction
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(item => {
    const questionBtn = item.querySelector('.faq-question');
    if (!questionBtn) return;

    questionBtn.addEventListener('click', () => {
      const isOpen = item.classList.contains('active');

      // Close other opened FAQs for accordion behavior
      faqItems.forEach(otherItem => {
        otherItem.classList.remove('active');
        const otherBtn = otherItem.querySelector('.faq-question');
        if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
      });

      if (!isOpen) {
        item.classList.add('active');
        questionBtn.setAttribute('aria-expanded', 'true');
      }
    });
  });

  // 2. Start Now Button: Smoothly scrolls to Academic Inputs section
  const startNowBtn = document.getElementById('startNowBtn');
  startNowBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    smoothScrollTo('#studentInputs', 0.9, () => {
      const streamSelect = document.getElementById('academicStream');
      if (streamSelect) streamSelect.focus();
    });
  });

  // Modals Management (Native <dialog>)
  const signupDialog = document.getElementById('signupDialog');
  const startDialog = document.getElementById('startDialog');
  const closeSignupDialog = document.getElementById('closeSignupDialog');
  const closeStartDialog = document.getElementById('closeStartDialog');

  // Close buttons
  closeSignupDialog?.addEventListener('click', () => {
    signupDialog?.close();
  });

  closeStartDialog?.addEventListener('click', () => {
    startDialog?.close();
  });

  // Light dismiss on backdrop click for native dialogs
  [signupDialog, startDialog].forEach(dialog => {
    if (!dialog) return;
    dialog.addEventListener('click', (event) => {
      const rect = dialog.getBoundingClientRect();
      const isInDialog = (
        rect.top <= event.clientY &&
        event.clientY <= rect.top + rect.height &&
        rect.left <= event.clientX &&
        event.clientX <= rect.left + rect.width
      );
      if (!isInDialog) {
        dialog.close();
      }
    });
  });

  // 3. Smooth scroll for FAQ button
  const faqNavBtn = document.getElementById('faqNavBtn');
  faqNavBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    smoothScrollTo('#faq', 1.0);
  });

  // Intercept all in-page hash links for coordinated smooth scrolling
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const href = anchor.getAttribute('href');
      if (href && href.length > 1) {
        const targetElement = document.querySelector(href);
        if (targetElement) {
          e.preventDefault();
          smoothScrollTo(targetElement, 1.0);
        }
      }
    });
  });

  // 4. Student Academic Details Form submission
  const studentForm = document.getElementById('studentDetailsForm');
  studentForm?.addEventListener('submit', (e) => {
    e.preventDefault();

    const streamEl = document.getElementById('academicStream');
    const marksEl = document.getElementById('marksPercentage');
    const cityEl = document.getElementById('currentCity');

    const streamVal = streamEl ? streamEl.value.trim() : '';
    const marksVal = marksEl ? marksEl.value.trim() : '';
    const cityVal = cityEl ? cityEl.value.trim() : '';

    if (!streamVal) {
      window.showToast('Please select your academic stream.');
      streamEl?.focus();
      return;
    }

    const marksNum = parseFloat(marksVal);
    if (isNaN(marksNum) || marksNum < 0 || marksNum > 100) {
      window.showToast('Please enter a valid percentage between 0 and 100.');
      marksEl?.focus();
      return;
    }

    if (!cityVal) {
      window.showToast('Please enter your current city.');
      cityEl?.focus();
      return;
    }

    try {
      localStorage.setItem('goguide_stream', streamVal);
      localStorage.setItem('goguide_marks', marksVal);
      localStorage.setItem('goguide_city', cityVal);
    } catch (err) {
      console.warn('Storage unavailable:', err);
    }

    window.showToast('Academic details saved! Proceeding to Parent Financial Info...');

    // Smoothly scroll down to Parent Financial Inputs section
    smoothScrollTo('#parentInputs', 0.95);
  });

  // 4b. Parent Financial Details Form submission
  const parentForm = document.getElementById('parentDetailsForm');
  parentForm?.addEventListener('submit', (e) => {
    e.preventDefault();

    const incomeEl = document.getElementById('annualIncome');
    const savingsEl = document.getElementById('savingsAvailable');
    const budgetEl = document.getElementById('annualBudget');
    const loanEl = document.getElementById('maxLoan');

    const incomeVal = incomeEl ? incomeEl.value.trim() : '';
    const savingsVal = savingsEl ? savingsEl.value.trim() : '';
    const budgetVal = budgetEl ? budgetEl.value.trim() : '';
    const loanVal = loanEl ? loanEl.value.trim() : '';

    if (!incomeVal || parseFloat(incomeVal) < 0) {
      window.showToast('Please enter a valid annual household income.');
      incomeEl?.focus();
      return;
    }

    if (!savingsVal || parseFloat(savingsVal) < 0) {
      window.showToast('Please enter the savings available.');
      savingsEl?.focus();
      return;
    }

    if (!budgetVal || parseFloat(budgetVal) < 0) {
      window.showToast('Please enter the annual education budget.');
      budgetEl?.focus();
      return;
    }

    if (!loanVal || parseFloat(loanVal) < 0) {
      window.showToast('Please enter the maximum loan willingness.');
      loanEl?.focus();
      return;
    }

    try {
      localStorage.setItem('goguide_annual_income', incomeVal);
      localStorage.setItem('goguide_savings_available', savingsVal);
      localStorage.setItem('goguide_annual_budget', budgetVal);
      localStorage.setItem('goguide_max_loan', loanVal);
    } catch (err) {
      console.warn('Storage unavailable:', err);
    }

    window.showToast('Financial overview saved! Proceeding to Parent Preferences...');

    // Smoothly scroll down to Parent Preferences section
    smoothScrollTo('#parentPreferencesSection', 0.95);
  });

  // 4c. Parent Preferences Form submission (Risk appetite & early employment)
  const parentPrefForm = document.getElementById('parentPreferencesForm');
  parentPrefForm?.addEventListener('submit', (e) => {
    e.preventDefault();

    const selectedRisk = document.querySelector('input[name="parent_risk_appetite"]:checked')?.value || '3';
    const selectedEmploy = document.querySelector('input[name="parent_early_employment"]:checked')?.value || '3';

    try {
      localStorage.setItem('goguide_parent_risk', selectedRisk);
      localStorage.setItem('goguide_parent_employment', selectedEmploy);
    } catch (err) {
      console.warn('Storage unavailable:', err);
    }

    window.showToast('Parent preferences saved! Proceeding to Expected Careers...');

    // Smoothly scroll down to Parent Expected Careers section
    smoothScrollTo('#parentCareersSection', 0.95);
  });

  // 4d. Render Parent Careers Selection & Handle 3-5 Career Selection Form
  renderParentCareers();

  const parentCareersForm = document.getElementById('parentCareersForm');
  parentCareersForm?.addEventListener('submit', (e) => {
    e.preventDefault();

    const selectedCareers = window.getSelectedParentCareers();
    if (selectedCareers.length < 3) {
      window.showToast('Please select at least 3 expected careers (maximum 5).');
      return;
    }
    if (selectedCareers.length > 5) {
      window.showToast('You can select a maximum of 5 expected careers.');
      return;
    }

    try {
      localStorage.setItem('goguide_parent_careers', JSON.stringify(selectedCareers));
    } catch (err) {
      console.warn('Storage unavailable:', err);
    }

    window.showToast('Parent expected careers saved! Revealing Interest Assessment...');

    // Smoothly scroll down to Interest Assessment section
    smoothScrollTo('#interestSection', 0.95);
  });

  // Pre-fill previously stored inputs if available
  try {
    const savedStream = localStorage.getItem('goguide_stream');
    const savedMarks = localStorage.getItem('goguide_marks');
    const savedCity = localStorage.getItem('goguide_city');

    if (savedStream) {
      const streamEl = document.getElementById('academicStream');
      if (streamEl) streamEl.value = savedStream;
    }
    if (savedMarks) {
      const marksEl = document.getElementById('marksPercentage');
      if (marksEl) marksEl.value = savedMarks;
    }
    if (savedCity) {
      const cityEl = document.getElementById('currentCity');
      if (cityEl) cityEl.value = savedCity;
    }

    // Pre-fill parent financial fields
    const savedIncome = localStorage.getItem('goguide_annual_income');
    const savedSavings = localStorage.getItem('goguide_savings_available');
    const savedBudget = localStorage.getItem('goguide_annual_budget');
    const savedLoan = localStorage.getItem('goguide_max_loan');

    if (savedIncome) {
      const el = document.getElementById('annualIncome');
      if (el) el.value = savedIncome;
    }
    if (savedSavings) {
      const el = document.getElementById('savingsAvailable');
      if (el) el.value = savedSavings;
    }
    if (savedBudget) {
      const el = document.getElementById('annualBudget');
      if (el) el.value = savedBudget;
    }
    if (savedLoan) {
      const el = document.getElementById('maxLoan');
      if (el) el.value = savedLoan;
    }

    // Pre-fill parent preferences fields
    const savedParentRisk = localStorage.getItem('goguide_parent_risk');
    const savedParentEmploy = localStorage.getItem('goguide_parent_employment');

    if (savedParentRisk) {
      const rEl = document.querySelector(`input[name="parent_risk_appetite"][value="${savedParentRisk}"]`);
      if (rEl) rEl.checked = true;
    }
    if (savedParentEmploy) {
      const eEl = document.querySelector(`input[name="parent_early_employment"][value="${savedParentEmploy}"]`);
      if (eEl) eEl.checked = true;
    }
  } catch (err) {
    // Ignore
  }

  // 5. Render 24 Interest Questions & setup GSAP horizontal scroll
  renderInterestAssessment();
  initInterestHorizontalScroll();

  // 6. Render 8 Skill Sliders & setup GSAP entrance animation
  renderSkillSliders();
  initSkillsCardAnimation();

  // 7. GSAP SplitText on All Step Headers (and FAQ)
  initAllStepHeadersSplitText();

  // 8. GSAP Inputs Card Entrance Animation
  initInputsCardAnimation();

  // 9. GSAP Typewriter Animation on Hero Description
  initHeroTypewriter();

  // 10. Step 4 Handlers & Final Submission
  initStep4Handlers();

  // 11. Floating Bottom Navigation Bar (Hidden on landing page, visible on other sections)
  initBottomNavBar();

  // 12. PRISM Engine Results Page
  initResultsEngine();

  // 13. Settings & User Profile Dropdown
  initSettingsDropdown();

  // 14. Dynamic GSAP AI Chatbot Dropdown
  initAiChatDropdown();
});

// GSAP Typewriter Animation for text under GoGuide
function initHeroTypewriter() {
  const descEl = document.querySelector('.hero-description');
  if (!descEl) return;

  const fullText = descEl.textContent.trim().replace(/\s+/g, ' ');
  descEl.setAttribute('aria-label', fullText);
  descEl.innerHTML = '<span class="typewriter-text"></span><span class="typewriter-cursor" aria-hidden="true"></span>';

  const textTarget = descEl.querySelector('.typewriter-text');
  const cursor = descEl.querySelector('.typewriter-cursor');

  if (typeof gsap === 'undefined') {
    textTarget.textContent = fullText;
    return;
  }

  // Realistic blinking cursor with GSAP
  gsap.to(cursor, {
    opacity: 0,
    duration: 0.5,
    repeat: -1,
    yoyo: true,
    ease: 'steps(1)'
  });

  // Typewriter typing effect with GSAP
  const typeState = { charCount: 0 };

  gsap.to(typeState, {
    charCount: fullText.length,
    duration: 3.4,
    delay: 0.45,
    ease: 'none',
    onUpdate: () => {
      const current = Math.floor(typeState.charCount);
      textTarget.textContent = fullText.slice(0, current);
    },
    onComplete: () => {
      textTarget.textContent = fullText;
    }
  });
}

// GSAP SplitText Animation Helper for any heading element
function animateSplitText(headingElement, triggerElement = null) {
  if (!headingElement) return;

  const rawText = headingElement.textContent.trim().replace(/\s+/g, ' ');
  headingElement.setAttribute('aria-label', rawText);
  headingElement.innerHTML = '';

  const words = rawText.split(' ');
  words.forEach((word) => {
    const wordSpan = document.createElement('span');
    wordSpan.className = 'split-word';

    const chars = word.split('');
    chars.forEach((char) => {
      const charSpan = document.createElement('span');
      charSpan.className = 'split-char';
      charSpan.textContent = char;
      wordSpan.appendChild(charSpan);
    });

    headingElement.appendChild(wordSpan);
  });

  if (typeof gsap === 'undefined') return;

  if (typeof ScrollTrigger !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
  }

  const chars = headingElement.querySelectorAll('.split-char');
  const trigger = triggerElement || headingElement;

  // GSAP 3D reveal with elastic bounce and blur clearance
  gsap.fromTo(
    chars,
    {
      opacity: 0,
      y: 40,
      rotateX: -85,
      filter: 'blur(5px)',
      scale: 0.85,
    },
    {
      opacity: 1,
      y: 0,
      rotateX: 0,
      filter: 'blur(0px)',
      scale: 1,
      duration: 0.8,
      ease: 'back.out(1.8)',
      stagger: 0.026,
      scrollTrigger: {
        trigger: trigger,
        start: 'top 85%',
        toggleActions: 'restart none none reverse',
      },
    }
  );
}

// Initialize SplitText GSAP Animation on all Step Headers (and FAQ)
function initAllStepHeadersSplitText() {
  const stepHeadings = [
    { heading: '#studentInputs .section-title', trigger: '#studentInputs' },
    { heading: '#parentInputs .section-title', trigger: '#parentInputs' },
    { heading: '#parentPreferencesSection .section-title', trigger: '#parentPreferencesSection' },
    { heading: '#parentCareersSection .section-title', trigger: '#parentCareersSection' },
    { heading: '#interestSection .section-title', trigger: '#interestSection' },
    { heading: '#skillsSection .section-title', trigger: '#skillsSection' },
    { heading: '#preferencesSection .section-title', trigger: '#preferencesSection' },
    { heading: '#faq .section-title', trigger: '#faq' },
  ];

  stepHeadings.forEach(({ heading, trigger }) => {
    const el = document.querySelector(heading);
    const trigEl = trigger ? document.querySelector(trigger) : el;
    if (el) {
      animateSplitText(el, trigEl);
    }
  });
}

// GSAP Inputs Card Entrance Animation
function initInputsCardAnimation() {
  const cards = document.querySelectorAll('.inputs-card');
  if (!cards.length || typeof gsap === 'undefined') return;

  if (typeof ScrollTrigger !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
  }

  cards.forEach(card => {
    const section = card.closest('section') || card;
    gsap.fromTo(
      card,
      {
        opacity: 0,
        y: 40,
        scale: 0.97,
      },
      {
        opacity: 1,
        y: 0,
        scale: 1,
        duration: 0.9,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: section,
          start: 'top 80%',
          toggleActions: 'play none none none',
        },
      }
    );
  });
}

// Toast notification helper
window.showToast = function (message) {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
      <polyline points="22 4 12 14.01 9 11.01"></polyline>
    </svg>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(15px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3200);
};

// Signup form handler
window.handleSignupSubmit = function () {
  const nameInput = document.getElementById('fullName');
  const emailInput = document.getElementById('email');
  const name = nameInput && nameInput.value.trim() ? nameInput.value.trim() : 'Alex Morgan';
  const email = emailInput && emailInput.value.trim() ? emailInput.value.trim() : 'alex.morgan@goguide.ai';
  const signupDialog = document.getElementById('signupDialog');

  try {
    localStorage.setItem('goguide_user_name', name);
    localStorage.setItem('goguide_user_email', email);
    localStorage.setItem('goguide_is_logged_in', 'true');
  } catch (err) {
    console.warn('Storage unavailable:', err);
  }

  if (typeof window.updateDropdownUser === 'function') {
    window.updateDropdownUser();
  }

  if (signupDialog) signupDialog.close();
  window.showToast(`Welcome aboard, ${name}! Logged in successfully.`, 'success');

  const form = document.getElementById('signupForm');
  if (form) form.reset();
};

// ==========================================================================
// Parent Expected Careers Catalog & Selection Logic (3–5 careers)
// ==========================================================================
const PARENT_CAREER_OPTIONS = [
  { id: 'swe', name: 'Software Engineer', icon: '💻' },
  { id: 'ds_ai', name: 'AI & Data Scientist', icon: '🤖' },
  { id: 'doctor', name: 'Medical Doctor / Surgeon', icon: '🩺' },
  { id: 'civil_services', name: 'Civil Services / IAS / IPS', icon: '🏛️' },
  { id: 'ca_fin', name: 'Chartered Accountant / Fin. Analyst', icon: '📊' },
  { id: 'corp_law', name: 'Corporate Lawyer / Legal Counsel', icon: '⚖️' },
  { id: 'pm', name: 'Product Manager', icon: '🚀' },
  { id: 'cloud_sec', name: 'Cybersecurity & Cloud Architect', icon: '🛡️' },
  { id: 'biotech', name: 'Biotechnologist / Geneticist', icon: '🧬' },
  { id: 'mech_aero', name: 'Mechanical / Aerospace Engineer', icon: '✈️' },
  { id: 'investment_bank', name: 'Investment Banker / VC', icon: '💼' },
  { id: 'architect', name: 'Architect & Urban Planner', icon: '📐' },
  { id: 'academic', name: 'University Professor / Researcher', icon: '🎓' },
  { id: 'ui_ux', name: 'UI/UX & Creative Director', icon: '🎨' },
  { id: 'entrepreneur', name: 'Entrepreneur & Startup Founder', icon: '⚡' }
];

let selectedParentCareersSet = new Set();

function renderParentCareers() {
  const grid = document.getElementById('parentCareersGrid');
  if (!grid) return;

  grid.innerHTML = '';

  // Retrieve saved careers if any
  try {
    const saved = localStorage.getItem('goguide_parent_careers');
    if (saved) {
      const arr = JSON.parse(saved);
      if (Array.isArray(arr)) {
        selectedParentCareersSet = new Set(arr);
      }
    }
  } catch (e) {
    // Ignore JSON parse errors
  }

  PARENT_CAREER_OPTIONS.forEach(career => {
    const chip = document.createElement('div');
    const isSelected = selectedParentCareersSet.has(career.name);
    chip.className = `career-chip ${isSelected ? 'selected' : ''}`;
    chip.dataset.name = career.name;
    chip.setAttribute('role', 'checkbox');
    chip.setAttribute('aria-checked', isSelected ? 'true' : 'false');
    chip.innerHTML = `
      <span class="chip-icon">${career.icon}</span>
      <span class="chip-label">${career.name}</span>
      <span class="chip-check">&#10003;</span>
    `;

    chip.addEventListener('click', () => toggleParentCareer(career.name, chip));
    grid.appendChild(chip);
  });

  updateParentCareerCounter();
}

function toggleParentCareer(careerName, chipEl) {
  if (selectedParentCareersSet.has(careerName)) {
    selectedParentCareersSet.delete(careerName);
    chipEl.classList.remove('selected');
    chipEl.setAttribute('aria-checked', 'false');
  } else {
    if (selectedParentCareersSet.size >= 5) {
      window.showToast('You can select a maximum of 5 careers.');
      return;
    }
    selectedParentCareersSet.add(careerName);
    chipEl.classList.add('selected');
    chipEl.setAttribute('aria-checked', 'true');
  }

  updateParentCareerCounter();
}

function updateParentCareerCounter() {
  const badge = document.getElementById('careerSelectionCountBadge');
  if (!badge) return;

  const count = selectedParentCareersSet.size;
  badge.textContent = `${count} of 3–5 selected`;

  if (count >= 3 && count <= 5) {
    badge.classList.add('valid');
  } else {
    badge.classList.remove('valid');
  }
}

window.getSelectedParentCareers = function () {
  return Array.from(selectedParentCareersSet);
};

// ==========================================================================
// 24 Interest-Assessment Questions & Horizontal GSAP Cycling
// ==========================================================================

const INTEREST_QUESTIONS = [
  { id: 'q1', category: 'Mathematics & Logic', text: 'Solving mathematical puzzles and equations' },
  { id: 'q2', category: 'Software & Automation', text: 'Writing code or scripts to automate tasks' },
  { id: 'q3', category: 'Design & Aesthetics', text: 'Designing graphics, layouts, or user interfaces' },
  { id: 'q4', category: 'Scientific Discovery', text: 'Conducting scientific experiments in a laboratory' },
  { id: 'q5', category: 'Writing & Journalism', text: 'Reading and writing articles, essays, or stories' },
  { id: 'q6', category: 'Data & Statistics', text: 'Analysing data trends and building visual dashboards' },
  { id: 'q7', category: 'Hardware & Circuits', text: 'Building or repairing electronic devices and chips' },
  { id: 'q8', category: 'Healthcare & Medicine', text: 'Researching medical conditions and novel treatments' },
  { id: 'q9', category: 'Leadership & Management', text: 'Managing projects, schedules, and multidisciplinary teams' },
  { id: 'q10', category: 'Product & Web Apps', text: 'Developing full-stack mobile or web applications' },
  { id: 'q11', category: 'Teaching & Mentorship', text: 'Teaching or explaining complex technical topics to others' },
  { id: 'q12', category: 'Fine Arts & Illustration', text: 'Drawing, digital painting, or visual conceptual art' },
  { id: 'q13', category: 'Mechanical Systems', text: 'Working with mechanical systems, robotics, and machinery' },
  { id: 'q14', category: 'Business & Ventures', text: 'Understanding how modern businesses operate, scale, and grow' },
  { id: 'q15', category: 'Astronomy & Physics', text: 'Exploring outer space, astronomy, or theoretical physics' },
  { id: 'q16', category: 'Human Behavior', text: 'Helping people solve personal, career, or social challenges' },
  { id: 'q17', category: 'History & Culture', text: 'Learning about world history, civilisations, and cultural shifts' },
  { id: 'q18', category: 'Artificial Intelligence', text: 'Developing AI, neural networks, or machine learning models' },
  { id: 'q19', category: 'Performing Arts', text: 'Performing through music, theatre, composition, or cinema' },
  { id: 'q20', category: 'Ecology & Biology', text: 'Studying natural ecosystems, plant genetics, or biodiversity' },
  { id: 'q21', category: 'Law & Ethics', text: 'Investigating legal disputes, public policy, and ethics' },
  { id: 'q22', category: 'Architecture & Spaces', text: 'Creating architectural structures, interiors, or urban plans' },
  { id: 'q23', category: 'Financial Markets', text: 'Working with financial portfolios, investment budgets, or trading' },
  { id: 'q24', category: 'Applied Innovation', text: 'Pioneering breakthrough research to solve an unsolved world problem' }
];

const RATING_DESCRIPTIONS = {
  '1': 'Not at all interested',
  '2': 'Slightly interested',
  '3': 'Moderately interested',
  '4': 'Very interested',
  '5': 'Extremely passionate'
};

// Render the 24 cards using user-specified .radio-input markup
function renderInterestAssessment() {
  const track = document.getElementById('interestTrack');
  if (!track || track.children.length > 0) return;

  INTEREST_QUESTIONS.forEach((q, idx) => {
    const card = document.createElement('div');
    card.className = 'interest-card';
    card.id = `interestCard_${idx + 1}`;
    card.setAttribute('data-index', idx + 1);

    // Retrieve saved value if available
    const savedVal = localStorage.getItem(`goguide_interest_${q.id}`) || '';

    card.innerHTML = `
      <div class="interest-card-top">
        <span class="card-category-tag">${q.category}</span>
        <span class="card-q-index">Q${String(idx + 1).padStart(2, '0')} / 24</span>
      </div>

      <div class="interest-card-body">
        <h3 class="interest-question-title">${q.text}</h3>

        <div class="scale-prompt">
          <span class="scale-prompt-lo">1 = Not at all</span>
          <span class="scale-prompt-hi">5 = Very much</span>
        </div>

        <!-- User-specified radio-input scale structure -->
        <div class="radio-input" role="radiogroup" aria-label="Rating scale 1 to 5 for Question ${idx + 1}">
          ${[1, 2, 3, 4, 5].map(val => `
            <label class="label" for="${q.id}_val_${val}">
              <input value="${val}" name="interest_${q.id}" id="${q.id}_val_${val}" type="radio" ${savedVal === String(val) ? 'checked' : ''} />
              <span class="text">${val}</span>
            </label>
          `).join('')}
        </div>
      </div>
    `;

    track.appendChild(card);
  });

  // Event listener for radio scale selection
  track.addEventListener('change', (e) => {
    if (e.target && e.target.type === 'radio') {
      const qName = e.target.name.replace('interest_', '');
      const value = e.target.value;

      try {
        localStorage.setItem(`goguide_interest_${qName}`, value);
      } catch (err) {
        // Storage failover
      }

      updateInterestAnsweredCount();
    }
  });

  updateInterestAnsweredCount();
}

// Update the answered question counter
function updateInterestAnsweredCount() {
  let count = 0;
  INTEREST_QUESTIONS.forEach(q => {
    if (localStorage.getItem(`goguide_interest_${q.id}`)) count++;
  });

  const pill = document.getElementById('interestAnsweredPill');
  if (pill) {
    pill.textContent = `${count} / 24 answered`;
    if (count === 24) {
      pill.style.color = '#34d399';
    }
  }
}

// GSAP Horizontal Pinning and Scrubbing
let horizontalScrollTriggerInstance = null;
let horizontalTweenInstance = null;

function initInterestHorizontalScroll() {
  const section = document.getElementById('interestSection');
  const track = document.getElementById('interestTrack');
  if (!section || !track) return;
  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;

  gsap.registerPlugin(ScrollTrigger);

  // Synchronize ScrollTrigger measurements
  ScrollTrigger.refresh();

  const getScrollDist = () => {
    return Math.max(0, track.scrollWidth - window.innerWidth + 120);
  };

  // Calibrate ultra-smooth vertical scroll travel: ~600px per card (significantly reduces horizontal scroll speed)
  const totalCards = track.querySelectorAll('.interest-card').length || 24;
  const totalScrollDistance = totalCards * 600;

  horizontalTweenInstance = gsap.to(track, {
    x: () => -getScrollDist(),
    ease: 'none',
    scrollTrigger: {
      trigger: section,
      start: 'top top',
      end: () => `+=${totalScrollDistance}`,
      pin: true,
      pinSpacing: true,
      anticipatePin: 1, // Eliminates jump upon entering pinned section
      scrub: 1.2, // Ultra-smooth, gentle horizontal scroll dampening
      invalidateOnRefresh: true,
      onUpdate: (self) => {
        const total = 24;
        const currentCard = Math.min(total, Math.max(1, Math.round(self.progress * (total - 1)) + 1));
        const badge = document.getElementById('currentQBadge');
        if (badge) badge.textContent = `Question ${currentCard} of ${total}`;

        const fill = document.getElementById('interestProgressFill');
        if (fill) fill.style.width = `${Math.max(4, Math.round(self.progress * 100))}%`;
      }
    }
  });

  horizontalScrollTriggerInstance = horizontalTweenInstance.scrollTrigger;

  // Arrow button handlers
  const prevBtn = document.getElementById('prevQuestionBtn');
  const nextBtn = document.getElementById('nextQuestionBtn');

  prevBtn?.addEventListener('click', () => window.stepInterestCard(-1));
  nextBtn?.addEventListener('click', () => window.stepInterestCard(1));
}

// Helper to step between cards horizontally via smooth GSAP animation
window.stepInterestCard = function (direction) {
  const track = document.getElementById('interestTrack');
  if (!track || !horizontalScrollTriggerInstance) return;

  const card = track.querySelector('.interest-card');
  const stepSize = card ? card.offsetWidth + 36 : 440;
  const totalDist = Math.max(0, track.scrollWidth - window.innerWidth + 120);
  if (totalDist <= 0) return;

  const currentX = Math.abs(gsap.getProperty(track, 'x') || 0);
  const targetX = Math.max(0, Math.min(totalDist, currentX + direction * stepSize));
  const targetProgress = targetX / totalDist;
  const st = horizontalScrollTriggerInstance;
  const targetScrollY = st.start + targetProgress * (st.end - st.start);

  gsap.to(window, {
    scrollTo: {
      y: targetScrollY,
      autoKill: false,
    },
    duration: 0.55,
    ease: 'power2.out',
    overwrite: 'auto',
  });
};

// ==========================================================================
// Step 3: 8 Skill Ratings (Metallic Depth Cards + Monochrome Block Slider)
// ==========================================================================

const SKILLS = [
  { id: 'mathematics', label: 'Mathematics', icon: '📐' },
  { id: 'statistics', label: 'Statistics', icon: '📊' },
  { id: 'programming', label: 'Programming', icon: '💻' },
  { id: 'logic', label: 'Logic', icon: '🧩' },
  { id: 'communication', label: 'Communication', icon: '🗣️' },
  { id: 'design', label: 'Design', icon: '🎨' },
  { id: 'biology', label: 'Biology', icon: '🧬' },
  { id: 'electronics', label: 'Electronics', icon: '⚡' },
];

const SKILL_LEVELS = [
  { max: 15, label: 'Novice', color: '#94a3b8', bg: 'rgba(148, 163, 184, 0.2)' },
  { max: 35, label: 'Beginner', color: '#f87171', bg: 'rgba(248, 113, 113, 0.2)' },
  { max: 55, label: 'Developing', color: '#fbbf24', bg: 'rgba(251, 191, 36, 0.2)' },
  { max: 75, label: 'Intermediate', color: '#06b6d4', bg: 'rgba(6, 182, 212, 0.2)' },
  { max: 90, label: 'Proficient', color: '#818cf8', bg: 'rgba(129, 140, 248, 0.2)' },
  { max: 100, label: 'Expert', color: '#34d399', bg: 'rgba(52, 211, 153, 0.2)' },
];

// Grayscale Monochrome Shades for the 10 Block Steps (10% to 100%)
const MONO_SHADES = [
  '#1e293b',
  '#334155',
  '#475569',
  '#64748b',
  '#94a3b8',
  '#cbd5e1',
  '#e2e8f0',
  '#f1f5f9',
  '#f8fafc',
  '#ffffff'
];

function getSkillTier(val) {
  return SKILL_LEVELS.find(lvl => val <= lvl.max) || SKILL_LEVELS[SKILL_LEVELS.length - 1];
}

function renderSkillSliders() {
  const grid = document.getElementById('skillsGrid');
  if (!grid || grid.children.length > 0) return;

  SKILLS.forEach(skill => {
    const savedVal = localStorage.getItem(`goguide_skill_${skill.id}`) || '50';
    const initVal = parseInt(savedVal, 10);

    const card = document.createElement('div');
    card.className = 'card-container';
    card.id = `skillCard_${skill.id}`;

    const blocksHtml = MONO_SHADES.map((shade, idx) => {
      const stepVal = (idx + 1) * 10;
      return `
        <button
          type="button"
          class="item-color ${stepVal <= initVal ? 'active' : 'inactive'}"
          style="--color: ${shade}"
          aria-color="${stepVal}%"
          data-value="${stepVal}"
          data-skill="${skill.id}"
          title="${skill.label}: ${stepVal}%"
        ></button>
      `;
    }).join('');

    card.innerHTML = `
      <div class="skill-header">
        <div class="skill-title-wrap">
          <span class="skill-name">${skill.label}</span>
        </div>
      </div>

      <div class="comic-panel">
        <div class="container-items" id="skillBlocks_${skill.id}">
          ${blocksHtml}
        </div>
      </div>

      <div class="skill-val-row">
        <span>Proficiency Score</span>
        <span class="skill-val-num" id="skillVal_${skill.id}">${initVal} / 100</span>
      </div>
    `;

    grid.appendChild(card);

    const blockContainer = card.querySelector(`#skillBlocks_${skill.id}`);
    blockContainer?.addEventListener('click', (e) => {
      const btn = e.target.closest('.item-color');
      if (!btn) return;

      const val = parseInt(btn.getAttribute('data-value'), 10);
      updateSkillBlockUI(skill.id, val, true);
      try {
        localStorage.setItem(`goguide_skill_${skill.id}`, val);
      } catch (err) { }
    });

    updateSkillBlockUI(skill.id, initVal, false);
  });
}

function updateSkillBlockUI(skillId, val, animate = true) {
  const card = document.getElementById(`skillCard_${skillId}`);
  if (!card) return;

  const valDisplay = card.querySelector(`#skillVal_${skillId}`);
  const buttons = card.querySelectorAll('.item-color');

  buttons.forEach((btn, idx) => {
    const stepVal = (idx + 1) * 10;
    if (stepVal <= val) {
      btn.classList.remove('inactive');
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
      btn.classList.add('inactive');
    }
  });

  if (valDisplay) {
    if (animate && typeof gsap !== 'undefined') {
      const currentVal = parseInt(valDisplay.textContent, 10) || val;
      const state = { current: currentVal };
      gsap.to(state, {
        current: val,
        duration: 0.25,
        ease: 'power1.out',
        onUpdate: () => {
          valDisplay.textContent = `${Math.round(state.current)} / 100`;
        }
      });
    } else {
      valDisplay.textContent = `${val} / 100`;
    }
  }
}

// GSAP ScrollTrigger Entrance Animation for Skill Cards
function initSkillsCardAnimation() {
  const section = document.getElementById('skillsSection');
  const cards = document.querySelectorAll('.card-container');
  if (!section || cards.length === 0 || typeof gsap === 'undefined') return;

  if (typeof ScrollTrigger !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
  }

  gsap.fromTo(
    cards,
    {
      opacity: 0,
      y: 35,
      scale: 0.96,
    },
    {
      opacity: 1,
      y: 0,
      scale: 1,
      duration: 0.7,
      ease: 'back.out(1.3)',
      stagger: 0.08,
      scrollTrigger: {
        trigger: '#skillsSection',
        start: 'top 80%',
        toggleActions: 'play none none none',
      },
    }
  );
}

// Step 3 to Step 4 navigation and Final Generate Roadmap Submission
function initStep4Handlers() {
  // Continue to Step 4 button
  document.getElementById('continueToStep4Btn')?.addEventListener('click', () => {
    smoothScrollTo('#preferencesSection', 1.0);
  });

  // Generate My Roadmap button
  const btn = document.getElementById('generateRoadmapBtn');
  btn?.addEventListener('click', () => {
    // Collect all profile data directly from DOM or localStorage without fake fallbacks
    const stream = document.getElementById('academicStream')?.value || localStorage.getItem('goguide_stream') || null;
    const marksRaw = document.getElementById('marksPercentage')?.value || localStorage.getItem('goguide_marks');
    const marks = marksRaw ? parseFloat(marksRaw) : null;
    const city = document.getElementById('currentCity')?.value || localStorage.getItem('goguide_city') || null;

    // Interests
    const interests = {};
    INTEREST_QUESTIONS.forEach(q => {
      const val = localStorage.getItem(`goguide_interest_${q.id}`);
      if (val !== null && val !== '') {
        interests[q.id] = parseInt(val, 10);
      }
    });

    // Skills
    const skills = {};
    SKILLS.forEach(s => {
      const val = localStorage.getItem(`goguide_skill_${s.id}`);
      if (val !== null && val !== '') {
        skills[s.id] = parseInt(val, 10);
      }
    });

    // Risk tolerance
    const riskChecked = document.querySelector('input[name="risk_tolerance"]:checked');
    const risk = riskChecked ? parseInt(riskChecked.value, 10) : null;

    // Target career
    const targetCareerRaw = document.getElementById('targetCareer')?.value;
    const targetCareer = targetCareerRaw && targetCareerRaw.trim() !== '' ? targetCareerRaw.trim() : null;

    // Financial fields (extract without '0' fallback if empty)
    const incomeRaw = document.getElementById('annualIncome')?.value || localStorage.getItem('goguide_annual_income');
    const savingsRaw = document.getElementById('savingsAvailable')?.value || localStorage.getItem('goguide_savings_available');
    const budgetRaw = document.getElementById('annualBudget')?.value || localStorage.getItem('goguide_annual_budget');
    const maxLoanRaw = document.getElementById('maxLoan')?.value || localStorage.getItem('goguide_max_loan');

    const payload = {
      academic_stream: stream,
      marks_percentage: marks,
      current_city: city,
      interests,
      skills,
      risk_tolerance: risk,
      target_career: targetCareer,
      annual_income: incomeRaw ? parseFloat(incomeRaw) : null,
      savings: savingsRaw ? parseFloat(savingsRaw) : null,
      annual_budget: budgetRaw ? parseFloat(budgetRaw) : null,
      max_loan: maxLoanRaw ? parseFloat(maxLoanRaw) : null,
    };

    console.log('[GoGuide] Final Profile Payload:', payload);

    try {
      localStorage.setItem('goguide_student_profile', JSON.stringify(payload));
    } catch (err) { }

    // Animate button
    const textEl = btn.querySelector('.text');
    if (textEl) textEl.textContent = 'GENERATING ROADMAP…';
    btn.disabled = true;

    // Clear previous results
    CANONICAL_FEASIBLE_CAREERS.length = 0;
    CANONICAL_BLOCKED_CAREERS.length = 0;
    CONFLICT_COMPARISON_DATA.length = 0;
    renderRankedCareers();
    renderBlockedCareers();
    renderConflictTable();

    // Hide results section initially
    const resultsContainer = document.getElementById('resultsSection');
    if (resultsContainer) {
      resultsContainer.style.display = 'none';
    }

    // Build the GuideRequest payload expected by the backend
    const guidePayload = {
      message: "career fit me job consider skill gap pathway degree",
      student_profile: payload,
      parent_profile: null,
    };

    // Attach parent preference vectors if available
    const parentRiskChecked = document.querySelector('input[name="parent_risk_appetite"]:checked');
    const parentRisk = parentRiskChecked ? parentRiskChecked.value : localStorage.getItem('goguide_parent_risk');
    
    const parentEmployChecked = document.querySelector('input[name="parent_early_employment"]:checked');
    const parentEmploy = parentEmployChecked ? parentEmployChecked.value : localStorage.getItem('goguide_parent_employment');
    
    let parentCareers = [];
    try {
      parentCareers = JSON.parse(localStorage.getItem('goguide_parent_careers') || '[]');
    } catch (e) {}

    if (parentRisk || parentEmploy || parentCareers.length > 0) {
      guidePayload.parent_profile = {
        risk_appetite: parentRisk ? parseInt(parentRisk, 10) : null,
        early_employment: parentEmploy ? parseInt(parentEmploy, 10) : null,
        expected_careers: parentCareers,
      };
    }

    console.log('[GoGuide] GuideRequest Payload:', guidePayload);

    // Call real backend endpoint
    fetch('http://127.0.0.1:8001/api/guide', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(guidePayload),
    })
      .then(async res => {
        if (!res.ok) {
          const errText = await res.text().catch(() => '');
          throw new Error(`Backend returned ${res.status}: ${errText}`);
        }
        return res.json();
      })
      .then(data => {
        console.log('[GoGuide] /api/guide response:', data);
        if (data.status === 'AVAILABLE' || data.recommendations) {
          window._guideResponse = data;
          
          // Hide hero and forms
          const heroContent = document.querySelector('.hero-content');
          const studentInputs = document.querySelectorAll('.student-inputs-section, .interest-assessment-section, .skills-assessment-section, .parent-inputs-section, .parent-preferences-section, .parent-careers-section');
          
          if (heroContent) heroContent.style.display = 'none';
          studentInputs.forEach(el => el.style.display = 'none');
          window.scrollTo(0, 0);
          
          // Populate UI with real backend response
          populateResultsFromBackend(data);
          
          // Reveal dashboard
          if (resultsContainer) {
            resultsContainer.style.display = 'block';
            if (typeof ScrollTrigger !== 'undefined') {
              setTimeout(() => ScrollTrigger.refresh(), 100);
            }
          }

          window.showToast('Your personalized PRISM roadmap is ready!', 'success');
          if (textEl) textEl.textContent = '✓ ROADMAP READY!';
        } else {
          throw new Error('API returned UNAVAILABLE');
        }
      })
      .catch(err => {
        console.error('[GoGuide] /api/guide error:', err);
        window.showToast('Failed to generate roadmap. Please check inputs and try again.', 'error');
        if (textEl) textEl.textContent = '⚠ ERROR GENERATING';
      })
      .finally(() => {
        setTimeout(() => {
          if (textEl) textEl.innerHTML = 'GENERATE MY ROADMAP <span class="arrow">&rarr;</span>';
          btn.disabled = false;
        }, 3500);
      });
  });
}

// ==========================================================================
// Floating Isometric Bottom Navigation Bar Implementation
// ==========================================================================
function initBottomNavBar() {
  const container = document.getElementById('bottomNavContainer');
  const heroSection = document.getElementById('home') || document.querySelector('.hero-wrapper');
  if (!container) return;

  const isLandingPage = () => {
    const scrollY = window.pageYOffset || document.documentElement.scrollTop || window.scrollY || 0;

    // Rule 1: Anywhere within the top 120px is unconditionally the landing page
    if (scrollY <= 120) return true;

    const hero = document.getElementById('home') || document.querySelector('.hero-wrapper');
    const step1 = document.getElementById('studentInputs');

    // Rule 2: If Step 1 has not yet reached into the viewport, user is still on the landing page
    if (step1) {
      const step1Rect = step1.getBoundingClientRect();
      if (step1Rect.top > 80) return true;
    }

    // Rule 3: If hero section bottom is still covering significant viewport height
    if (hero) {
      const heroRect = hero.getBoundingClientRect();
      if (heroRect.bottom > 80) return true;
      if (scrollY < (hero.offsetHeight * 0.75)) return true;
    }

    return false;
  };

  const checkVisibility = () => {
    const onLanding = isLandingPage();

    if (onLanding) {
      document.body.classList.add('is-landing-page');
      container.classList.remove('visible');
    } else {
      document.body.classList.remove('is-landing-page');
      container.classList.add('visible');
    }
  };

  window.addEventListener('scroll', checkVisibility, { passive: true });
  window.addEventListener('resize', checkVisibility, { passive: true });
  window.addEventListener('hashchange', checkVisibility, { passive: true });
  document.addEventListener('scroll', checkVisibility, { passive: true });

  // Hook into GSAP ScrollTrigger updates & pin lifecycle so it stays strictly in sync
  if (typeof ScrollTrigger !== 'undefined') {
    ScrollTrigger.addEventListener('scrollEnd', checkVisibility);
    ScrollTrigger.addEventListener('refresh', checkVisibility);
    ScrollTrigger.addEventListener('update', checkVisibility);
  }

  // IntersectionObserver specifically for landing page hero section
  if (heroSection && 'IntersectionObserver' in window) {
    const heroObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && entry.boundingClientRect.bottom > 80) {
          document.body.classList.add('is-landing-page');
          container.classList.remove('visible');
        } else {
          checkVisibility();
        }
      });
    }, {
      threshold: [0, 0.1, 0.25, 0.5, 0.75, 1.0]
    });
    heroObserver.observe(heroSection);
  }

  // Check immediately and continuously upon layout changes
  checkVisibility();
  setTimeout(checkVisibility, 50);
  setTimeout(checkVisibility, 150);
  setTimeout(checkVisibility, 400);
  setTimeout(checkVisibility, 1000);

  // Home Button: Maps to Landing Page (hero at top of page)
  const homeBtn = document.getElementById('bottomNavHomeBtn');
  homeBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    // Instantly hide nav bar before scroll animation begins
    document.body.classList.add('is-landing-page');
    container.classList.remove('visible');

    if (typeof window.smoothScrollTo === 'function') {
      window.smoothScrollTo('#home', 0.9);
    } else {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    if (history.pushState) {
      history.pushState(null, null, '#home');
    } else {
      location.hash = '#home';
    }
  });

  // Footer Back to Top link
  const backToTopLink = document.querySelector('a[href="#home"]');
  backToTopLink?.addEventListener('click', () => {
    document.body.classList.add('is-landing-page');
    container.classList.remove('visible');
  });

  // AI Bot Button: Toggles the dynamic GSAP AI Chatbot Dropdown
  const aiBotBtn = document.getElementById('bottomNavAiBotBtn');
  aiBotBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (typeof window.toggleAiChatDropdown === 'function') {
      window.toggleAiChatDropdown();
    }
  });

  // Results Button: Maps to Results Section
  const resultsBtn = document.getElementById('bottomNavResultsBtn');
  resultsBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    if (typeof window.smoothScrollTo === 'function') {
      window.smoothScrollTo('#resultsSection', 0.9);
    } else {
      document.getElementById('resultsSection')?.scrollIntoView({ behavior: 'smooth' });
    }
    if (history.pushState) {
      history.pushState(null, null, '#resultsSection');
    }
  });

  // Reset Progress button inside Settings dialog
  document.getElementById('clearProgressBtn')?.addEventListener('click', () => {
    const keys = Object.keys(localStorage);
    keys.forEach((k) => {
      if (k.startsWith('goguide_')) {
        localStorage.removeItem(k);
      }
    });
    window.showToast('Progress and responses reset successfully!', 'success');
    settingsDialog?.close();
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  });
}

// ==========================================================================
// Backend Response → Results Population
// Maps /api/guide GuideResponse into existing PRISM results UI
// ==========================================================================

function populateResultsFromBackend(data) {
  if (!data) return;

  // --- Populate LLM answer summary ---
  const answerEl = document.getElementById('prismAnswerSummary');
  if (answerEl && data.answer) {
    answerEl.innerHTML = formatChatMarkdown ? formatChatMarkdown(data.answer) : data.answer;
    answerEl.style.display = 'block';
  }

  // --- Populate recommendations into CANONICAL_FEASIBLE_CAREERS ---
  if (data.recommendations && Array.isArray(data.recommendations) && data.recommendations.length > 0) {
    // Clear the hardcoded array and replace with backend data
    CANONICAL_FEASIBLE_CAREERS.length = 0;

    data.recommendations.forEach((rec, idx) => {
      const career = {
        id: rec.occupation_id || rec.title?.toLowerCase().replace(/[^a-z0-9]+/g, '-') || `career-${idx}`,
        name: rec.title || rec.occupation_id || 'Unknown Career',
        cluster: rec.category || rec.cluster || 'General',
        flags: [],
        fit: typeof rec.fit_score === 'number' ? rec.fit_score : (typeof rec.composite_score === 'number' ? rec.composite_score : 0.5),
        market: typeof rec.market_score === 'number' ? rec.market_score : 0.5,
        fin: typeof rec.financial_score === 'number' ? rec.financial_score : 0.5,
        risk: typeof rec.risk_score === 'number' ? rec.risk_score : 0.5,
        conflict: typeof rec.conflict_score === 'number' ? rec.conflict_score : 0.0,
        total_cost: rec.total_cost || 'Not available',
        savings: rec.savings || 'Not available',
        scholarship: rec.scholarship || 'Not available',
        funding_req: rec.funding_req || 'Not available',
        loan_need: rec.loan_need || 'Not available',
        monthly_emi: rec.monthly_emi || 'Not available',
        emi_ratio: rec.emi_ratio || 'Not available',
        skill_gaps: {
          large: [],
          some: [],
          on_track: [],
        },
        roadmap: [],
        exams: rec.exams || 'Not available',
        scholarships: rec.scholarships || 'Not available',
        adjacent: rec.adjacent || [],
        sources: rec.sources || 'GoGuide Engine',
      };

      // Build flags from available data
      if (rec.composite_score && rec.composite_score > 0.85) career.flags.push('High Match');
      if (rec.demand_label) career.flags.push(rec.demand_label);
      if (rec.category) career.flags.push(rec.category);
      if (career.flags.length === 0) career.flags.push(`Rank #${idx + 1}`);

      CANONICAL_FEASIBLE_CAREERS.push(career);
    });
  }

  // --- Populate skill gap data ---
  if (data.skill_gap && typeof data.skill_gap === 'object') {
    const sg = data.skill_gap;

    // Update the top-ranked career's skill_gaps if we have data
    if (CANONICAL_FEASIBLE_CAREERS.length > 0) {
      const topCareer = CANONICAL_FEASIBLE_CAREERS[0];

      // Map strengths/gaps/unassessed from backend
      if (sg.strengths && Array.isArray(sg.strengths)) {
        topCareer.skill_gaps.on_track = sg.strengths.map(s =>
          typeof s === 'string' ? s : (s.skill || s.name || JSON.stringify(s))
        );
      }
      if (sg.gaps && Array.isArray(sg.gaps)) {
        topCareer.skill_gaps.large = sg.gaps.map(g =>
          typeof g === 'string' ? g : (g.skill || g.name || JSON.stringify(g))
        );
      }
      if (sg.moderate_gaps && Array.isArray(sg.moderate_gaps)) {
        topCareer.skill_gaps.some = sg.moderate_gaps.map(g =>
          typeof g === 'string' ? g : (g.skill || g.name || JSON.stringify(g))
        );
      }
      if (sg.unassessed && Array.isArray(sg.unassessed)) {
        // Append unassessed to "some" gaps category
        const unassessedLabels = sg.unassessed.map(u =>
          typeof u === 'string' ? `${u} (unassessed)` : `${u.skill || u.name || ''} (unassessed)`
        );
        topCareer.skill_gaps.some = topCareer.skill_gaps.some.concat(unassessedLabels);
      }
    }
  }

  // --- Populate pathway data ---
  if (data.pathway && typeof data.pathway === 'object' && data.pathway.status === 'AVAILABLE') {
    const pw = data.pathway;
    if (CANONICAL_FEASIBLE_CAREERS.length > 0) {
      const topCareer = CANONICAL_FEASIBLE_CAREERS[0];

      if (pw.education_pathways && Array.isArray(pw.education_pathways)) {
        topCareer.roadmap = pw.education_pathways.map((ep, i) => ({
          time: ep.duration || `Phase ${i + 1}`,
          title: ep.degree || ep.name || `Pathway ${i + 1}`,
          desc: ep.description || ep.institutions?.join(', ') || 'Details not available',
        }));
      }
      if (pw.entrance_exams && Array.isArray(pw.entrance_exams)) {
        topCareer.exams = pw.entrance_exams.join(', ');
      }
    }
  }

  // --- Populate financial data ---
  if (data.financial && typeof data.financial === 'object') {
    const fin = data.financial;
    if (CANONICAL_FEASIBLE_CAREERS.length > 0) {
      const topCareer = CANONICAL_FEASIBLE_CAREERS[0];
      const getVal = (obj) => {
        if (!obj) return 'Not available';
        if (typeof obj === 'object' && obj.value !== undefined) return obj.value;
        return obj;
      };

      const tc = getVal(fin.total_cost);
      topCareer.total_cost = typeof tc === 'number' ? `₹${(tc / 100000).toFixed(1)} L` : String(tc);
      const fn = getVal(fin.funding_need);
      topCareer.funding_req = typeof fn === 'number' ? `₹${(fn / 100000).toFixed(1)} L` : String(fn);
      topCareer.loan_need = topCareer.funding_req;
      const emi = getVal(fin.monthly_emi);
      topCareer.monthly_emi = typeof emi === 'number' ? `₹${Math.round(emi).toLocaleString('en-IN')} / mo` : String(emi);
      const ar = getVal(fin.affordability_ratio);
      topCareer.emi_ratio = typeof ar === 'number' ? `${(ar * 100).toFixed(1)}%` : String(ar);
      const isFeasible = getVal(fin.is_feasible);
      if (typeof isFeasible === 'boolean') {
        topCareer.fin = isFeasible ? 0.9 : 0.3;
      }
    }
  }

  // --- Populate conflict data ---
  if (data.conflict && typeof data.conflict === 'object') {
    const conf = data.conflict;
    const getVal = (obj) => {
      if (!obj) return null;
      if (typeof obj === 'object' && obj.value !== undefined) return obj.value;
      return obj;
    };
    const ci = getVal(conf.conflict_index);
    if (typeof ci === 'number' && CANONICAL_FEASIBLE_CAREERS.length > 0) {
      // Distribute conflict score to top career
      CANONICAL_FEASIBLE_CAREERS[0].conflict = ci;
    }
  }

  // --- Re-render results with updated data ---
  renderRankedCareers();
  renderBlockedCareers();
  renderConflictTable();

  // --- Populate grounding/sources if there's a place for it ---
  const sourcesEl = document.getElementById('prismSourcesList');
  if (sourcesEl && data.sources && Array.isArray(data.sources)) {
    sourcesEl.innerHTML = data.sources
      .filter(s => s.source && s.source !== 'unknown')
      .map(s => `<span class="source-chip">${s.source}: ${s.value || ''}</span>`)
      .join('');
    if (sourcesEl.innerHTML) sourcesEl.style.display = 'flex';
  }

  // --- Refresh GSAP ScrollTrigger after DOM update ---
  if (typeof ScrollTrigger !== 'undefined') {
    setTimeout(() => ScrollTrigger.refresh(), 300);
  }
}

// ==========================================================================
// PRISM Engine Results Page Implementation
// Strictly adheres to Phase 7.2 PRISM formula, PRD, and Design Specifications
// ==========================================================================

const DEFAULT_PRISM_WEIGHTS = {
  fit: 40,
  market: 30,
  financial: 15,
  risk: 15,
};

let currentPrismWeights = { ...DEFAULT_PRISM_WEIGHTS };

// Feasible Canonical Careers evaluated through PRISM
const CANONICAL_FEASIBLE_CAREERS = [];

// Blocked Careers strictly kept separate from ranked results (Financial Feasibility Gate Failed)
const CANONICAL_BLOCKED_CAREERS = [];

// Per-career alignment data for Conflict View
const CONFLICT_COMPARISON_DATA = [];

function initResultsEngine() {
  updateRailFromStorage();
  renderRankedCareers();
  renderBlockedCareers();
  renderConflictTable();
  setupWeightSliders();
  setupDetailModal();
}

// Update left rail and local card using storage or defaults
function updateRailFromStorage() {
  const stream = localStorage.getItem('goguide_stream') || 'Science – PCM';
  const marks = localStorage.getItem('goguide_marks') || '88.5';
  const city = localStorage.getItem('goguide_city') || 'Mumbai, MH';
  const income = localStorage.getItem('goguide_annual_income') || '1200000';
  const savings = localStorage.getItem('goguide_savings_available') || '500000';

  const streamEl = document.getElementById('railStudentStream');
  if (streamEl) streamEl.textContent = stream;

  const marksEl = document.getElementById('railStudentMarks');
  if (marksEl) marksEl.textContent = `${marks}%`;

  const cityEl = document.getElementById('railStudentCity');
  if (cityEl) cityEl.textContent = city;

  const localCardCity = document.getElementById('localCardCity');
  if (localCardCity) localCardCity.textContent = `📍 ${city} Metropolitan Region`;

  const incomeNum = parseFloat(income);
  const incomeLakh = isNaN(incomeNum) ? '12.0' : (incomeNum / 100000).toFixed(1);
  const incomeEl = document.getElementById('railFamilyIncome');
  if (incomeEl) incomeEl.innerHTML = `&#8377;${incomeLakh} L/yr`;

  const savingsNum = parseFloat(savings);
  const savingsLakh = isNaN(savingsNum) ? '5.0' : (savingsNum / 100000).toFixed(1);
  const savingsEl = document.getElementById('railFamilySavings');
  if (savingsEl) savingsEl.innerHTML = `&#8377;${savingsLakh} L`;
}

// Calculate PRISM score for each career based on normalized weights
function calculatePrismScores(weights) {
  const sum = weights.fit + weights.market + weights.financial + weights.risk;
  const wFit = sum > 0 ? weights.fit / sum : 0.40;
  const wMarket = sum > 0 ? weights.market / sum : 0.30;
  const wFin = sum > 0 ? weights.financial / sum : 0.15;
  const wRisk = sum > 0 ? weights.risk / sum : 0.15;

  return CANONICAL_FEASIBLE_CAREERS.map((career) => {
    // Proportional weighted contributions (0 - 100 scale)
    const fitContrib = wFit * career.fit * 100;
    const marketContrib = wMarket * career.market * 100;
    const finContrib = wFin * career.fin * 100;
    const riskContrib = wRisk * career.risk * 100;
    const conflictDeduct = career.conflict * 100;

    const grossScore = fitContrib + marketContrib + finContrib + riskContrib;
    const netScore = Math.max(0, Math.min(100, Math.round((grossScore - conflictDeduct) * 10) / 10));

    return {
      ...career,
      netScore,
      fitContrib,
      marketContrib,
      finContrib,
      riskContrib,
      conflictDeduct,
      wFit,
      wMarket,
      wFin,
      wRisk,
    };
  });
}

// Render ranked feasible careers list
function renderRankedCareers() {
  const container = document.getElementById('rankedCareersList');
  if (!container) return;

  const scored = calculatePrismScores(currentPrismWeights);
  // Sort descending by net Match Index
  scored.sort((a, b) => b.netScore - a.netScore);

  container.innerHTML = scored
    .map((career, index) => {
      const rank = index + 1;
      const flagsHtml = career.flags
        .map((f) => `<span class="flag-chip">${f}</span>`)
        .join('');

      return `
        <div class="career-row-card" tabindex="0" role="button" aria-label="${career.name}, Match Index ${career.netScore} out of 100" onclick="window.openCareerDetail('${career.id}')" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault(); window.openCareerDetail('${career.id}');}">
          <div class="career-row-top">
            <div class="career-info-group">
              <span class="rank-badge">#${rank}</span>
              <div>
                <div class="career-cluster-name">${career.cluster}</div>
                <h3 class="career-title-text">${career.name}</h3>
                <div class="career-flags-row">${flagsHtml}</div>
              </div>
            </div>
            <div class="career-score-wrap">
              <span class="score-label-text">Match Index</span>
              <div class="score-display-row">
                <span class="score-number">${career.netScore.toFixed(1)}</span>
                <span class="score-scale">/ 100</span>
              </div>
            </div>
          </div>

          <!-- PRISM Component Bar: Visually separates FIT | MARKET | FINANCIAL | RISK with hatched Conflict deduction -->
          <div class="prism-component-bar-wrapper">
            <div class="prism-bar-header">
              <span class="bar-title">PRISM Composite Component Distribution</span>
              <span class="bar-summary">Fit: ${(career.fit * 100).toFixed(0)}% &bull; Market: ${(career.market * 100).toFixed(0)}% &bull; Financial: ${(career.fin * 100).toFixed(0)}% &bull; Risk: ${(career.risk * 100).toFixed(0)}%</span>
            </div>
            <div class="prism-component-bar" aria-label="PRISM Score Distribution">
              <div class="prism-seg prism-seg-fit" style="width: ${career.fitContrib.toFixed(1)}%;" title="Fit Component: ${career.fitContrib.toFixed(1)} pts (${(career.fit * 100).toFixed(0)}% match @ ${(career.wFit * 100).toFixed(0)}% weight)"></div>
              <div class="prism-seg prism-seg-market" style="width: ${career.marketContrib.toFixed(1)}%;" title="Market Component: ${career.marketContrib.toFixed(1)} pts (${(career.market * 100).toFixed(0)}% match @ ${(career.wMarket * 100).toFixed(0)}% weight)"></div>
              <div class="prism-seg prism-seg-financial" style="width: ${career.finContrib.toFixed(1)}%;" title="Financial Component: ${career.finContrib.toFixed(1)} pts (${(career.fin * 100).toFixed(0)}% match @ ${(career.wFin * 100).toFixed(0)}% weight)"></div>
              <div class="prism-seg prism-seg-risk" style="width: ${career.riskContrib.toFixed(1)}%;" title="Risk Component: ${career.riskContrib.toFixed(1)} pts (${(career.risk * 100).toFixed(0)}% match @ ${(career.wRisk * 100).toFixed(0)}% weight)"></div>
              <div class="prism-seg prism-seg-conflict" style="width: ${career.conflictDeduct.toFixed(1)}%;" title="Conflict Deduction: -${career.conflictDeduct.toFixed(1)} pts (-${career.conflict.toFixed(2)})"></div>
            </div>
          </div>

          <!-- Component Score Pills & Detail CTA -->
          <div class="career-metrics-row">
            <div class="component-metrics-group">
              <span class="c-pill pill-fit" title="Fit Score"><span class="c-dot dot-fit"></span> Fit: ${career.fit.toFixed(2)}</span>
              <span class="c-pill pill-market" title="Market Score"><span class="c-dot dot-market"></span> Market: ${career.market.toFixed(2)}</span>
              <span class="c-pill pill-financial" title="Financial Feasibility"><span class="c-dot dot-financial"></span> Financial: ${career.fin.toFixed(2)}</span>
              <span class="c-pill pill-risk" title="Risk Alignment"><span class="c-dot dot-risk"></span> Risk: ${career.risk.toFixed(2)}</span>
              <span class="c-pill pill-conflict" title="Conflict Deduction"><span class="c-dot dot-conflict"></span> Conflict: &minus;${career.conflict.toFixed(2)}</span>
            </div>
            <button type="button" class="view-detail-btn" onclick="event.stopPropagation(); window.openCareerDetail('${career.id}');">
              View Breakdown &amp; Roadmap &rarr;
            </button>
          </div>
        </div>
      `;
    })
    .join('');
}

// Render Blocked Careers (Financial Feasibility Gate Failed)
function renderBlockedCareers() {
  const container = document.getElementById('blockedCareersList');
  if (!container) return;

  container.innerHTML = CANONICAL_BLOCKED_CAREERS.map((b) => {
    return `
      <div class="blocked-career-card">
        <div class="blocked-card-top">
          <div>
            <h4 class="blocked-card-title">${b.name}</h4>
            <span class="blocked-tag">&#10006; Financial Gate Blocked</span>
          </div>
          <div class="blocked-gap-badge">${b.gap}</div>
        </div>
        <p class="blocked-reason-text">${b.reason}</p>
        <p class="blocked-explanation-text">${b.explanation}</p>
      </div>
    `;
  }).join('');
}

// Render Conflict Comparison Table
function renderConflictTable() {
  const tbody = document.getElementById('conflictTableBody');
  if (!tbody) return;

  tbody.innerHTML = CONFLICT_COMPARISON_DATA.map((row) => {
    return `
      <tr>
        <td style="font-weight: 700; color: #ffffff;">${row.career}</td>
        <td><span style="color: #8b93f8; font-weight: 700;">${row.youFit}</span></td>
        <td><span style="color: #38bdf8; font-weight: 700;">${row.parentAffinity}</span></td>
        <td><span style="font-family: monospace; color: #f0f6fc;">${row.diff}</span></td>
        <td><span class="risk-disagreement-tag ${row.riskDisagreement.toLowerCase().replace(/\s+/g, '-')}">${row.riskDisagreement}</span></td>
        <td style="font-size: 0.84rem; color: #8b949e;">${row.note}</td>
      </tr>
    `;
  }).join('');
}

// Setup real-time weight sliders & reset to defaults button
function setupWeightSliders() {
  const sliderFit = document.getElementById('sliderFit');
  const sliderMarket = document.getElementById('sliderMarket');
  const sliderFin = document.getElementById('sliderFinancial');
  const sliderRisk = document.getElementById('sliderRisk');
  const resetBtn = document.getElementById('resetWeightsBtn');

  const fitVal = document.getElementById('fitWeightVal');
  const marketVal = document.getElementById('marketWeightVal');
  const finVal = document.getElementById('financialWeightVal');
  const riskVal = document.getElementById('riskWeightVal');
  const assumptionsDisplay = document.getElementById('assumptionsWeightDisplay');

  const handleSliderChange = () => {
    currentPrismWeights.fit = parseInt(sliderFit?.value || '40', 10);
    currentPrismWeights.market = parseInt(sliderMarket?.value || '30', 10);
    currentPrismWeights.financial = parseInt(sliderFin?.value || '15', 10);
    currentPrismWeights.risk = parseInt(sliderRisk?.value || '15', 10);

    if (fitVal) fitVal.textContent = `${currentPrismWeights.fit}%`;
    if (marketVal) marketVal.textContent = `${currentPrismWeights.market}%`;
    if (finVal) finVal.textContent = `${currentPrismWeights.financial}%`;
    if (riskVal) riskVal.textContent = `${currentPrismWeights.risk}%`;

    if (assumptionsDisplay) {
      assumptionsDisplay.textContent = `${currentPrismWeights.fit} / ${currentPrismWeights.market} / ${currentPrismWeights.financial} / ${currentPrismWeights.risk}`;
    }

    renderRankedCareers();
  };

  [sliderFit, sliderMarket, sliderFin, sliderRisk].forEach((slider) => {
    slider?.addEventListener('input', handleSliderChange);
  });

  // "Back to defaults" resets weights to 40 / 30 / 15 / 15
  resetBtn?.addEventListener('click', () => {
    currentPrismWeights = { ...DEFAULT_PRISM_WEIGHTS };
    if (sliderFit) sliderFit.value = '40';
    if (sliderMarket) sliderMarket.value = '30';
    if (sliderFin) sliderFin.value = '15';
    if (sliderRisk) sliderRisk.value = '15';

    if (fitVal) fitVal.textContent = '40%';
    if (marketVal) marketVal.textContent = '30%';
    if (finVal) finVal.textContent = '15%';
    if (riskVal) riskVal.textContent = '15%';

    if (assumptionsDisplay) {
      assumptionsDisplay.textContent = '40 / 30 / 15 / 15';
    }

    renderRankedCareers();
    window.showToast('Weights reset to standard defaults (40 / 30 / 15 / 15)', 'info');
  });
}

// Setup career detail modal and keyboard listeners
function setupDetailModal() {
  const overlay = document.getElementById('careerDetailOverlay');
  const closeBtn = document.getElementById('closeCareerDetailBtn');

  closeBtn?.addEventListener('click', () => {
    window.closeCareerDetail();
  });

  overlay?.addEventListener('click', (e) => {
    if (e.target === overlay) {
      window.closeCareerDetail();
    }
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && overlay && overlay.style.display !== 'none') {
      window.closeCareerDetail();
    }
  });
}

// Open Career Detail View with full 9-point PRISM breakdown
window.openCareerDetail = function (careerId) {
  const career = CANONICAL_FEASIBLE_CAREERS.find((c) => c.id === careerId) || CANONICAL_FEASIBLE_CAREERS[0];
  const overlay = document.getElementById('careerDetailOverlay');
  if (!overlay || !career) return;

  // Calculate current score with current weights
  const scored = calculatePrismScores(currentPrismWeights).find((c) => c.id === career.id);
  const currentNetScore = scored ? scored.netScore : (career.fit * 40 + career.market * 30 + career.fin * 15 + career.risk * 15 - career.conflict * 100);

  // 1. Career Name + Badges
  const titleEl = document.getElementById('modalCareerTitle');
  if (titleEl) titleEl.textContent = career.name;

  const clusterEl = document.getElementById('modalCareerCluster');
  if (clusterEl) clusterEl.textContent = career.cluster;

  const flagEl = document.getElementById('modalCareerFlag');
  if (flagEl) flagEl.textContent = career.flags[0] || 'High Feasibility';

  // 2. Full PRISM Component Breakdown
  const scoreEl = document.getElementById('modalMatchScore');
  if (scoreEl) scoreEl.textContent = `${currentNetScore.toFixed(1)} / 100`;

  const fitVal = document.getElementById('modalFitVal');
  if (fitVal) fitVal.textContent = career.fit.toFixed(2);

  const marketVal = document.getElementById('modalMarketVal');
  if (marketVal) marketVal.textContent = career.market.toFixed(2);

  const finVal = document.getElementById('modalFinVal');
  if (finVal) finVal.textContent = career.fin.toFixed(2);

  const riskVal = document.getElementById('modalRiskVal');
  if (riskVal) riskVal.textContent = career.risk.toFixed(2);

  const barEl = document.getElementById('modalPrismBar');
  if (barEl && scored) {
    barEl.innerHTML = `
      <div class="prism-seg prism-seg-fit" style="width: ${scored.fitContrib.toFixed(1)}%;" title="Fit: ${scored.fitContrib.toFixed(1)} pts"></div>
      <div class="prism-seg prism-seg-market" style="width: ${scored.marketContrib.toFixed(1)}%;" title="Market: ${scored.marketContrib.toFixed(1)} pts"></div>
      <div class="prism-seg prism-seg-financial" style="width: ${scored.finContrib.toFixed(1)}%;" title="Financial: ${scored.finContrib.toFixed(1)} pts"></div>
      <div class="prism-seg prism-seg-risk" style="width: ${scored.riskContrib.toFixed(1)}%;" title="Risk: ${scored.riskContrib.toFixed(1)} pts"></div>
      <div class="prism-seg prism-seg-conflict" style="width: ${scored.conflictDeduct.toFixed(1)}%;" title="Conflict: -${scored.conflictDeduct.toFixed(1)} pts"></div>
    `;
  }

  // 3. Cost & Funding
  const costEl = document.getElementById('modalTotalCost');
  if (costEl) costEl.textContent = career.total_cost;

  const savingsEl = document.getElementById('modalSavings');
  if (savingsEl) savingsEl.textContent = career.savings;

  const scholarshipEl = document.getElementById('modalScholarship');
  if (scholarshipEl) scholarshipEl.textContent = career.scholarship;

  const fundReqEl = document.getElementById('modalFundingReq');
  if (fundReqEl) fundReqEl.textContent = career.funding_req;

  const loanNeedEl = document.getElementById('modalLoanNeed');
  if (loanNeedEl) loanNeedEl.textContent = career.loan_need;

  const monthlyEmiEl = document.getElementById('modalMonthlyEmi');
  if (monthlyEmiEl) monthlyEmiEl.textContent = career.monthly_emi;

  const emiRatioEl = document.getElementById('modalEmiRatio');
  if (emiRatioEl) emiRatioEl.textContent = career.emi_ratio;

  // 4. Skill Gaps (Large, Some, On Track)
  const largeGapsEl = document.getElementById('modalLargeGaps');
  if (largeGapsEl) {
    largeGapsEl.innerHTML = career.skill_gaps.large
      .map((s) => `<span class="gap-chip">${s}</span>`)
      .join('');
  }

  const someGapsEl = document.getElementById('modalSomeGaps');
  if (someGapsEl) {
    someGapsEl.innerHTML = career.skill_gaps.some
      .map((s) => `<span class="gap-chip">${s}</span>`)
      .join('');
  }

  const onTrackEl = document.getElementById('modalOnTrackSkills');
  if (onTrackEl) {
    onTrackEl.innerHTML = career.skill_gaps.on_track
      .map((s) => `<span class="gap-chip">${s}</span>`)
      .join('');
  }

  // 5. Grounded Action Roadmap (0–3m, 3–6m, 6–12m)
  const timelineEl = document.querySelector('.detail-timeline');
  if (timelineEl && career.roadmap) {
    timelineEl.innerHTML = career.roadmap
      .map((step) => {
        return `
          <div class="timeline-step">
            <div class="timeline-marker">${step.time}</div>
            <div class="timeline-body">
              <strong>${step.title}:</strong> ${step.desc}
            </div>
          </div>
        `;
      })
      .join('');
  }

  // 6. Exams
  const examsEl = document.getElementById('modalExams');
  if (examsEl) examsEl.textContent = career.exams;

  // 7. Scholarships
  const scholarshipsEl = document.getElementById('modalScholarships');
  if (scholarshipsEl) scholarshipsEl.textContent = career.scholarships;

  // 8. Adjacent Careers
  const adjacentEl = document.getElementById('modalAdjacentCareers');
  if (adjacentEl) {
    adjacentEl.innerHTML = career.adjacent
      .map((c) => `<span class="adj-chip">${c}</span>`)
      .join('');
  }

  overlay.style.display = 'flex';
  overlay.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
};

// Close Career Detail View
window.closeCareerDetail = function () {
  const overlay = document.getElementById('careerDetailOverlay');
  if (!overlay) return;
  overlay.style.display = 'none';
  overlay.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
};

// Subnav Tab Switching (Top Matches, Conflict View, Local Opportunity, SWOT Matrix)
window.switchResultsTab = function (tabName) {
  const tabs = [
    { name: 'recommendations', btnId: 'tabRecommendationsBtn', panelId: 'tabRecommendationsPanel' },
    { name: 'conflict', btnId: 'tabConflictBtn', panelId: 'tabConflictPanel' },
    { name: 'local', btnId: 'tabLocalBtn', panelId: 'tabLocalPanel' },
    { name: 'swot', btnId: 'tabSwotBtn', panelId: 'tabSwotPanel' },
  ];

  tabs.forEach((tab) => {
    const btn = document.getElementById(tab.btnId);
    const panel = document.getElementById(tab.panelId);

    if (tab.name === tabName) {
      btn?.classList.add('active');
      btn?.setAttribute('aria-selected', 'true');
      if (panel) {
        panel.style.display = 'block';
        panel.classList.add('active');
      }
    } else {
      btn?.classList.remove('active');
      btn?.setAttribute('aria-selected', 'false');
      if (panel) {
        panel.style.display = 'none';
        panel.classList.remove('active');
      }
    }
  });
};

// ==========================================================================
// Settings & User Profile Dropdown Logic
// Displays Logged-In User Profile, Light/Dark Mode Switcher, and Sign Out/In
// ==========================================================================

function initSettingsDropdown() {
  const dropdown = document.getElementById('settingsDropdown');
  const bottomSettingsBtn = document.getElementById('bottomNavSettingsBtn');
  const heroSettingsBtn = document.getElementById('heroSettingsBtn');
  const themeLightBtn = document.getElementById('themeLightBtn');
  const themeDarkBtn = document.getElementById('themeDarkBtn');
  const themeCurrentLabel = document.getElementById('themeCurrentLabel');
  const authBtn = document.getElementById('dropdownAuthBtn');
  const resetBtn = document.getElementById('dropdownResetBtn');
  const soundToggle = document.getElementById('dropdownSoundToggle');
  const heroBtnText = document.getElementById('heroSettingsBtnText');

  // Initialize theme from storage (default to 'dark')
  const savedTheme = localStorage.getItem('goguide_theme') || 'dark';
  applyTheme(savedTheme, false);

  // Update user info display
  updateDropdownUser();

  // Toggle Dropdown Menu
  function toggleSettingsDropdown(forceState) {
    if (!dropdown) return;
    const isCurrentlyActive = dropdown.classList.contains('active');
    const nextState = typeof forceState === 'boolean' ? forceState : !isCurrentlyActive;

    if (nextState) {
      updateDropdownUser();
      dropdown.classList.add('active');
      dropdown.setAttribute('aria-hidden', 'false');
      bottomSettingsBtn?.setAttribute('aria-expanded', 'true');
      heroSettingsBtn?.setAttribute('aria-expanded', 'true');
    } else {
      dropdown.classList.remove('active');
      dropdown.setAttribute('aria-hidden', 'true');
      bottomSettingsBtn?.setAttribute('aria-expanded', 'false');
      heroSettingsBtn?.setAttribute('aria-expanded', 'false');
    }
  }
  window.toggleSettingsDropdown = toggleSettingsDropdown;

  // Trigger from hero navigation
  heroSettingsBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    toggleSettingsDropdown();
  });

  // Trigger from floating nav
  bottomSettingsBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    toggleSettingsDropdown();
  });

  // Light dismiss on click outside dropdown
  document.addEventListener('click', (e) => {
    if (!dropdown || !dropdown.classList.contains('active')) return;
    const clickedInside = dropdown.contains(e.target);
    const clickedTrigger = (bottomSettingsBtn && bottomSettingsBtn.contains(e.target)) ||
                           (heroSettingsBtn && heroSettingsBtn.contains(e.target));
    if (!clickedInside && !clickedTrigger) {
      toggleSettingsDropdown(false);
    }
  });

  // Close on Escape key
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && dropdown?.classList.contains('active')) {
      toggleSettingsDropdown(false);
    }
  });

  // Theme Switcher Handlers (Light / Dark Mode)
  function applyTheme(theme, notify = true) {
    if (theme === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
      document.body.setAttribute('data-theme', 'light');
      themeLightBtn?.classList.add('active');
      themeLightBtn?.setAttribute('aria-checked', 'true');
      themeDarkBtn?.classList.remove('active');
      themeDarkBtn?.setAttribute('aria-checked', 'false');
      if (themeCurrentLabel) themeCurrentLabel.textContent = 'Light';
    } else {
      document.documentElement.removeAttribute('data-theme');
      document.body.removeAttribute('data-theme');
      document.documentElement.setAttribute('data-theme', 'dark');
      document.body.setAttribute('data-theme', 'dark');
      themeDarkBtn?.classList.add('active');
      themeDarkBtn?.setAttribute('aria-checked', 'true');
      themeLightBtn?.classList.remove('active');
      themeLightBtn?.setAttribute('aria-checked', 'false');
      if (themeCurrentLabel) themeCurrentLabel.textContent = 'Dark';
    }

    try {
      localStorage.setItem('goguide_theme', theme);
    } catch (err) {}

    if (notify) {
      window.showToast(`Theme switched to ${theme === 'light' ? 'Light' : 'Dark'} mode`, 'info');
    }
  }

  themeLightBtn?.addEventListener('click', () => applyTheme('light', true));
  themeDarkBtn?.addEventListener('click', () => applyTheme('dark', true));

  // Update user info display (logged in user vs guest)
  function updateDropdownUser() {
    const isLoggedIn = localStorage.getItem('goguide_is_logged_in') !== 'false';
    const userName = localStorage.getItem('goguide_user_name') || 'Alex Morgan';
    const userEmail = localStorage.getItem('goguide_user_email') || 'alex.morgan@goguide.ai';
    const stream = localStorage.getItem('goguide_stream') || 'Science – PCM';

    const avatarEl = document.getElementById('dropdownAvatar');
    const statusDot = document.getElementById('dropdownStatusDot');
    const nameEl = document.getElementById('dropdownUserName');
    const badgeEl = document.getElementById('dropdownUserBadge');
    const emailEl = document.getElementById('dropdownUserEmail');
    const roleEl = document.getElementById('dropdownUserRole');
    const authBtnText = document.getElementById('dropdownAuthText');

    if (isLoggedIn) {
      if (nameEl) nameEl.textContent = userName;
      if (emailEl) emailEl.textContent = userEmail;
      if (roleEl) roleEl.textContent = `Student • ${stream}`;

      // Initials for avatar
      const initials = userName
        .split(' ')
        .filter(Boolean)
        .map((part) => part[0])
        .join('')
        .slice(0, 2)
        .toUpperCase() || 'AM';

      if (avatarEl) {
        avatarEl.textContent = initials;
        avatarEl.classList.remove('guest');
      }

      if (statusDot) {
        statusDot.className = 'settings-status-dot online';
        statusDot.title = 'Status: Online';
      }

      if (badgeEl) {
        badgeEl.textContent = 'Active';
        badgeEl.className = 'settings-badge';
      }

      if (authBtn) {
        authBtn.className = 'settings-auth-btn sign-out';
      }
      if (authBtnText) authBtnText.textContent = 'Sign Out';

      if (heroBtnText) heroBtnText.textContent = userName.split(' ')[0] || 'Settings';
    } else {
      // Guest / Signed out state
      if (nameEl) nameEl.textContent = 'Guest User';
      if (emailEl) emailEl.textContent = 'Not signed in';
      if (roleEl) roleEl.textContent = 'Explore GoGuide as a guest';

      if (avatarEl) {
        avatarEl.innerHTML = '&#128100;';
        avatarEl.classList.add('guest');
      }

      if (statusDot) {
        statusDot.className = 'settings-status-dot offline';
        statusDot.title = 'Status: Signed Out';
      }

      if (badgeEl) {
        badgeEl.textContent = 'Guest';
        badgeEl.className = 'settings-badge guest';
      }

      if (authBtn) {
        authBtn.className = 'settings-auth-btn sign-in';
      }
      if (authBtnText) authBtnText.textContent = 'Sign In / Register';

      if (heroBtnText) heroBtnText.textContent = 'Settings';
    }
  }
  window.updateDropdownUser = updateDropdownUser;

  // Sign Out / Sign In action click
  authBtn?.addEventListener('click', () => {
    const isLoggedIn = localStorage.getItem('goguide_is_logged_in') !== 'false';
    if (isLoggedIn) {
      // Perform sign out
      try {
        localStorage.setItem('goguide_is_logged_in', 'false');
      } catch (err) {}
      updateDropdownUser();
      window.showToast('You have signed out. Browsing as Guest.', 'info');
    } else {
      // Prompt sign in via signup dialog
      toggleSettingsDropdown(false);
      const signupDialog = document.getElementById('signupDialog');
      if (signupDialog && typeof signupDialog.showModal === 'function') {
        signupDialog.showModal();
      }
    }
  });

  // Sound Feedback Toggle
  soundToggle?.addEventListener('change', (e) => {
    const isChecked = e.target.checked;
    window.showToast(`Sound cues ${isChecked ? 'enabled' : 'disabled'}.`, 'info');
  });

  // Reset Assessment Progress button
  resetBtn?.addEventListener('click', () => {
    const confirmed = confirm('Are you sure you want to reset your academic and parent preferences?');
    if (!confirmed) return;

    const keys = Object.keys(localStorage);
    keys.forEach((k) => {
      if (k.startsWith('goguide_') && k !== 'goguide_theme' && k !== 'goguide_user_name' && k !== 'goguide_user_email' && k !== 'goguide_is_logged_in') {
        localStorage.removeItem(k);
      }
    });
    window.showToast('Assessment progress reset successfully!', 'success');
    toggleSettingsDropdown(false);
    setTimeout(() => {
      window.location.reload();
    }, 900);
  });
}

// ==========================================================================
// Dynamic GSAP AI Chatbot Dropdown Implementation
// Features: GSAP Entrance/Exit, Pulsating Indicators, Staggered Chips,
// Word-Streaming Typewriter Effect, and Grounded PRISM Context Responses
// ==========================================================================

function initAiChatDropdown() {
  const dropdown = document.getElementById('aiChatDropdown');
  const bottomAiBtn = document.getElementById('bottomNavAiBotBtn');
  const heroAiBtn = document.getElementById('heroAiBotBtn');
  const closeBtn = document.getElementById('aiCloseChatBtn');
  const clearBtn = document.getElementById('aiClearChatBtn');
  const messagesContainer = document.getElementById('aiChatMessages');
  const typingIndicator = document.getElementById('aiTypingIndicator');
  const chatForm = document.getElementById('aiChatForm');
  const chatInput = document.getElementById('aiChatInput');
  const quickChips = document.getElementById('aiQuickChips');

  let isAiResponding = false;

  // Hydrate context bar with student's profile & top match
  function updateAiContextBar() {
    const stream = localStorage.getItem('goguide_stream');
    const marks = localStorage.getItem('goguide_marks');
    const contextStudent = document.getElementById('aiContextStudent');
    const contextScore = document.getElementById('aiContextScore');
    const contextMatch = document.getElementById('aiContextMatch');

    if (contextStudent) {
      if (stream) {
        contextStudent.textContent = stream;
        contextStudent.style.display = 'inline-flex';
      } else {
        contextStudent.style.display = 'none';
      }
    }

    if (contextScore) {
      if (marks) {
        contextScore.textContent = `${marks}% Score`;
        contextScore.style.display = 'inline-flex';
      } else {
        contextScore.style.display = 'none';
      }
    }

    if (contextMatch) {
      if (window._guideResponse && window._guideResponse.recommendations && window._guideResponse.recommendations.length > 0) {
        let title = window._guideResponse.recommendations[0].title || 'Unknown';
        // Truncate if too long
        if (title.length > 15) title = title.substring(0, 15) + '...';
        contextMatch.textContent = `#1 Match: ${title}`;
        contextMatch.style.display = 'inline-flex';
      } else {
        contextMatch.style.display = 'none';
      }
    }
  }

  // Open Dropdown with GSAP Spring Entrance
  function openAiChatDropdown() {
    if (!dropdown) return;

    // Close settings dropdown if active to prevent overlapping
    if (typeof window.toggleSettingsDropdown === 'function') {
      window.toggleSettingsDropdown(false);
    }

    updateAiContextBar();
    dropdown.style.display = 'flex';

    if (typeof gsap !== 'undefined') {
      gsap.fromTo(
        dropdown,
        {
          opacity: 0,
          scale: 0.86,
          y: -24,
          transformOrigin: 'top right',
        },
        {
          opacity: 1,
          scale: 1,
          y: 0,
          duration: 0.42,
          ease: 'back.out(1.4)',
          onStart: () => {
            dropdown.classList.add('active');
            dropdown.setAttribute('aria-hidden', 'false');
            bottomAiBtn?.setAttribute('aria-expanded', 'true');
            heroAiBtn?.setAttribute('aria-expanded', 'true');
          },
          onComplete: () => {
            chatInput?.focus();
          },
        }
      );

      // Stagger animate suggestion chips
      const chips = dropdown.querySelectorAll('.chat-quick-chip');
      if (chips.length > 0) {
        gsap.fromTo(
          chips,
          { opacity: 0, y: 12, scale: 0.94 },
          { opacity: 1, y: 0, scale: 1, duration: 0.3, stagger: 0.05, ease: 'power2.out', delay: 0.1 }
        );
      }

      // Pulsating glowing green status badge
      gsap.to('.ai-pulse-dot', {
        scale: 1.5,
        opacity: 0.35,
        duration: 0.85,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut',
      });
    } else {
      dropdown.classList.add('active');
      dropdown.setAttribute('aria-hidden', 'false');
      chatInput?.focus();
    }
  }

  // Close Dropdown with GSAP
  function closeAiChatDropdown() {
    if (!dropdown || !dropdown.classList.contains('active')) return;

    if (typeof gsap !== 'undefined') {
      gsap.to(dropdown, {
        opacity: 0,
        scale: 0.88,
        y: -18,
        duration: 0.22,
        ease: 'power2.in',
        onComplete: () => {
          dropdown.classList.remove('active');
          dropdown.setAttribute('aria-hidden', 'true');
          dropdown.style.display = 'none';
          bottomAiBtn?.setAttribute('aria-expanded', 'false');
          heroAiBtn?.setAttribute('aria-expanded', 'false');
        },
      });
    } else {
      dropdown.classList.remove('active');
      dropdown.setAttribute('aria-hidden', 'true');
      dropdown.style.display = 'none';
    }
  }

  // Toggle Dropdown
  function toggleAiChatDropdown() {
    if (dropdown?.classList.contains('active')) {
      closeAiChatDropdown();
    } else {
      openAiChatDropdown();
    }
  }
  window.toggleAiChatDropdown = toggleAiChatDropdown;

  // Event Listeners for Open / Close
  heroAiBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    toggleAiChatDropdown();
  });

  closeBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    closeAiChatDropdown();
  });

  // Light dismiss on click outside
  document.addEventListener('click', (e) => {
    if (!dropdown || !dropdown.classList.contains('active')) return;
    const clickedInside = dropdown.contains(e.target);
    const clickedTrigger =
      (bottomAiBtn && bottomAiBtn.contains(e.target)) ||
      (heroAiBtn && heroAiBtn.contains(e.target));
    if (!clickedInside && !clickedTrigger) {
      closeAiChatDropdown();
    }
  });

  // Close on Escape key
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && dropdown?.classList.contains('active')) {
      closeAiChatDropdown();
    }
  });

  // Quick Chips Click Handlers
  quickChips?.addEventListener('click', (e) => {
    const chip = e.target.closest('.chat-quick-chip');
    if (!chip || isAiResponding) return;
    const prompt = chip.getAttribute('data-prompt') || chip.textContent.trim();
    sendUserMessage(prompt);
  });

  // Chat Form Submit Handler
  function handleAiChatSubmit() {
    if (!chatInput || isAiResponding) return;
    const text = chatInput.value.trim();
    if (!text) return;
    chatInput.value = '';
    sendUserMessage(text);
  }
  window.handleAiChatSubmit = handleAiChatSubmit;
  
  if (chatForm) {
    chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      handleAiChatSubmit();
    });
  }

  // Send User Message & Trigger Grounded Response
  function sendUserMessage(text) {
    if (!messagesContainer || isAiResponding) return;

    // Retrieve user initial
    const userName = localStorage.getItem('goguide_user_name') || 'Alex Morgan';
    const initials = userName
      .split(' ')
      .filter(Boolean)
      .map((p) => p[0])
      .join('')
      .slice(0, 2)
      .toUpperCase() || 'AM';

    // Hide quick chips with smooth GSAP fade
    if (quickChips && quickChips.style.display !== 'none') {
      if (typeof gsap !== 'undefined') {
        gsap.to(quickChips, {
          opacity: 0,
          height: 0,
          margin: 0,
          duration: 0.25,
          onComplete: () => {
            quickChips.style.display = 'none';
          },
        });
      } else {
        quickChips.style.display = 'none';
      }
    }

    // Create User Message Bubble
    const userMsgEl = document.createElement('div');
    userMsgEl.className = 'chat-msg user-msg';
    userMsgEl.innerHTML = `
      <div class="msg-avatar">${initials}</div>
      <div class="msg-bubble"><p>${escapeHtml(text)}</p></div>
    `;

    // Insert before typing indicator
    if (typingIndicator) {
      messagesContainer.insertBefore(userMsgEl, typingIndicator);
    } else {
      messagesContainer.appendChild(userMsgEl);
    }

    // GSAP message entrance animation
    if (typeof gsap !== 'undefined') {
      gsap.fromTo(
        userMsgEl,
        { opacity: 0, y: 16, scale: 0.94 },
        { opacity: 1, y: 0, scale: 1, duration: 0.28, ease: 'power2.out' }
      );
      gsap.to(messagesContainer, {
        scrollTop: messagesContainer.scrollHeight,
        duration: 0.35,
        ease: 'power2.out',
      });
    } else {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Show Typing Indicator with GSAP bouncing dots
    isAiResponding = true;
    if (typingIndicator) {
      typingIndicator.style.display = 'flex';
      const dots = typingIndicator.querySelectorAll('.typing-dot');
      if (typeof gsap !== 'undefined') {
        gsap.killTweensOf(dots);
        gsap.fromTo(
          dots,
          { y: 0 },
          { y: -6, duration: 0.3, stagger: 0.1, repeat: -1, yoyo: true, ease: 'power1.inOut' }
        );
        gsap.to(messagesContainer, {
          scrollTop: messagesContainer.scrollHeight,
          duration: 0.3,
          ease: 'power2.out',
        });
      }
    }

    // Call backend Quick Doubts API
    generateAiResponse(text);
  }

  // Generate Intelligent Grounded Response based on query
  async function generateAiResponse(userQuery) {
    let reply = '';
    try {
      const response = await fetch('http://127.0.0.1:8001/api/quick-doubts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userQuery }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.status === 'AVAILABLE' && data.answer) {
        reply = data.answer;
      } else {
        reply = data.message || "Quick Doubts is temporarily unavailable.";
      }
    } catch (err) {
      console.error('[GoGuide] Quick Doubts API Error:', err);
      reply = "Quick Doubts is temporarily unavailable.";
    }

    // Hide typing indicator
    if (typingIndicator) {
      typingIndicator.style.display = 'none';
      const dots = typingIndicator.querySelectorAll('.typing-dot');
      if (typeof gsap !== 'undefined') gsap.killTweensOf(dots);
    }

    // Create AI Response Message Bubble
    const aiMsgEl = document.createElement('div');
    aiMsgEl.className = 'chat-msg ai-msg';
    aiMsgEl.innerHTML = `
      <div class="msg-avatar">🤖</div>
      <div class="msg-bubble">
        <div class="ai-text-target"></div>
        <span class="ai-typewriter-cursor"></span>
      </div>
    `;

    if (typingIndicator) {
      messagesContainer.insertBefore(aiMsgEl, typingIndicator);
    } else {
      messagesContainer.appendChild(aiMsgEl);
    }

    // GSAP entrance for the AI message container
    if (typeof gsap !== 'undefined') {
      gsap.fromTo(
        aiMsgEl,
        { opacity: 0, y: 16, scale: 0.94 },
        { opacity: 1, y: 0, scale: 1, duration: 0.3, ease: 'power2.out' }
      );
    }

    const textTarget = aiMsgEl.querySelector('.ai-text-target');
    const cursor = aiMsgEl.querySelector('.ai-typewriter-cursor');

    // Smooth Word-by-Word Streamed Typewriter Animation
    const words = reply.split(' ');
    let currentIdx = 0;
    const streamSpeed = Math.max(25, Math.min(50, Math.floor(1400 / words.length)));

    const streamInterval = setInterval(() => {
      currentIdx += 2;
      if (currentIdx >= words.length) {
        currentIdx = words.length;
        clearInterval(streamInterval);
        if (textTarget) textTarget.innerHTML = formatChatMarkdown(reply);
        if (cursor) cursor.style.display = 'none';
        isAiResponding = false;
      } else {
        if (textTarget) textTarget.innerHTML = formatChatMarkdown(words.slice(0, currentIdx).join(' '));
      }
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, streamSpeed);
  }

  // Clear Chat History
  clearBtn?.addEventListener('click', () => {
    if (isAiResponding) return;
    messagesContainer.innerHTML = `
      <div class="chat-msg ai-msg">
        <div class="msg-avatar">🤖</div>
        <div class="msg-bubble">
          <p>Conversation cleared. Ready for your next career pathway question!</p>
        </div>
      </div>
      <div class="chat-quick-chips" id="aiQuickChips">
        <button type="button" class="chat-quick-chip" data-prompt="Why is Software Architect my #1 match?">
          🎯 Why is Software Architect #1?
        </button>
        <button type="button" class="chat-quick-chip" data-prompt="Explain my loan need and EMI breakdown">
          💰 Explain loan &amp; EMI calculation
        </button>
        <button type="button" class="chat-quick-chip" data-prompt="How do I reconcile parent preferences?">
          🤝 How to resolve parent conflict?
        </button>
        <button type="button" class="chat-quick-chip" data-prompt="What projects should I build for local Mumbai tech?">
          📍 Local Mumbai tech projects
        </button>
      </div>
      <div class="chat-msg ai-msg typing-indicator" id="aiTypingIndicator" style="display: none;">
        <div class="msg-avatar">🤖</div>
        <div class="msg-bubble typing-bubble">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </div>
      </div>
    `;

    // Re-animate chips with GSAP
    if (typeof gsap !== 'undefined') {
      const newChips = messagesContainer.querySelectorAll('.chat-quick-chip');
      gsap.fromTo(
        newChips,
        { opacity: 0, y: 10 },
        { opacity: 1, y: 0, duration: 0.3, stagger: 0.05, ease: 'power2.out' }
      );
    }

    window.showToast('Chat history cleared.', 'info');
  });

  // Helper Markdown to HTML Formatter
  function formatChatMarkdown(text) {
    if (!text) return '';
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n\n/g, '<br/><br/>')
      .replace(/\n•/g, '<br/>&bull;')
      .replace(/\n/g, '<br/>');
  }

  // Helper HTML Escaper
  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }
}






