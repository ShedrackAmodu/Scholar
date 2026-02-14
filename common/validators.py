from django.core.exceptions import ValidationError
from django.utils import timezone
import re


def validate_nigerian_phone(value):
    """Validate Nigerian phone numbers"""
    # Remove any spaces or dashes
    phone = re.sub(r'[\s\-]', '', value)
    
    # Nigerian phone patterns
    patterns = [
        r'^\+234[0-9]{10}$',  # +234XXXXXXXXXX
        r'^0[7-9][0-9]{9}$',   # 0XXXXXXXXXXX
        r'^[7-9][0-9]{9}$',    # XXXXXXXXXX (without leading 0)
    ]
    
    valid = any(re.match(pattern, phone) for pattern in patterns)
    
    if not valid:
        raise ValidationError("Enter a valid Nigerian phone number.")


def validate_future_date(value):
    """Ensure date is not in the past"""
    if value < timezone.now().date():
        raise ValidationError("Date cannot be in the past.")


def validate_past_date(value):
    """Ensure date is not in the future"""
    if value > timezone.now().date():
        raise ValidationError("Date cannot be in the future.")


def validate_file_extension(value, allowed_extensions):
    """Validate file extension"""
    ext = value.name.split('.')[-1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")


def validate_file_size(value, max_size_mb=5):
    """Validate file size"""
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"File size cannot exceed {max_size_mb}MB.")


def validate_score(value, max_score=100):
    """Validate academic scores"""
    if value < 0 or value > max_score:
        raise ValidationError(f"Score must be between 0 and {max_score}.")


def validate_percentage(value):
    """Validate percentage values"""
    if value < 0 or value > 100:
        raise ValidationError("Percentage must be between 0 and 100.")


def validate_email_domain(value, allowed_domains=None):
    """Validate email domain"""
    if allowed_domains:
        domain = value.split('@')[-1]
        if domain not in allowed_domains:
            raise ValidationError(f"Email domain must be one of: {', '.join(allowed_domains)}")
