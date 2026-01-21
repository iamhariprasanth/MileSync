# Skill: Execute PRP

## Purpose
Execute a Product Requirement Plan step-by-step.

## Usage
```
/execute-prp <prp-filename>
```

## Process
1. Read the specified PRP file
2. Check off completed tasks
3. Execute tasks in sequence
4. Validate after each step
5. Update TASK.md with progress

## Execution Rules
- Follow task sequence strictly
- Run validation after each task
- Stop on errors - don't proceed until fixed
- Update success criteria checkboxes
- Document any discovered issues

## Validation Steps
After each task:
1. Check for syntax errors
2. Run relevant tests
3. Verify functionality
4. Update progress in PRP
