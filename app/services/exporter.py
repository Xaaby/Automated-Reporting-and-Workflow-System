import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text


def export_to_csv(
    db: Session,
    sql_query: str,
    output_dir: str,
    report_name: str
) -> Tuple[str, int]:
    """
    Execute SQL query and export results to CSV file.
    
    Args:
        db: Database session
        sql_query: SQL query to execute
        output_dir: Directory to save CSV file
        report_name: Name of the report (for file naming)
    
    Returns:
        Tuple of (output_path, row_count)
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c for c in report_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_')
    filename = f"{safe_name}_{timestamp}.csv"
    output_path = os.path.join(output_dir, filename)
    
    # Execute SQL query
    result = db.execute(text(sql_query))
    rows = result.fetchall()
    
    # Get column names from result
    column_names = result.keys()
    
    # Write to CSV
    row_count = 0
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(column_names)
        
        # Write data rows
        for row in rows:
            writer.writerow(row)
            row_count += 1
    
    return output_path, row_count
