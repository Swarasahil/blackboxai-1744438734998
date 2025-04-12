import re
import requests
from urllib.parse import urlparse
import whois
from bs4 import BeautifulSoup
from datetime import datetime

def analyze_url(url):
    """Analyze a URL for potential phishing indicators."""
    features = extract_features(url)
    risk_factors = []
    risk_score = 0

    # Check URL length
    if features['url_length'] > 75:
        risk_factors.append("Unusually long URL")
        risk_score += 0.2

    # Check for IP address in domain
    if features['has_ip']:
        risk_factors.append("IP address used instead of domain name")
        risk_score += 0.3

    # Check for @ symbol
    if features['has_at_symbol']:
        risk_factors.append("@ symbol in URL")
        risk_score += 0.3

    # Check for double slash redirect
    if features['double_slash_redirect']:
        risk_factors.append("Double slash redirect detected")
        risk_score += 0.2

    # Check for prefix/suffix
    if features['prefix_suffix']:
        risk_factors.append("Prefix or suffix used in domain")
        risk_score += 0.2

    # Check number of subdomains
    if features['subdomain_count'] > 3:
        risk_factors.append(f"Multiple subdomains ({features['subdomain_count']})")
        risk_score += 0.2

    # Check HTTPS protocol
    if not features['https_protocol']:
        risk_factors.append("No HTTPS security")
        risk_score += 0.2

    # Determine prediction
    prediction = "Legitimate"
    if risk_score >= 0.5:
        prediction = "Phishing"

    return {
        'prediction': prediction,
        'risk_score': round(risk_score, 2),
        'risk_factors': risk_factors,
        'features': features
    }

def extract_features(url):
    """Extract features from a URL for phishing detection."""
    features = {}
    
    # Basic URL features
    features['url_length'] = len(url)
    features['has_ip'] = bool(re.match(
        r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url))
    features['has_at_symbol'] = '@' in url
    features['double_slash_redirect'] = '//' in urlparse(url).path
    features['prefix_suffix'] = '-' in urlparse(url).netloc
    
    # Domain features
    domain = urlparse(url).netloc
    features['subdomain_count'] = len(domain.split('.')) - 1
    features['https_protocol'] = url.startswith('https://')

    try:
        # Additional security checks
        response = requests.get(url, timeout=5, verify=True)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for forms
        features['has_form'] = bool(soup.find('form'))
        
        # Check for suspicious titles
        title = soup.title.string.lower() if soup.title else ''
        features['suspicious_title'] = any(word in title for word in [
            'login', 'sign in', 'account', 'password', 'secure'])
        
        # SSL certificate check
        features['valid_ssl'] = response.ok
        
    except Exception:
        features['has_form'] = False
        features['suspicious_title'] = False
        features['valid_ssl'] = False

    try:
        # WHOIS information
        domain_info = whois.whois(domain)
        features['domain_age'] = (
            datetime.now() - domain_info.creation_date[0]
        ).days if domain_info.creation_date else 0
    except Exception:
        features['domain_age'] = 0

    return features

def is_valid_url(url):
    """Check if a URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
