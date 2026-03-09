# Security Policy

## Supported Versions

Currently supported versions with security updates:

| Version | Supported          |
|---------|-------------------|
| 2.x.x   | :white_check_mark: Yes |
| < 2.0   | :x: No              |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please do **NOT** create a public issue.

### How to Report

**Email**: Send an email to the project maintainers

Please include:

- A description of the vulnerability
- Steps to reproduce the vulnerability
- Affected versions
- Potential impact
- Suggested fix (if known)

### What Happens Next

1. **Acknowledgment**: We will acknowledge receipt of your report within 48 hours
2. **Investigation**: We will investigate the vulnerability
3. **Resolution**: We will work on a fix and provide a timeline
4. **Update**: We will update you on the progress
5. **Disclosure**: We will coordinate the disclosure with you

## Security Best Practices

### For Users

1. **Keep dependencies updated**
   ```bash
   pip install --upgrade -r requirements.txt
   pip install --upgrade pip
   ```

2. **Use virtual environments**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Never commit `.env` files**
   - The `.env` file contains sensitive credentials
   - Always use `.env.example` as a template
   - `.env` is already in `.gitignore`

4. **Review permissions**
   - Only grant necessary permissions to Feishu app
   - Rotate API keys if compromised

### For Developers

1. **Dependency scanning**
   ```bash
   pip install pip-audit
   pip-audit
   ```

2. **Secrets management**
   - Never hardcode credentials
   - Use environment variables for all secrets
   - Use `.env` for local development

3. **Code review**
   - All code changes should be reviewed
   - Pay special attention to data handling
   - Validate all user inputs

## Security-Related Configuration

### Environment Variables

Required variables (contains sensitive information):
- `FEISHU_APP_ID` - Feishu application ID
- `FEISHU_APP_SECRET` - Feishu application secret
- `DEEPSEEK_API_KEY` - DeepSeek API key

These should **never** be:
- Committed to version control
- Shared in public forums
- Logged in plain text

### File Permissions

Ensure proper file permissions:

```bash
# Make .env readable only by owner
chmod 600 .env

# Make scripts executable
chmod 755 *.py
```

## Security Features

### Input Validation

- B站视频 URL format validation
- File path sanitization
- API response validation

### Data Handling

- Temporary files are automatically cleaned up
- No sensitive data in logs
- Secure credential storage

### Network Security

- HTTPS for all API calls
- Proxy support for controlled environments
- No plain-text credentials in URLs

## Vulnerability Disclosure Process

1. **Report received**
   - Security team acknowledges receipt
   - Initial triage within 48 hours

2. **Investigation**
   - Confirm vulnerability
   - Assess severity and impact
   - Develop fix

3. **Fix Development**
   - Create fix in private branch
   - Test thoroughly
   - Code review

4. **Coordination**
   - Coordinate disclosure with reporter
   - Set disclosure date
   - Prepare patches

5. **Release**
   - Publish security advisory
   - Release fix
   - Update documentation

## Security Advisories

Past security advisories will be published in the GitHub Security Advisories section.

## Contact

For security-related questions:
- Create an issue with the `security` label
- Send an email to the maintainers

**Note**: For non-security issues, please use the regular [issue tracker](https://github.com/yourusername/bili2txt-agent/issues).
