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
  const signupNavBtn = document.getElementById('signupNavBtn');
  const closeSignupDialog = document.getElementById('closeSignupDialog');
  const closeStartDialog = document.getElementById('closeStartDialog');

  // Open Signup
  signupNavBtn?.addEventListener('click', () => {
    signupDialog?.showModal();
  });

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
    // Collect all profile data from Steps 1, 2, 3, and 4
    const stream = localStorage.getItem('goguide_stream') || document.getElementById('academicStream')?.value || '';
    const marks = localStorage.getItem('goguide_marks') || document.getElementById('marksPercentage')?.value || '';
    const city = localStorage.getItem('goguide_city') || document.getElementById('currentCity')?.value || '';

    // Interests
    const interests = {};
    INTEREST_QUESTIONS.forEach(q => {
      const val = localStorage.getItem(`goguide_interest_${q.id}`);
      if (val) interests[q.id] = parseInt(val, 10);
    });

    // Skills
    const skills = {};
    SKILLS.forEach(s => {
      const val = localStorage.getItem(`goguide_skill_${s.id}`) || '50';
      skills[s.id] = parseInt(val, 10);
    });

    // Risk tolerance
    const riskChecked = document.querySelector('input[name="risk_tolerance"]:checked');
    const risk = riskChecked ? parseInt(riskChecked.value, 10) : 3;

    // Target career
    const targetCareer = document.getElementById('targetCareer')?.value.trim() || null;

    const payload = {
      academic_stream: stream,
      marks_percentage: parseFloat(marks) || null,
      current_city: city,
      interests,
      skills,
      risk_tolerance: risk,
      target_career: targetCareer
    };

    console.log('[GoGuide] Final Profile Payload:', payload);

    try {
      localStorage.setItem('goguide_student_profile', JSON.stringify(payload));
    } catch (err) { }

    // Animate button
    const textEl = btn.querySelector('.text');
    if (textEl) textEl.textContent = 'GENERATING ROADMAP…';
    btn.disabled = true;

    const apiUrl = window.API_URL || '';
    fetch(`${apiUrl}/api/students`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then(async res => {
        const data = await res.json().catch(() => ({}));
        console.log('[GoGuide] Backend response:', data);
        window.showToast('Profile saved to GoGuide! Generating your personalized roadmap…', 'success');
        if (textEl) textEl.textContent = '✓ SUBMITTED!';
        setTimeout(() => {
          if (typeof window.smoothScrollTo === 'function') {
            window.smoothScrollTo('#resultsSection', 1.0);
          }
        }, 700);
      })
      .catch(err => {
        console.warn('[GoGuide] Backend note:', err.message);
        window.showToast('Profile saved locally! Displaying your PRISM matches.', 'success');
        if (textEl) textEl.textContent = '✓ SAVED LOCALLY!';
        setTimeout(() => {
          if (typeof window.smoothScrollTo === 'function') {
            window.smoothScrollTo('#resultsSection', 1.0);
          }
        }, 700);
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

  const checkVisibility = () => {
    const scrollY = window.pageYOffset || document.documentElement.scrollTop || window.scrollY || 0;
    const currentHash = window.location.hash;

    // Check whether the user is on the first landing page (hero at the very top)
    let isLandingPage = false;
    if (heroSection) {
      const heroRect = heroSection.getBoundingClientRect();
      // On landing page if scrollY is near top (< 80px) AND hero bottom covers the top screen
      if (scrollY < 80 && heroRect.top >= -50 && (!currentHash || currentHash === '#home')) {
        isLandingPage = true;
      }
    } else if (scrollY < 80 && (!currentHash || currentHash === '#home')) {
      isLandingPage = true;
    }

    // Navigation bar MUST be visible on all pages/sections except the first landing page
    if (!isLandingPage) {
      container.classList.add('visible');
    } else {
      container.classList.remove('visible');
    }
  };

  window.addEventListener('scroll', checkVisibility, { passive: true });
  window.addEventListener('resize', checkVisibility, { passive: true });
  window.addEventListener('hashchange', checkVisibility, { passive: true });
  document.addEventListener('scroll', checkVisibility, { passive: true });

  // Hook into GSAP ScrollTrigger updates & pin lifecycle so it remains persistent throughout all steps
  if (typeof ScrollTrigger !== 'undefined') {
    ScrollTrigger.addEventListener('scrollEnd', checkVisibility);
    ScrollTrigger.addEventListener('refresh', checkVisibility);
  }

  // Check immediately and continuously upon layout changes
  checkVisibility();
  setTimeout(checkVisibility, 100);
  setTimeout(checkVisibility, 400);
  setTimeout(checkVisibility, 1000);

  // Home Button: Maps to Landing Page (hero at top of page)
  const homeBtn = document.getElementById('bottomNavHomeBtn');
  homeBtn?.addEventListener('click', (e) => {
    e.preventDefault();
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

  // Settings Button: Toggles Settings & User Profile Dropdown
  const settingsBtn = document.getElementById('bottomNavSettingsBtn');
  settingsBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (typeof window.toggleSettingsDropdown === 'function') {
      window.toggleSettingsDropdown();
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

// 5 Feasible Canonical Careers evaluated through PRISM
const CANONICAL_FEASIBLE_CAREERS = [
  {
    id: 'software-architect',
    name: 'Software Architect & Systems Engineer',
    cluster: 'Information Technology',
    flags: ['High Market Demand', 'Entrance Exam Required'],
    fit: 0.94,
    market: 0.91,
    fin: 0.92,
    risk: 0.86,
    conflict: 0.03,
    total_cost: '₹14,50,000',
    savings: '₹4,00,000',
    scholarship: '₹1,50,000',
    funding_req: '₹9,00,000',
    loan_need: '₹9,00,000',
    monthly_emi: '₹11,640 / mo',
    emi_ratio: '15.5% (Safe < 40%)',
    skill_gaps: {
      large: ['Distributed Systems', 'Cloud Native Architecture (Kubernetes)'],
      some: ['Relational Database Indexing', 'Data Structures & Algorithms'],
      on_track: ['Python Scripting', 'Mathematical Logic', 'System Debugging'],
    },
    roadmap: [
      {
        time: '0–3 mo',
        title: 'Foundation & Entrance Prep',
        desc: 'Prepare for JEE Main / State CET. Master core data structures & algorithms in Python or C++.',
      },
      {
        time: '3–6 mo',
        title: 'Application & Practical Artifact',
        desc: 'Build an end-to-end fullstack telemetry microservice application. Publish GitHub repository.',
      },
      {
        time: '6–12 mo',
        title: 'Admission & Core Specialization',
        desc: 'Secure Tier-1/2 CS enrollment; apply for central state merit scholarships before August deadlines.',
      },
    ],
    exams: 'JEE Main, MHT-CET, BITSAT',
    scholarships: 'Reliance Foundation Undergraduate Scholarship (Dec 15) • National Scholarship Portal (Oct 31)',
    adjacent: ['Cloud & DevOps Specialist', 'Data Science & AI Engineer', 'Cybersecurity Architect'],
    sources: 'ESCO Canonical Occupation Graph (2024) • O*NET v28.1 • India Job Market Feed (Q3 2024)',
  },
  {
    id: 'data-scientist-ai',
    name: 'Data Science & AI Engineer',
    cluster: 'Artificial Intelligence & Analytics',
    flags: ['High Market Demand', 'Rapid Salary Escalation'],
    fit: 0.90,
    market: 0.95,
    fin: 0.88,
    risk: 0.80,
    conflict: 0.04,
    total_cost: '₹15,20,000',
    savings: '₹4,00,000',
    scholarship: '₹1,20,000',
    funding_req: '₹10,00,000',
    loan_need: '₹10,00,000',
    monthly_emi: '₹12,930 / mo',
    emi_ratio: '17.2% (Safe < 40%)',
    skill_gaps: {
      large: ['Deep Learning Frameworks (PyTorch)', 'LLM Fine-Tuning & Quantization'],
      some: ['Multivariate Statistics', 'Feature Engineering'],
      on_track: ['Python Scripting', 'SQL Queries', 'Analytical Reasoning'],
    },
    roadmap: [
      {
        time: '0–3 mo',
        title: 'Math & Statistical Baseline',
        desc: 'Deepen multivariate calculus, matrix operations, probability distributions, and data analysis pipelines.',
      },
      {
        time: '3–6 mo',
        title: 'Predictive Modeling Project',
        desc: 'Deploy an open predictive machine learning inference API using FastAPI and municipal open datasets.',
      },
      {
        time: '6–12 mo',
        title: 'Degree Track & Research Lab',
        desc: 'Pursue specialized B.Tech/B.S. in Data Engineering/AI; join university machine learning research groups.',
      },
    ],
    exams: 'JEE Main, VITEEE, MET',
    scholarships: 'Tata Trust Technical Scholarship (Nov 15) • NSP Central Sector (Oct 31)',
    adjacent: ['Machine Learning Researcher', 'Business Intelligence Architect', 'Quantitative Analyst'],
    sources: 'O*NET v28.1 • India Tech Labor Market Index (2024)',
  },
  {
    id: 'cloud-devops',
    name: 'Cloud & DevOps Infrastructure Specialist',
    cluster: 'Cloud Computing & Systems',
    flags: ['Low Early Volatility', 'High Entry Placement'],
    fit: 0.85,
    market: 0.92,
    fin: 0.94,
    risk: 0.88,
    conflict: 0.02,
    total_cost: '₹12,80,000',
    savings: '₹4,00,000',
    scholarship: '₹1,00,000',
    funding_req: '₹7,80,000',
    loan_need: '₹7,80,000',
    monthly_emi: '₹10,080 / mo',
    emi_ratio: '14.8% (Safe < 40%)',
    skill_gaps: {
      large: ['Kubernetes Cluster Admin', 'Terraform Infrastructure-as-Code'],
      some: ['Linux Kernel Tuning', 'CI/CD Automated Pipelines'],
      on_track: ['Bash Scripting', 'Networking Protocols', 'Git Workflow'],
    },
    roadmap: [
      {
        time: '0–3 mo',
        title: 'Linux & Networking Fundamentals',
        desc: 'Master Linux administration, TCP/IP networking, containerization fundamentals with Docker.',
      },
      {
        time: '3–6 mo',
        title: 'CI/CD Automated Deployments',
        desc: 'Set up multi-cloud deployment pipelines on AWS/GCP with automated test runners and monitoring.',
      },
      {
        time: '6–12 mo',
        title: 'Cloud Certification & Degree',
        desc: 'Earn AWS Solutions Architect Associate; complete B.Tech Information Technology curriculum.',
      },
    ],
    exams: 'JEE Main, State CET, COMEDK',
    scholarships: 'AICTE Pragati / Saksham Scheme (Nov 30) • Foundation for Excellence (Oct 15)',
    adjacent: ['Site Reliability Engineer', 'Cyber Defense Analyst', 'Solutions Architect'],
    sources: 'ESCO Cloud Domain Map • NASSCOM IT Workforce Survey 2024',
  },
  {
    id: 'vlsi-embedded',
    name: 'VLSI & Embedded Systems Design Engineer',
    cluster: 'Electronics & Semiconductor Hardware',
    flags: ['National Semiconductor Mission', 'Hardware Moat'],
    fit: 0.82,
    market: 0.88,
    fin: 0.85,
    risk: 0.90,
    conflict: 0.05,
    total_cost: '₹14,00,000',
    savings: '₹4,00,000',
    scholarship: '₹1,50,000',
    funding_req: '₹8,50,000',
    loan_need: '₹8,50,000',
    monthly_emi: '₹10,990 / mo',
    emi_ratio: '16.9% (Safe < 40%)',
    skill_gaps: {
      large: ['Verilog / SystemVerilog Synthesis', 'FPGA Hardware Emulation'],
      some: ['Digital Circuit Timing Analysis', 'Microcontroller Interfacing'],
      on_track: ['Physics Electromagnetism', 'Boolean Logic', 'C Programming'],
    },
    roadmap: [
      {
        time: '0–3 mo',
        title: 'Digital Logic & Circuit Physics',
        desc: 'Complete circuit synthesis foundations, CMOS transistor logic, and logic gate minimization.',
      },
      {
        time: '3–6 mo',
        title: 'Verilog Simulation Artifact',
        desc: 'Simulate a 5-stage pipelined RISC-V processor in Icarus Verilog; test logic waveform traces.',
      },
      {
        time: '6–12 mo',
        title: 'Hardware Lab & Apprenticeship',
        desc: 'B.Tech Electronics & Communication; target India Semiconductor Mission subsidized lab programs.',
      },
    ],
    exams: 'JEE Main, JEE Advanced, BITSAT',
    scholarships: 'India Semiconductor Mission Fellowship (Dec 01) • NSP Central Sector (Oct 31)',
    adjacent: ['Firmware Engineer', 'Robotics Systems Specialist', 'IoT Hardware Architect'],
    sources: 'India Semiconductor Mission (ISM) Roadmap • ESCO Electronics Matrix',
  },
  {
    id: 'product-systems',
    name: 'Product Systems & Operations Specialist',
    cluster: 'Product Management & Systems',
    flags: ['Interdisciplinary', 'High Executive Mobility'],
    fit: 0.80,
    market: 0.84,
    fin: 0.90,
    risk: 0.82,
    conflict: 0.06,
    total_cost: '₹13,50,000',
    savings: '₹4,00,000',
    scholarship: '₹1,20,000',
    funding_req: '₹8,30,000',
    loan_need: '₹8,30,000',
    monthly_emi: '₹10,730 / mo',
    emi_ratio: '16.5% (Safe < 40%)',
    skill_gaps: {
      large: ['Product Lifecycle Analytics', 'Quantitative A/B Testing Design'],
      some: ['User Journey Mapping', 'Product Roadmapping'],
      on_track: ['Analytical Writing', 'Structured Problem Solving', 'Logic'],
    },
    roadmap: [
      {
        time: '0–3 mo',
        title: 'Data Analytics & Wireframing',
        desc: 'Master SQL, product metrics (LTV, CAC, churn), and Figma user flow diagrams.',
      },
      {
        time: '3–6 mo',
        title: 'Civic Product Case Study',
        desc: 'Conduct usability and efficiency audit for urban transit ticketing; publish teardown paper.',
      },
      {
        time: '6–12 mo',
        title: 'STEM + Product Degree Path',
        desc: 'Pursue Industrial Engineering / Computer Science with product management club leadership.',
      },
    ],
    exams: 'JEE Main, State CET, IPMAT',
    scholarships: 'State Merit Scholarship (Nov 15) • Aditya Birla Scholarship (Oct 20)',
    adjacent: ['Technical Program Manager', 'Business Operations Lead', 'UX Systems Analyst'],
    sources: 'O*NET v28.1 • Product Management Association Survey 2024',
  },
];

// Blocked Careers strictly kept separate from ranked results (Financial Feasibility Gate Failed)
const CANONICAL_BLOCKED_CAREERS = [
  {
    id: 'private-mbbs',
    name: 'Private MBBS / Medical Surgeon',
    reason: 'Financial Feasibility Gate Failed: Total cost ₹85.0 L exceeds affordable plan cap; EMI / Salary ratio 68.4% exceeds 40% safety threshold.',
    gap: '₹63.75 lakh more than your plan covers.',
    explanation: 'Private medical tuition in India averages ₹85 lakh across 5.5 years plus residency. With family liquid savings of ₹5 lakh and family loan tolerance of ₹16.25 lakh, there is an unbridgeable ₹63.75 lakh capital shortfall.',
  },
  {
    id: 'commercial-pilot',
    name: 'Commercial Aviation Pilot (CPL)',
    reason: 'Financial Feasibility Gate Failed: Training cost ₹55.0 L with upfront capital blocks; monthly loan EMI ₹52,400 exceeds 40% entry co-pilot stipend.',
    gap: '₹38.50 lakh more than your plan covers.',
    explanation: 'Commercial Pilot License flight school requires ₹55 lakh in lump-sum tranches. Bank educational loan collateral guidelines and starting First Officer stipends trigger severe loan-stress flags.',
  },
];

// Per-career alignment data for Conflict View
const CONFLICT_COMPARISON_DATA = [
  {
    career: 'Software Architect & Systems Engineer',
    youFit: '0.94',
    parentAffinity: '0.70',
    diff: '0.24',
    riskDisagreement: 'Low',
    note: 'High market demand and rapid starting salary bridge family risk concerns.',
  },
  {
    career: 'Data Science & AI Engineer',
    youFit: '0.90',
    parentAffinity: '0.75',
    diff: '0.15',
    riskDisagreement: 'Low',
    note: 'Clear quantitative rigor reassures parents seeking established STEM paths.',
  },
  {
    career: 'Biomedical Engineering (Compromise)',
    youFit: '0.78',
    parentAffinity: '0.88',
    diff: '0.10',
    riskDisagreement: 'Very Low',
    note: 'Synthesizes healthcare career stability with student affinity for tech innovation.',
  },
  {
    career: 'Civil & Urban Infrastructure',
    youFit: '0.65',
    parentAffinity: '0.85',
    diff: '0.20',
    riskDisagreement: 'Medium',
    note: 'Parent priority for government/PSU stability exceeds student interest in digital domains.',
  },
  {
    career: 'Pure Research (Theoretical Physics)',
    youFit: '0.85',
    parentAffinity: '0.35',
    diff: '0.50',
    riskDisagreement: 'High',
    note: 'Extended doctoral timeline without guaranteed industry return causes family hesitation.',
  },
];

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
    const stream = localStorage.getItem('goguide_stream') || 'Science – PCM';
    const marks = localStorage.getItem('goguide_marks') || '88.5';
    const contextStudent = document.getElementById('aiContextStudent');
    const contextScore = document.getElementById('aiContextScore');
    const contextMatch = document.getElementById('aiContextMatch');

    if (contextStudent) contextStudent.textContent = stream;
    if (contextScore) contextScore.textContent = `${marks}% Score`;
    if (contextMatch) contextMatch.textContent = '#1 Match: Software Arch.';
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

    // Simulate realistic grounded response calculation delay
    setTimeout(() => {
      generateAiResponse(text);
    }, 750);
  }

  // Generate Intelligent Grounded Response based on query
  function generateAiResponse(userQuery) {
    const q = userQuery.toLowerCase();
    let reply = '';

    if (q.includes('software') || q.includes('architect') || q.includes('#1') || q.includes('top match')) {
      reply = `**Software Architect & Systems Engineer** is your **#1 match** with a composite **PRISM Match Index of 88.6/100**.\n\n• **Fit Score: 0.94** — Exceptional aptitude synergy with your Science PCM baseline (88.5%).\n• **Market Demand: 0.91** — Top tier placement volume and salary escalation across Indian tech hubs.\n• **Financial Feasibility: 0.92** — 4-year tuition of ₹14.5L requires a ₹9L loan with a safe ₹11,640/mo EMI (only 15.5% of your entry salary!).`;
    } else if (q.includes('loan') || q.includes('emi') || q.includes('cost') || q.includes('budget') || q.includes('financ')) {
      reply = `Here is your **Deterministic Financial Solver breakdown**:\n\n• **Total 4-Year Cost**: ₹14,50,000\n• **Family Savings Allocated**: ₹4,00,000\n• **Scholarship Assumed**: ₹1,50,000\n• **Net Loan Principal Needed**: **₹9,00,000**\n• **Monthly Loan EMI**: **₹11,640 / mo** (10-yr tenure @ 9.5% SBI Ed-Loan)\n• **Affordability Ratio**: **15.5%** of entry salary (comfortably under the 40% risk ceiling!).`;
    } else if (q.includes('conflict') || q.includes('parent') || q.includes('family') || q.includes('reconcil')) {
      reply = `Your **Conflict Index (CI) is 0.34 (Low-Moderate disagreement)**:\n\n• **Your Vector**: Passion for high-level software engineering and technical architecture.\n• **Parent Vector**: Preference for institutional stability, government PSU tracks, and predictable ROI.\n• **Reconciled Compromise**: **Biomedical Engineering** (Fits you at 0.78, family at 0.88), or **Cloud Infrastructure** which bridges parents' stability goals with modern tech compensation!`;
    } else if (q.includes('mumbai') || q.includes('local') || q.includes('project') || q.includes('city')) {
      reply = `Grounding your path in the **Mumbai Metropolitan Region**:\n\n• **Municipal Problem**: Seasonal monsoon transport bottlenecks and ward drainage delays.\n• **Recommended Project**: Build an open-source precipitation routing telemetry dashboard for Ward D using municipal sensor feeds and open map APIs.\n• **Matching Skills**: Python analytics, embedded telemetry, and spatial routing. Excellent for college admissions and GitHub portfolios!`;
    } else if (q.includes('skill') || q.includes('gap') || q.includes('learn')) {
      reply = `Based on our canonical **ESCO & O*NET 28.1 Skill Gap Model**:\n\n• **Large Gaps**: Distributed Systems & Cloud-Native Kubernetes Orchestration.\n• **Some Gaps**: Relational DB Indexing & Data Structures.\n• **On Track**: Python Scripting, Algorithmic Math, and System Debugging.\n• **Roadmap (0–3 Months)**: Master C++/Python data structure basics and practice coding algorithmic fundamentals!`;
    } else if (q.includes('mbbs') || q.includes('medical') || q.includes('pilot') || q.includes('blocked')) {
      reply = `**Private MBBS** was strictly blocked by our **Financial Feasibility Gate**:\n\n• **Reason**: 5.5-year private tuition averages ₹85 Lakh, leaving a **₹63.75 Lakh unbridgeable shortfall** beyond your plan.\n• **EMI Stress**: The projected EMI ratio of 68.4% far exceeds our 40% debt safety cap.\n• **PRISM Rule**: Blocked careers are never mixed into ranked results to protect families from dangerous over-leveraging!`;
    } else if (q.includes('exam') || q.includes('scholarship') || q.includes('test')) {
      reply = `Key **Entrance Exams & Scholarships** for your pathway:\n\n• **Exams**: JEE Main, MHT-CET, and BITSAT.\n• **Top Scholarships**: Reliance Foundation Undergraduate Scholarship (Dec 15 deadline) & National Scholarship Portal Central Sector Scheme (Oct 31 deadline).\n• Both schemes can provide ₹1.2L–₹2.0L in tuition fee relief!`;
    } else {
      reply = `I have analyzed your **Science – PCM (88.5% score)** profile and current simulation weights (40% Fit, 30% Market, 15% Financial, 15% Risk).\n\nYour optimal pathway balances **Software Architecture** with **Cloud Infrastructure**. You can adjust sliders in the Left Rail to see ranks reorder, or ask me for advice on exams, skill gaps, or financial planning!`;
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






