# Skill: Generate PRP

## Purpose
Generate a Product Requirement Plan (PRP) for a new feature.

## Usage
```
/generate-prp <feature-name>
```

## Output Format
Creates a new file in `.claude/PRPs/` with the following structure:

```markdown
# PRP-XXX: Feature Name

## Goal
[What this feature accomplishes]

## Why
[Business justification]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Files to Create/Update
[List of files with paths]

## Task Sequence
1. Task 1
2. Task 2

## Anti-Patterns
[Things to avoid]

## Gotchas
[Common pitfalls]
```

## Instructions
1. Analyze the feature request
2. Review existing codebase patterns
3. Identify all files that need changes
4. Create ordered task list
5. Document potential issues
