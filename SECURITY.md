# Security

## Security Measures

AnomReceipt has been developed with security in mind:

### Dependency Security

All dependencies are regularly checked for known vulnerabilities:

- **PyQt5** (>=5.15.0): No known vulnerabilities
- **PyYAML** (>=6.0): No known vulnerabilities
- **python-escpos** (>=3.0): No known vulnerabilities
- **Pillow** (>=10.3.0): Updated to address all known vulnerabilities

#### Pillow Vulnerabilities Fixed

Previous version (9.0.0) had the following vulnerabilities:
- Buffer overflow vulnerability (Fixed in 10.3.0)
- Denial of Service vulnerability (Fixed in 10.0.0)
- Bundled libwebp vulnerability (Fixed in 10.0.1)
- Data Amplification attack (Fixed in 9.2.0)

**Action Taken**: Updated to Pillow 10.3.0+

### Code Security

#### Exception Handling
- All exception handlers use specific exception types
- No bare `except:` clauses that could hide errors
- Proper logging of all exceptions

#### Input Validation
- Receipt width validated against printer capabilities (32-80 chars)
- Logo dimensions validated (width: 20-80 chars, height: 5-30 lines)
- File paths validated to prevent directory traversal
- UTF-8 encoding enforced for all file operations

#### Configuration Security
- VAT rates are configurable per template (not hard-coded)
- Default values defined as constants
- Settings validated before use

### Network Security

When using network printer connections:
- No credentials stored in plain text
- IP addresses validated
- Port numbers validated (1-65535)
- Connection errors logged but not exposed to UI in detail

### File System Security

- Templates loaded from specific directories only
- File extensions validated (.txt, .json, .yaml, .yml)
- UTF-8 encoding enforced
- No arbitrary code execution from templates
- Logo files restricted to text format

### Best Practices

1. **Run with Minimal Privileges**
   - Don't run as root unless necessary for USB access
   - Use udev rules for USB printer access instead

2. **Keep Dependencies Updated**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Validate Templates**
   - Review template files before loading
   - Validate YAML/JSON syntax
   - Check for suspicious content

4. **Secure Network Printers**
   - Use private networks for printers
   - Don't expose printers to public internet
   - Use firewall rules to restrict access

## Reporting Security Issues

If you discover a security vulnerability, please email the maintainers directly instead of opening a public issue.

## Security Checklist for Deployment

- [ ] All dependencies updated to latest secure versions
- [ ] Application running with minimal privileges
- [ ] USB printer access configured via udev rules
- [ ] Network printers on private network
- [ ] Template files reviewed and validated
- [ ] Firewall rules configured
- [ ] Logging enabled and monitored
- [ ] Regular security updates scheduled

## Compliance Notes

### Data Privacy
- No customer data is stored permanently
- Receipt data is transient (in memory only)
- No network transmission of customer data
- Local printer communication only

### Commercial Use
When deploying for commercial use:
- Obtain proper authorization for brand logos
- Comply with trademark regulations
- Follow PCI-DSS guidelines if processing card payments
- Implement additional security measures as required by industry

## Security Updates

### Version 1.0.0 (Current)
- ✓ Updated Pillow to 10.3.0+ (CVE fixes)
- ✓ Removed bare exception handlers
- ✓ Added input validation for all settings
- ✓ Configured VAT rates (not hard-coded)
- ✓ Added constants for magic numbers
- ✓ Improved error handling in printer disconnect

## Future Security Enhancements

Planned for future releases:
- Digital signature support for receipts
- Encrypted storage for template files
- Audit logging for all print operations
- Role-based access control
- Integration with HSM for key management
- Certificate-based printer authentication
