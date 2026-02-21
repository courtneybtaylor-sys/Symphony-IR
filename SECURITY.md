# Security Policy

## Reporting Vulnerabilities

**DO NOT** open a public GitHub issue for security vulnerabilities. Public disclosure could put users at risk.

Instead, please report security vulnerabilities responsibly by emailing the maintainers directly at **security@symphonyir.dev** or opening a [private security advisory](https://docs.github.com/en/code-security/repository-security-advisories/creating-a-repository-security-advisory).

When reporting a vulnerability, please include:

* **Description** — Clear explanation of the vulnerability
* **Steps to reproduce** — Minimal steps that demonstrate the issue
* **Impact assessment** — Potential security implications (authentication bypass, data leakage, code execution, etc.)
* **Proof of concept** — Code snippet or configuration that triggers the vulnerability (optional but helpful)
* **Your name** — For attribution in security advisories (optional)

We will acknowledge your report within 48 hours and provide a timeline for patching.

## Supported Versions

We provide security updates for the following versions:

| Version | Status | Support |
|---------|--------|---------|
| Latest (main branch) | Active | Full support |
| Previous release | Maintenance | Security fixes only |
| Older releases | End-of-life | Community support |

## Security Considerations

### API Key Management

Symphony-IR stores API keys using the system's native credential manager (Windows Credential Manager, macOS Keychain, Linux Secret Service). **Never commit API keys** to version control.

### AI Provider Interactions

* Claude API calls are made over HTTPS with TLS 1.3+
* Anthropic API keys are transmitted securely and not logged
* Ollama (local) runs with in-process communication (no network exposure by default)

### Dependency Security

We use [GitHub Dependabot](https://github.com/dependabot) to track and alert on known vulnerabilities in dependencies. Updates are applied automatically for patch and minor versions.

To report a vulnerability in a third-party dependency:
1. Check if it's already tracked in [our security advisories](https://github.com/courtneybtaylor-sys/Symphony-IR/security/advisories)
2. If not, report it to the upstream dependency maintainers
3. Optionally notify us so we can coordinate patching

### Code Signing

Binaries distributed via installers are code-signed to prevent tampering:

* **Windows**: Signed with EV (Extended Validation) certificate
* **macOS**: Signed and notarized for Gatekeeper bypass
* **Linux**: AppImage includes GPG signature verification

## Security Best Practices

When using Symphony-IR:

✅ **DO**:
* Keep Symphony-IR and dependencies updated
* Store API keys in system credential manager (not .env files)
* Review workflow definitions before execution
* Use unique API keys per environment (dev, staging, prod)

❌ **DON'T**:
* Commit API keys to version control
* Run untrusted workflow templates
* Expose API keys in logs or debug output
* Share credentials between users or systems

## Responsible Disclosure

We believe in responsible disclosure. If you discover a security vulnerability:

1. **Do** report it privately
2. **Do** give us time to patch (typically 30-90 days depending on severity)
3. **Don't** publicly disclose until we've released a fix
4. **Don't** access data or systems without permission

Thank you for helping keep Symphony-IR secure.

## References

* [OWASP Top 10](https://owasp.org/www-project-top-ten/)
* [CWE Top 25](https://cwe.mitre.org/top25/)
* [Responsible Disclosure Policy](https://www.eff.org/deeplinks/2013/03/responsible-disclosure-security-research)
