# GoGuide Application Flow (APP_FLOW)

## 1. Primary User Journey

The primary user journey is a linear progression through the GoGuide application, moving from data collection to deterministic analysis, and finally to conversational synthesis.

1. **Landing**
   - User arrives at GoGuide landing page.
   - Values proposition: AI-assisted career and education decision-support.

2. **Role Selection**
   - User identifies as: Student, Parent/Guardian, or Both (Joint Session).
   - Establishes the profile context for subsequent inputs.

3. **Student Assessment** (*User-Entered Data*)
   - Capture: Interests, preferences, aptitude, academic history, education preference, location preference, self-reported skills.

4. **Parent Input** (*User-Entered Data*)
   - Capture: Preferred career directions, education preferences, affordability expectations, location preferences, priorities/concerns.

5. **Financial Profile** (*User-Entered Data*)
   - Capture: Annual budget, total savings, loan willingness, scholarship awareness.

6. **Preference/Conflict Analysis** (*Deterministic Backend Calculation*)
   - Evaluates the delta between Student Assessment and Parent Input using the Conflict Engine.
   - Identifies areas of alignment and areas requiring discussion.

7. **Career Recommendations** (*Deterministic Backend Calculation*)
   - Executes the Phase 7.2 Top-K Recommendation Engine based on validated data.
   - Presents a ranked list of careers based on student fit, market opportunity, and progression evidence.

8. **Career Detail** (*Deterministic Backend + Live Web Information*)
   - Deep dive into a selected career.
   - *Backend*: Presents historical salary data, cluster mapping, required skills.
   - *Live Web*: Retrieves current job openings, real-time market signals.

9. **Skill-Gap Analysis** (*Deterministic Backend Calculation*)
   - Compares self-reported skills against canonical occupation-required skills.

10. **Education/Pathway Exploration** (*Deterministic Backend + Live Web Information*)
   - *Backend*: Maps canonical education pathways (degrees, exams) to the career.
   - *Live Web*: Retrieves current college fees, course availability, admission dates.

11. **Financial Feasibility** (*Deterministic Backend Calculation*)
   - Calculates Total Cost, Funding Need, EMI, and loan-cap feasibility.

12. **What-If Simulation** (*Deterministic Backend Calculation*)
   - User adjusts parameters (e.g., budget, location, loan assumptions).
   - Recalculates financial feasibility and recommendation rankings dynamically.

13. **Alternative Paths** (*Deterministic Backend Calculation*)
   - Suggests adjacent careers based on the Career Progression graph (Phase 6 data).

14. **Final Action Plan** (*Deterministic Backend + LLM Generation*)
   - Synthesizes findings into concrete steps (skills to build, exams to take, finances to prepare).
   - *LLM*: Generates natural language wording grounded in backend facts.

15. **Conversational GoGuide Assistant** (*LLM-Generated Explanation*)
   - Ongoing chat interface for contextual questions.
   - Explains recommendations, mediates parent/student discussions, and answers questions using structured backend context.

---

## 2. Support Journeys

- **Student-only journey**: Skips parent input and conflict analysis. Focuses heavily on aptitude, skill gaps, and pathways.
- **Parent-only input**: A parent can fill out a profile for their child to generate baseline financial and career scenarios.
- **Combined student + parent journey**: Full primary journey.
- **Returning user journey**: Bypasses initial assessments. Resumes at the dashboard (Action Plan, What-If Simulator, or Assistant).
- **Incomplete-profile handling**: The system uses nullable fields (e.g., `NOT_AVAILABLE`) and provides baseline recommendations using only available data.

---

## 3. Data Source Distinction

The application flow strictly separates data sources to maintain trust and accuracy:

- **User-Entered Data**: Profile inputs, financial constraints, self-reported skills.
- **Deterministic Backend Calculations**: Recommendation scores, preference alignment vectors, EMI math, canonical skill mappings. Always the *Source of Truth*.
- **Live Web Information**: Real-time variables that expire (fees, dates, live job counts). If unavailable, explicitly marked as `NOT_AVAILABLE`. Never fabricated.
- **LLM-Generated Explanations**: Natural language synthesis. The LLM translates backend numbers into human-readable advice, generates action plan text, and powers the chat assistant. It *never* calculates EMI or invents job statistics.
