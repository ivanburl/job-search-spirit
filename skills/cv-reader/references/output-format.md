# CV extraction output contract

Return valid UTF-8 JSON, without comments. All keys in the envelope below are required. `name` means given name(s); `surname` means family name(s). Keep `full_name` even if the split is uncertain. Contact fields are arrays so multiple values are retained; the repeated GitHub field in the original request is represented once.

```json
{
  "schema_version": "1.0",
  "source": {"filename": "cv.pdf", "page_count": 0},
  "extraction": {"status": "blocked", "methods": [], "pages_read": [], "unreadable_pages": []},
  "full_name": null,
  "name": null,
  "surname": null,
  "github": [],
  "linkedin": [],
  "phone_number": [],
  "email": [],
  "other_links": [],
  "skills": [],
  "education": [],
  "languages": [],
  "certifications": [],
  "work_experience": [],
  "evidence": [],
  "missing_fields": [],
  "review_issues": [],
  "unresolved_items": []
}
```

The envelope illustrates types, not an extraction result. Replace source metadata and extraction status with observed values. `page_count` is a positive integer when known, otherwise null. Page numbers are one-based. `methods` uses any applicable values from `pdf_text`, `pdf_links`, `visual`, and `ocr`.

`status` is `complete` only when all pages and requested sections have been inspected and no extraction ambiguity remains. It can be complete even if the CV omits fields. Use `partial` when some facts are reliable but content is unreadable or ambiguous, and `blocked` when no reliable extraction is possible. In `pages_read`, include fully inspected pages; list unreadable or only partly readable pages in `unreadable_pages`.

## Values and records

Unknown scalar values are null, never invented values or strings such as `N/A`. Collections are arrays, empty when nothing can be extracted. Use `missing_fields` to distinguish confirmed absence from unknown due to extraction problems. Every object in the following collections includes all shown keys; scalar fields are strings or null unless otherwise stated.

| Collection | Item shape |
| --- | --- |
| `github`, `linkedin`, `phone_number`, `email` | String, preserving a distinct candidate contact value |
| `other_links` | `{"label": null, "url": null, "kind": null}`; kind is `repository`, `portfolio`, or `other` |
| `skills` | `{"name": null, "aliases": [], "basis": []}`; aliases are strings; basis contains `skills_section`, `work_experience`, `projects`, or `other_explicit_mention` |
| `education` | `{"institution": null, "qualification": null, "field_of_study": null, "location": null, "start_date": null, "end_date": null, "status": null, "details": []}`; details are original text strings |
| `languages` | `{"language": null, "proficiency": null, "qualification": null}` |
| `certifications` | `{"name": null, "issuer": null, "issue_date": null, "expiry_date": null, "credential_id": null, "credential_url": null, "status": null}` |
| `work_experience` | `{"company": null, "title": null, "location": null, "employment_type": null, "start_date": null, "end_date": null, "description": [], "bullets": []}`; description contains original paragraphs as strings |

Each work bullet has the recursive shape `{"text": "Original bullet text", "children": []}`. Preserve original wording after removing the bullet marker and joining purely visual line wraps. Nested bullets use the same shape inside `children`. Do not convert prose into invented bullets. Keep records and bullets in document order.

## Evidence and uncertainty

For every populated scalar leaf (including array strings and bullet text), add an evidence entry. A single entry can support multiple values through `fields`. Operational metadata, issue messages, and structural values such as `basis` do not need quotations; their underlying facts do.

```json
{
  "fields": ["/work_experience/0/bullets/0/text"],
  "pages": [2],
  "text": "Reduced build time by 30%.",
  "method": "pdf_text"
}
```

`fields` contains JSON Pointers using zero-based array indices. `pages` contains the source page numbers. `text` is the relevant source excerpt or actual hyperlink destination. `method` is one of the extraction methods above. Do not use PDF metadata author fields as proof of the candidate's name. For normalized URLs or aliases, evidence retains the original value.

- `missing_fields`: JSON Pointers to confirmed absent requested fields, e.g. `/certifications` or `/education/0/end_date`. Do not list internal optional metadata or absent fields that could be on unreadable pages.
- `review_issues`: objects with `fields` (array of JSON Pointers), `pages` (array of page numbers), and `message` (specific ambiguity, conflict, or extraction failure). Use empty arrays when the scope is unknown. Include candidates in the message when helpful; do not select one without evidence.
- `unresolved_items`: objects with `section` (string or null), `pages` (array), `text` (original text), and `reason` (string), for content that could not be assigned safely.

No numeric confidence scores, job suitability score, inferred skills, or rewritten CV content are part of this contract.
