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

    window.showToast('Academic details saved! Revealing Interest Assessment...');

    // Smoothly scroll down to Interest Assessment section with zero overlap
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
  const card = document.querySelector('.inputs-card');
  if (!card || typeof gsap === 'undefined') return;

  if (typeof ScrollTrigger !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
  }

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
        trigger: '#studentInputs',
        start: 'top 80%',
        toggleActions: 'play none none none',
      },
    }
  );
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
  const name = nameInput ? nameInput.value : 'Explorer';
  const signupDialog = document.getElementById('signupDialog');

  if (signupDialog) signupDialog.close();
  window.showToast(`Welcome aboard, ${name}! Your roadmap is ready.`);

  const form = document.getElementById('signupForm');
  if (form) form.reset();
};

// Track selection from Start Now dialog
window.selectTrack = function (trackName) {
  const startDialog = document.getElementById('startDialog');
  if (startDialog) startDialog.close();
  window.showToast(`Selected "${trackName}" track! Loading guide...`);
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
      })
      .catch(err => {
        console.warn('[GoGuide] Backend note:', err.message);
        window.showToast('Profile saved locally! Ready for GoGuide pipeline.', 'success');
        if (textEl) textEl.textContent = '✓ SAVED LOCALLY!';
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
    // Update hash without jumping
    if (history.pushState) {
      history.pushState(null, null, '#home');
    } else {
      location.hash = '#home';
    }
  });

  // AI Bot Button: Opens GoGuide AI Advisor Dialog
  const aiBotBtn = document.getElementById('bottomNavAiBotBtn');
  const aiBotDialog = document.getElementById('aiBotDialog');
  aiBotBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    if (aiBotDialog && typeof aiBotDialog.showModal === 'function') {
      aiBotDialog.showModal();
    } else {
      window.showToast('GoGuide AI Advisor is ready to assist your career journey!', 'info');
    }
  });

  document.getElementById('closeAiBotDialog')?.addEventListener('click', () => {
    aiBotDialog?.close();
  });

  // Settings Button: Opens Platform Settings Dialog
  const settingsBtn = document.getElementById('bottomNavSettingsBtn');
  const settingsDialog = document.getElementById('settingsDialog');
  settingsBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    if (settingsDialog && typeof settingsDialog.showModal === 'function') {
      settingsDialog.showModal();
    } else {
      window.showToast('GoGuide Settings opened', 'info');
    }
  });

  document.getElementById('closeSettingsDialog')?.addEventListener('click', () => {
    settingsDialog?.close();
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



