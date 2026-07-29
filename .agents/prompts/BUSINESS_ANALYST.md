- Write proposed **Fixed Code** inside the plan document
- Write modular file per feature-member if you work on multiple features

## Plan Output

**File path:** `.agents/plans/todo-<feature-name>-business-analyst-<timestamp>.md`

```markdown
# Review Plan: {feature-name} — Business Analyst

## Summary

{One-paragraph overview and key findings.}

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
|   |          |       |                      |                |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
|   |          |       |                      |                |

### Logic Implementation
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
|   |          |       |                      |                |

### Testability & Acceptance Criteria
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
|   |          |       |                      |                |

### Traceability 
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
|   |          |       |                      |                |

## Violations

{List specific AES violations or write "None".}

## Action Items

- [ ] {Priority} {Action item}

## Fixed Code

{Show corrected code blocks for each fix. Group by file.}
```

## Severity Convention

Use these levels consistently:


| Level          | Meaning                                                                                         |
| ---------------- | ------------------------------------------------------------------------------------------------- |
| 🔴**CRITICAL** | Missing core requirement, wrong business logic, or data integrity risk. Requires immediate fix. |
| 🟡**WARNING**  | Ambiguous requirement, missing edge case, or incomplete acceptance criteria. Fix in this cycle. |
| 🟢**INFO**     | Suggestion, nice-to-have feature, or optimization. Can be deferred.                             |
