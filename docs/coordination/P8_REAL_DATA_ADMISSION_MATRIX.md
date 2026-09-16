# P8 Real Data Admission Matrix

| Data Category | Specific Data Element | Permitted in Pilot? | Storage & Isolation Requirement | Retention & Destruction Policy |
|---|---|---|---|---|
| Student Identity | Synthetic/Obfuscated Username | YES | PostgreSQL Tenant RLS, hashed identifier | Kept during pilot; shredded on exit |
| Student Identity | Real Legal Name, National ID | NO (FORBIDDEN) | Must NOT enter system; fail-closed rejection | Zero retention; immediate drop |
| Guardian Data | Verified Guardian User Reference | YES | Tenant RLS, composite foreign key | Shredded upon pilot termination |
| Guardian Data | Personal Financial / Banking Info | NO (FORBIDDEN) | Forbidden; no billing schema permitted | Zero retention; immediate drop |
| Activity & Progress | Lesson Completion Timestamp | YES | Append-only learning progress table | Preserved only for pilot verification |
| Activity & Progress | Formative Assignment Submissions | YES | Isolated per-tenant object storage / DB | Crypto-shredded at pilot conclusion |
| Biometric Data | Facial Images, Voice Prints, Video | NO (FORBIDDEN) | Absolute architectural ban | Absolute rejection at API gateway |
| System Telemetry | Client IP, User-Agent, Session Nonce | YES (BOUNDED) | Anonymized audit logs, zero raw credentials | Standard 30-day security rotation |
