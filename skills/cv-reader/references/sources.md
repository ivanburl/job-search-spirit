# Design sources

Reviewed on 2026-10-26. Star counts below are rounded repository-wide counts displayed by GitHub at review time, not counts for individual skills or an accuracy benchmark.

## Anthropic PDF skill — approximately 184,000 repository stars

- Repository: https://github.com/anthropics/skills
- Skill: https://github.com/anthropics/skills/blob/main/skills/pdf/SKILL.md
- Contribution: inspiration for local PDF text extraction and a separate path for scanned PDFs requiring OCR. This is a general PDF skill, not a CV-specific parser.
- The PDF skill declares a proprietary license. Its prose and scripts are not copied or bundled here; this implementation is independently written.

## OpenResume — approximately 8,900 repository stars

- Repository: https://github.com/xitanggg/open-resume
- Parser pipeline: https://github.com/xitanggg/open-resume/blob/main/src/app/lib/parse-resume-from-pdf/index.ts
- PDF reader: https://github.com/xitanggg/open-resume/blob/main/src/app/lib/parse-resume-from-pdf/read-pdf.ts
- Contribution: inspiration for separating PDF reading from section grouping and semantic field extraction, and retaining positional evidence. OpenResume's pipeline documents a single-column English limitation; this skill uses page inspection and explicit uncertainty handling for other layouts instead of promising equivalent automatic parsing.
- OpenResume uses AGPL-3.0. No source code is copied, imported, or bundled here.

## Project-specific design

The requested fields, exact work-bullet preservation, hidden contact-link recovery, missing-versus-unreadable distinction, and evidence output contract are designed for Job Search Spirit. The helper only collects PDF evidence; the agent follows SKILL.md to interpret that evidence into the CV record. Neither referenced project is installed as a dependency.
