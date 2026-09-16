# P9 Operator Runbook

## 1. Overview
The Operator Runbook provides operational engineers and technical supervisors with explicit, unambiguous CLI and API command patterns to control synthetic rehearsal operations.

## 2. Standard Operating Procedures
### A. Initiating Synthetic Rehearsal
1. Verify system precheck:
   ```bash
   python manage.py check_synthetic_readiness
   ```
2. Verify token generation with strict scope binding:
   ```bash
   python manage.py issue_synthetic_token --tenant-id "a0000000-0000-0000-0000-000000000001"
   ```
3. Execute controlled start:
   ```bash
   python manage.py execute_synthetic_activation --token-file "/path/to/token.json"
   ```

### B. Triggering Maintenance Pause
```bash
python manage.py pause_synthetic_activation --tenant-id "a0000000-0000-0000-0000-000000000001" --reason "Routine DB Re-indexing"
```

### C. Resuming Operations
```bash
python manage.py resume_synthetic_activation --tenant-id "a0000000-0000-0000-0000-000000000001" --token-file "/path/to/token.json"
```

### D. Emergency Kill-Switch (Abort)
```bash
python manage.py emergency_abort_synthetic --tenant-id "a0000000-0000-0000-0000-000000000001" --reason "Security Anomaly Investigation"
```

## 3. Ambiguity & Human Error Prevention
- All dangerous commands (`emergency_abort`, `rollback`) require explicit confirmation flags (`--confirm-destructive-synthetic`).
- Distinct visual badges and terminal outputs clearly display `SYNTHETIC_TEST_ENVIRONMENT_ONLY` to prevent confusion with production.
