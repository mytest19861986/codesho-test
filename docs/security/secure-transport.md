# Secure transport boundary

Codesho terminates TLS at a trusted ingress or reverse proxy. The proxy owns
certificates and must overwrite, rather than pass through, the effective
`X-Forwarded-Proto` value. The bundled Nginx configuration does this with
`proxy_set_header X-Forwarded-Proto $scheme`; the backend is not a public TLS
listener.

`CODESHO_SECURE_TRANSPORT` is the explicit hardened-mode switch. It defaults to
`false` for local HTTP Compose development. Production settings fail closed
unless it is enabled. In hardened mode Django enables secure session/CSRF
cookies, trusts the proxy protocol marker, and uses the explicitly configured
redirect/HSTS values. HSTS defaults to a short 300-second rollout value with
`includeSubDomains` and `preload` disabled; operators must deliberately choose
longer values after validating every hostname and certificate boundary.

The backend network must remain private to the trusted proxy. Direct public
exposure of the Django/Gunicorn port is not an approved deployment topology;
an arbitrary client-supplied forwarded header is not a substitute for the
proxy boundary. Local Compose remains loopback-bound HTTP and does not enable
the hardened switch or secure cookies.
