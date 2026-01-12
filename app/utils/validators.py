import re
from typing import Tuple


def validate_cron_expression(cron: str) -> Tuple[bool, str]:
    """
    Validate cron expression format.
    Expected format: "minute hour day month day_of_week"
    Each field can be: number, *, */n, n-m, n,m, or combinations.
    
    Args:
        cron: Cron expression string
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not cron or not isinstance(cron, str):
        return False, "Cron expression must be a non-empty string"
    
    parts = cron.strip().split()
    
    if len(parts) != 5:
        return False, "Cron expression must have exactly 5 fields: minute hour day month day_of_week"
    
    # Basic pattern for cron field validation
    cron_field_pattern = re.compile(
        r'^(\*|(\d+(-\d+)?)(,\d+(-\d+)?)*|(\d+|\*)/\d+)$'
    )
    
    field_names = ["minute", "hour", "day", "month", "day_of_week"]
    
    for i, part in enumerate(parts):
        # Allow * for all fields
        if part == "*":
            continue
        
        # Check if it matches basic cron field pattern
        if not cron_field_pattern.match(part):
            return False, f"Invalid {field_names[i]} field: {part}"
        
        # Additional validation for specific fields
        if i == 0:  # minute
            if not validate_minute_field(part):
                return False, f"Invalid minute field: {part}"
        elif i == 1:  # hour
            if not validate_hour_field(part):
                return False, f"Invalid hour field: {part}"
        elif i == 2:  # day
            if not validate_day_field(part):
                return False, f"Invalid day field: {part}"
        elif i == 3:  # month
            if not validate_month_field(part):
                return False, f"Invalid month field: {part}"
        elif i == 4:  # day_of_week
            if not validate_day_of_week_field(part):
                return False, f"Invalid day_of_week field: {part}"
    
    return True, ""


def validate_minute_field(field: str) -> bool:
    """Validate minute field (0-59)."""
    return validate_numeric_range(field, 0, 59)


def validate_hour_field(field: str) -> bool:
    """Validate hour field (0-23)."""
    return validate_numeric_range(field, 0, 23)


def validate_day_field(field: str) -> bool:
    """Validate day field (1-31)."""
    return validate_numeric_range(field, 1, 31)


def validate_month_field(field: str) -> bool:
    """Validate month field (1-12)."""
    return validate_numeric_range(field, 1, 12)


def validate_day_of_week_field(field: str) -> bool:
    """Validate day of week field (0-6, where 0=Sunday)."""
    return validate_numeric_range(field, 0, 6)


def validate_numeric_range(field: str, min_val: int, max_val: int) -> bool:
    """
    Validate that numeric values in cron field are within range.
    Handles: *, */n, n, n-m, n,m, n-m,n
    """
    if field == "*":
        return True
    
    # Handle */n
    if "/" in field:
        parts = field.split("/")
        if len(parts) != 2 or parts[0] != "*":
            return False
        try:
            val = int(parts[1])
            return min_val <= val <= max_val
        except ValueError:
            return False
    
    # Handle ranges and lists
    for segment in field.split(","):
        if "-" in segment:
            range_parts = segment.split("-")
            if len(range_parts) != 2:
                return False
            try:
                start = int(range_parts[0])
                end = int(range_parts[1])
                if not (min_val <= start <= max_val and min_val <= end <= max_val):
                    return False
                if start > end:
                    return False
            except ValueError:
                return False
        else:
            try:
                val = int(segment)
                if not (min_val <= val <= max_val):
                    return False
            except ValueError:
                return False
    
    return True


def validate_sql_query(sql_query: str) -> Tuple[bool, str]:
    """
    Basic SQL query validation.
    Checks for dangerous operations and basic syntax.
    
    Args:
        sql_query: SQL query string
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not sql_query or not isinstance(sql_query, str):
        return False, "SQL query must be a non-empty string"
    
    sql_upper = sql_query.upper().strip()
    
    # Check for empty query
    if not sql_upper:
        return False, "SQL query cannot be empty"
    
    # Basic check: should start with SELECT
    if not sql_upper.startswith("SELECT"):
        return False, "Only SELECT queries are allowed"
    
    # Check for dangerous operations (basic security)
    dangerous_keywords = [
        "DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT",
        "UPDATE", "EXEC", "EXECUTE", "GRANT", "REVOKE"
    ]
    
    for keyword in dangerous_keywords:
        if f" {keyword} " in sql_upper or sql_upper.startswith(keyword):
            return False, f"Dangerous operation detected: {keyword} queries are not allowed"
    
    return True, ""


def validate_output_format(output_format: str) -> Tuple[bool, str]:
    """
    Validate output format.
    
    Args:
        output_format: Output format string
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_formats = ["CSV", "JSON"]
    
    if not output_format or not isinstance(output_format, str):
        return False, "Output format must be a non-empty string"
    
    if output_format.upper() not in valid_formats:
        return False, f"Output format must be one of: {', '.join(valid_formats)}"
    
    return True, ""
