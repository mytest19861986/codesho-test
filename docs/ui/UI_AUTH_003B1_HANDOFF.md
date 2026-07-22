# UI-AUTH-003B1 handoff

The development-only `/login` route uses same-origin CSRF bootstrap followed by
the passcode login endpoint. Persian and Arabic-Indic passcode digits are
normalized client-side; the backend receives six ASCII digits. No backend files
were changed. The Claude verification debt is closed and documented at the
Task51 checkpoint. The dev-only `/login` route does not authorize Production
release, real Alpha activation, protected promotion, or any new UI/Auth scope;
those actions require separate approval and Task authorization.
