# Symphony-IR Security & Privacy

Symphony-IR includes comprehensive security measures to protect your data and API keys.

## 🔐 Security Features

### 1. API Key Security (Windows Credential Manager)

**Problem Fixed:** API keys were stored in plaintext configuration files.

**Solution:** All API keys are now encrypted using Windows Credential Manager (or system equivalent).

#### How It Works

```
Before (Insecure):
  config.json: { "api_key": "sk-..." }  ← Plaintext, visible to anyone

After (Secure):
  config.json: { "api_key": null }  ← File has no sensitive data
  Windows Credential Manager: Encrypted storage
```

#### Features

✅ **Encrypted Storage**
- Uses Windows Credential Manager on Windows
- Uses Keychain on macOS
- Uses Secret Service on Linux
- All via keyring library

✅ **Never Plaintext**
- API keys never saved to config files
- Automatic cleanup of old plaintext keys
- Migration script for existing keys

✅ **Secure Retrieval**
- Keys only in memory while needed
- Automatic cleanup after use
- No logging of credentials

#### Usage

**In Settings Tab:**
1. Paste your API key
2. Click "Save Settings"
3. Key is stored securely in system credential manager
4. Config file stays clean and shareable

**For Developers:**
```python
from gui.secure_credentials import SecureConfig

config = SecureConfig(Path(".orchestrator/config.json"))

# Retrieve API key from secure storage
api_key = config.get_api_key()

# Store API key securely
config.set_api_key("sk-...")

# Migrate from plaintext
migrated, failed = config.migrate_from_plaintext()
```

#### Migrating Existing Keys

If you have plaintext API keys, use the migration script:

```bash
# Interactive migration
python windows/migrate_credentials.py

# Automated migration (no prompts)
python windows/migrate_credentials.py --force

# Dry run (see what would be migrated)
python windows/migrate_credentials.py --dry-run
```

### 2. Session Redaction

**Problem Fixed:** Sessions saved with API keys, file paths, and other sensitive data.

**Solution:** Automatic redaction of sensitive information before saving.

#### What Gets Redacted

✅ **API Keys & Tokens**
- Anthropic API keys (sk-...)
- Generic tokens and auth tokens
- Bearer tokens
- Custom API keys

✅ **File Paths**
- Home directories (/home/user, C:\Users\user)
- Project paths
- System paths

✅ **Environment Variables**
- HOME, USER, USERNAME
- API_KEY, PASSWORD, etc.
- Custom environment variables

✅ **Contact Information**
- Email addresses
- IP addresses (IPv4)

✅ **Database Credentials**
- Database passwords
- Connection strings

#### Example

```json
Before (Sensitive):
{
  "task": "Review code",
  "context": {
    "file": "/home/user/project/auth.py",
    "api_key": "sk-1234567890abcdef"
  }
}

After (Redacted):
{
  "task": "Review code",
  "context": {
    "file": "***REDACTED***",
    "api_key": "***REDACTED***"
  }
}
```

#### Features

✅ **Automatic Redaction**
- Happens before saving sessions
- Pattern-based detection
- Dictionary key detection
- Nested structure support

✅ **Multiple Redaction Levels**
- NONE: No redaction (local use only)
- BASIC: Redact known sensitive items (default)
- FULL: Aggressive redaction of anything suspicious

✅ **Export Options**
- "Export Sanitized" button in History tab
- Choose redaction level
- Safe to share with others

#### Usage

**In History Tab:**
1. Select a session
2. Click "Export Sanitized"
3. Choose redaction level
4. File is safe to share or archive

**For Developers:**
```python
from gui.session_redaction import SessionRedactor, RedactionLevel

# Redact text
redacted = SessionRedactor.redact_text("My email: user@example.com")
# Result: "My email: ***REDACTED***"

# Redact session object
redacted_session = SessionRedactor.redact_session(session_dict)

# Create sanitized export
sanitized = SessionRedactor.create_sanitized_export(
    session,
    level=RedactionLevel.BASIC
)

# Redact session file
SessionRedactor.redact_file(Path("session.json"))
```

### 3. User-Friendly Error Messages

**Problem Fixed:** Technical errors confuse users and don't suggest solutions.

**Solution:** Plain English errors with actionable suggestions and help links.

#### What's Different

```
Before (Technical):
  "Connection refused: [Errno 111] Connection refused"

After (User-Friendly):
  ❌ Can't Connect to AI Service

  Symphony-IR couldn't reach the AI service.

  ✓ What you can do:
    1. If using Claude: Check your internet connection
    2. If using Ollama: Make sure Ollama is running (run 'ollama serve')
    3. Check that the service is running on the correct address
    4. Try restarting the service and try again

  📚 Learn more: [link to documentation]
```

#### Error Coverage

✅ **API Key Errors**
- Not found
- Invalid
- Expired
- Wrong format

✅ **Connection Errors**
- Can't connect
- Timeout
- Slow connection
- Network issues

