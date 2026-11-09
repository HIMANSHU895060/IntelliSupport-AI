# Security and operational notes

- The default local bootstrap makes the first registered user admin when `ALLOW_FIRST_USER_ADMIN=true`. Set it to `false` in shared environments and provision admins with `scripts/create_admin.py`.
- JWTs expire after 12 hours. For production, consider short-lived access tokens, refresh-token rotation, MFA, revocation, rate limiting and secure cookie storage.
- MCP server tools are powerful. Keep the stdio process local or behind authenticated infrastructure; do not expose an unauthenticated MCP endpoint publicly.
- RAG content is demo knowledge. Replace it with reviewed company documentation and enforce tenant-level access controls for private documents.
- Human approval is required for refunds, account changes and destructive actions.
- AWS Terraform is a starting point. Add HTTPS/ACM, private-subnet egress/NAT, RDS, Secrets Manager, CloudWatch alarms, WAF, backups, least-privilege task roles and deployment pipeline before production.
