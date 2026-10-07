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

  // 6. GSAP SplitText on FAQ Heading
  initFaqSplitText();

  // 7. GSAP Inputs Card Entrance Animation
  initInputsCardAnimation();

  // 8. GSAP Typewriter Animation on Hero Description
  initHeroTypewriter();
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

// GSAP SplitText Animation Implementation
function initFaqSplitText() {
  const heading = document.querySelector('#faq .section-title');
  if (!heading) return;

  const rawText = heading.textContent.trim();
  heading.setAttribute('aria-label', rawText);
  heading.innerHTML = '';

  const words = rawText.split(/\s+/);
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

    heading.appendChild(wordSpan);
  });

  if (typeof gsap === 'undefined') return;

  if (typeof ScrollTrigger !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
  }

  const chars = heading.querySelectorAll('.split-char');

  // GSAP 3D reveal with elastic bounce and blur clearance
  gsap.fromTo(
    chars,
    {
      opacity: 0,
      y: 45,
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
      stagger: 0.032,
      scrollTrigger: {
        trigger: heading,
        start: 'top 85%',
        toggleActions: 'restart none none reverse',
      },
    }
  );
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
  { id: 'q1',  category: 'Mathematics & Logic', icon: '📐', text: 'Solving mathematical puzzles and equations' },
  { id: 'q2',  category: 'Software & Automation', icon: '💻', text: 'Writing code or scripts to automate tasks' },
  { id: 'q3',  category: 'Design & Aesthetics', icon: '🎨', text: 'Designing graphics, layouts, or user interfaces' },
  { id: 'q4',  category: 'Scientific Discovery', icon: '🔬', text: 'Conducting scientific experiments in a laboratory' },
  { id: 'q5',  category: 'Writing & Journalism', icon: '✍️', text: 'Reading and writing articles, essays, or stories' },
  { id: 'q6',  category: 'Data & Statistics', icon: '📊', text: 'Analysing data trends and building visual dashboards' },
  { id: 'q7',  category: 'Hardware & Circuits', icon: '⚡', text: 'Building or repairing electronic devices and chips' },
  { id: 'q8',  category: 'Healthcare & Medicine', icon: '🩺', text: 'Researching medical conditions and novel treatments' },
  { id: 'q9',  category: 'Leadership & Management', icon: '👥', text: 'Managing projects, schedules, and multidisciplinary teams' },
  { id: 'q10', category: 'Product & Web Apps', icon: '📱', text: 'Developing full-stack mobile or web applications' },
  { id: 'q11', category: 'Teaching & Mentorship', icon: '📚', text: 'Teaching or explaining complex technical topics to others' },
  { id: 'q12', category: 'Fine Arts & Illustration', icon: '🖌️', text: 'Drawing, digital painting, or visual conceptual art' },
  { id: 'q13', category: 'Mechanical Systems', icon: '⚙️', text: 'Working with mechanical systems, robotics, and machinery' },
  { id: 'q14', category: 'Business & Ventures', icon: '📈', text: 'Understanding how modern businesses operate, scale, and grow' },
  { id: 'q15', category: 'Astronomy & Physics', icon: '🚀', text: 'Exploring outer space, astronomy, or theoretical physics' },
  { id: 'q16', category: 'Human Behavior', icon: '🤝', text: 'Helping people solve personal, career, or social challenges' },
  { id: 'q17', category: 'History & Culture', icon: '🏛️', text: 'Learning about world history, civilisations, and cultural shifts' },
  { id: 'q18', category: 'Artificial Intelligence', icon: '🤖', text: 'Developing AI, neural networks, or machine learning models' },
  { id: 'q19', category: 'Performing Arts', icon: '🎭', text: 'Performing through music, theatre, composition, or cinema' },
  { id: 'q20', category: 'Ecology & Biology', icon: '🌿', text: 'Studying natural ecosystems, plant genetics, or biodiversity' },
  { id: 'q21', category: 'Law & Ethics', icon: '⚖️', text: 'Investigating legal disputes, public policy, and ethics' },
  { id: 'q22', category: 'Architecture & Spaces', icon: '🏗️', text: 'Creating architectural structures, interiors, or urban plans' },
  { id: 'q23', category: 'Financial Markets', icon: '💰', text: 'Working with financial portfolios, investment budgets, or trading' },
  { id: 'q24', category: 'Applied Innovation', icon: '💡', text: 'Pioneering breakthrough research to solve an unsolved world problem' }
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
        <span class="card-category-tag">${q.icon} ${q.category}</span>
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

  // Calibrate smooth vertical scroll travel: ~165px per card
  const totalCards = track.querySelectorAll('.interest-card').length || 24;
  const totalScrollDistance = totalCards * 165;

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
      scrub: 0.3, // Crisp & responsive, zero lag
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
