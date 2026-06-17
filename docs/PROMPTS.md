# Prompt Engineering Log

**Source:** software_submission_guidelines-V3 §8.3

> "Documentation of the AI-assisted development process, containing a list of all prompts
> used during development, description of each prompt's purpose, examples of outputs and
> iterations, and methods that proved useful from the development session."

---

## Format

Each entry follows this structure:

```
### PROMPT-NNN: [Short Title]
- **Date:** YYYY-MM-DD
- **Phase:** Planning | Implementation | Testing | Debugging | Refactoring
- **Tool:** Claude Code | ChatGPT | Copilot | etc.
- **Prompt:** [exact prompt text]
- **Output Summary:** [what was produced]
- **Iterations:** [how many attempts, what changed]
- **Useful:** YES / PARTIAL / NO
- **Notes:** [what worked, what didn't, lessons learned]
```

---

## Session 1: Planning Phase

### PROMPT-001: HW05 Planning & Skeleton Generation
- **Date:** 2026-06-17
- **Phase:** Planning
- **Tool:** Claude Code (claude-sonnet-4-6)
- **Prompt:** Full project preparation prompt — read 3 source files, analyze requirements,
  create all planning documents, PRDs, skeleton files. (see conversation history)
- **Output Summary:** Created docs/ directory with ASSIGNMENT_ANALYSIS.md,
  GUIDELINES_REQUIREMENTS.md, GRADING_RUBRIC.md, FEEDBACK_RISK_CHECKLIST.md, PLAN.md,
  ARCHITECTURE.md, PRD_INDEX.md, PROMPTS.md; docs/prds/ with 9 PRD files; README.md,
  .gitignore, .env.example, TODO.md
- **Iterations:** 1
- **Useful:** YES
- **Notes:** Reading all 3 source PDFs before generating ensured all requirements were
  traceable. The feedback report (HW01) was critical for identifying RISK-01 (costs) and
  RISK-02 (UI/UX) — the two biggest deduction areas.

---

## Session 2: Implementation Phase

*To be filled in as implementation progresses.*

### PROMPT-NNN: [Template]
- **Date:** YYYY-MM-DD
- **Phase:** Implementation
- **Tool:** Claude Code
- **Prompt:** [paste exact prompt]
- **Output Summary:** [what files were created/modified]
- **Iterations:** N
- **Useful:** YES / PARTIAL / NO
- **Notes:** [lessons]

---

## Lessons Learned

*To be updated throughout the project.*

1. Always read source documents completely before generating any code
2. Use the feedback report to identify grading risks before starting
3. Plan architecture before implementation — SDK layer must be designed first
4. Test with small models first before attempting large model downloads