✅ **Service Errors**
- Ollama not running
- Model not found
- Service overloaded

✅ **Configuration Errors**
- File not found
- Permission denied
- Invalid settings

✅ **Environment Errors**
- Missing dependencies
- Python issues
- Memory problems

#### Features

✅ **Severity Levels**
- Info (ℹ️) - Informational
- Warning (⚠️) - Be careful
- Error (❌) - Something failed
- Critical (🚨) - Major problem

✅ **Suggestions**
- Specific actionable steps
- Numbered list format
- Common solutions first

✅ **Help Links**
- Direct documentation links
- Relevant to the error
- GitHub issues for bugs

#### Usage

**In Application:**
All errors automatically convert to user-friendly format. Users see helpful suggestions instead of technical jargon.

**For Developers:**
```python
from gui.user_friendly_errors import ErrorHandler, ErrorTranslator

# Translate technical error
user_error = ErrorTranslator.translate(technical_error_message)
print(user_error)  # Shows friendly message with suggestions

# Handle exception
try:
    # ... code ...
except Exception as e:
    user_error = ErrorHandler.handle_error(e, context="my_function")
    # user_error.title
    # user_error.message
    # user_error.suggestions
    # user_error.help_link
```

---

## 🔒 Security Best Practices

### For Users

1. **Never share your API key**
   - It grants full access to your Claude account
   - Keep it private like a password
   - Don't commit it to version control

2. **Use secure storage**
   - Install keyring: `pip install keyring`
   - Migrate old plaintext keys
   - Settings tab shows secure status

3. **Redact before sharing**
   - Use "Export Sanitized" for sessions
   - Share with BASIC or FULL redaction level
   - Only keep NONE locally on trusted computers

4. **Check for sensitive data**
   - History tab shows redacted output
   - Sessions are auto-redacted before saving
   - File paths and emails are protected

### For Developers

1. **Never log credentials**
   - Use logger safely
   - Redact before logging
   - Test with fake credentials

2. **Use secure storage APIs**
   - SecureConfig for credentials
   - SessionRedactor for sessions
   - Never hardcode keys

3. **Handle errors safely**
   - Don't expose technical details to users
   - Use ErrorHandler for consistent messages
   - Log technical details separately

4. **Test security features**
   - Test credential migration
   - Test session redaction
   - Test error messages

---

## 📋 Security Checklist

- [ ] Install keyring: `pip install keyring`
- [ ] Migrate plaintext credentials: `python windows/migrate_credentials.py`
- [ ] Test secure storage: Settings → Add API key
- [ ] Test session redaction: History → Export Sanitized
- [ ] Verify error messages are user-friendly
- [ ] Never commit API keys to version control
- [ ] Use redacted exports when sharing

---

## 🚨 Common Security Issues

### Issue: "Keyring not installed"

**Solution:**
```bash
pip install keyring
python windows/migrate_credentials.py
```

### Issue: "Can't access credential manager"

**Cause:** Permissions issue or corrupted credential store.

**Solution:**
1. Run as Administrator
2. Try again
3. Contact support if persists

### Issue: "Session contains API key"

**Solution:**
1. Use History → Export Sanitized
2. Choose BASIC or FULL redaction
3. Share the redacted version

### Issue: "Forgot API key value"

**Solution:**
1. Get new key from https://console.anthropic.com
2. Update in Settings tab
3. Old key is discarded

---

## 🔐 Implementation Details

### Secure Credentials Module

Location: `gui/secure_credentials.py`

Features:
- CredentialManager class for system credential storage
- SecureConfig class for safe configuration
- Automatic migration from plaintext
- Environment variable support

### Session Redaction Module

Location: `gui/session_redaction.py`

Features:
- SessionRedactor class with pattern-based redaction
- RedactionLevel enum (NONE, BASIC, FULL)
- Redaction for text, dict, JSON, files
- Pattern library for common sensitive data

### User-Friendly Errors Module

Location: `gui/user_friendly_errors.py`

Features:
- ErrorTranslator for automatic translation
- ErrorHandler for exception handling
- Error patterns for common issues
- Severity levels and suggestions
- Pre-built error messages

---

## 📞 Support

### Get Help

- 📚 Documentation: Check docs/
- 🐛 Report Issues: GitHub issues
- 💬 Ask Questions: GitHub discussions
- 🔧 Troubleshooting: docs/TROUBLESHOOTING.md

### Report Security Issues

Found a security vulnerability?

**Do NOT** open a public issue.

Email security@symphony-ir.dev with:
1. Description of vulnerability
2. Steps to reproduce
3. Potential impact
4. Your contact information

---

## 🔄 Security Updates

- ✅ v1.0: Initial security features
  - API key encryption
  - Session redaction
  - User-friendly errors

---

**Your security is important to us.** All security features are enabled by default and require no user configuration.

Questions? Check the docs or open an issue on GitHub.
