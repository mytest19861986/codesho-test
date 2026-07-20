# UI-AUTH-003B1 handoff

The development-only `/login` route uses same-origin CSRF bootstrap followed by
the passcode login endpoint. Persian and Arabic-Indic passcode digits are
normalized client-side; the backend receives six ASCII digits. No backend files
were changed. Real Alpha activation, Production release, and protected
promotion remain blocked by `AUTH-PASSCODE-CHANGE-001F2-CLAUDE-VERIFICATION-DEBT`.
