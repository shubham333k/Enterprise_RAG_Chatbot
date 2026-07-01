## Engineering Team Handbook
### Acme Enterprise Solutions — Engineering Division
Version: 3.2 | Updated: March 2024

## Code Review Guidelines

All code changes must undergo peer review before being merged into the main branch. The following rules apply to the code review process:

1. Every pull request must have at least 2 approved reviews from senior engineers before merging.
2. Code reviews must be completed within 48 hours of PR submission on business days.
3. Reviewers must check for: correctness, security vulnerabilities, performance implications, test coverage, and documentation.
4. The submitter must respond to all review comments within 24 hours.
5. A PR cannot be merged if it has unresolved conversations.

Code review checklist:
- Unit tests are present and pass (minimum 80% coverage for new code)
- No hardcoded secrets, passwords, or API keys
- Error handling is comprehensive
- Logging is appropriate (not too verbose, not silent on errors)
- Database queries are optimized (no N+1 queries)

## Git Workflow

We follow the Gitflow branching model:
- `main` branch is always deployable and protected
- `develop` branch is the integration branch
- Feature branches: `feature/TICKET-ID-description`
- Bugfix branches: `bugfix/TICKET-ID-description`
- Release branches: `release/v1.x.x`
- Hotfix branches: `hotfix/TICKET-ID-description`

Branch naming rules: All branch names must be lowercase with hyphens. No spaces. Include the Jira ticket ID.

## Architecture Decision Records (ADR)

All significant architectural decisions must be documented as ADRs in the `/docs/adr/` directory. An ADR must include: context, decision, consequences, and alternatives considered. ADRs must be reviewed by the Tech Lead and CTO before implementation.

## Deployment Process

### Development Environment
Deployments to the dev environment are automatic on every commit to the `develop` branch via GitHub Actions CI/CD pipeline.

### Staging Environment
Deployments to staging require:
- All unit tests passing (100%)
- Integration tests passing
- Security scan passing (no critical or high vulnerabilities)
- Approval from QA Lead

### Production Environment
Production deployments require:
- All staging tests passing
- Load testing completed
- Rollback plan documented
- Approval from Tech Lead AND CTO
- Deployment window: Tuesday-Thursday, 10 PM to 2 AM IST only (maintenance window)

## On-Call Rotation

The on-call rotation cycles every week. On-call engineers are responsible for:
- Responding to PagerDuty alerts within 15 minutes during business hours
- Responding within 30 minutes during non-business hours
- Creating incident reports for P1 and P2 incidents
- On-call allowance: INR 5,000 per week

## Technology Stack Standards

Approved languages: Python (backend), TypeScript/JavaScript (frontend), Go (infrastructure tools)
Database standards: PostgreSQL for relational data, Redis for caching, Elasticsearch for full-text search
All new services must use Docker containers and be deployable to Kubernetes.
Infrastructure as Code: Terraform is mandatory for all cloud resource provisioning.

## Security Standards

- All API endpoints must require authentication (no public endpoints except health checks)
- TLS 1.3 minimum for all communications
- Secrets must be stored in AWS Secrets Manager or HashiCorp Vault — never in code or config files
- All data at rest must be encrypted using AES-256
- Penetration testing is conducted quarterly by the Security team

## Incident Response

P1 (Critical): Complete system outage. Response time: 15 minutes. Resolution target: 2 hours.
P2 (High): Major feature unavailable. Response time: 30 minutes. Resolution target: 4 hours.
P3 (Medium): Minor feature degraded. Response time: 4 hours. Resolution target: 24 hours.
P4 (Low): Cosmetic issues. Response time: 24 hours. Resolution target: 1 week.
