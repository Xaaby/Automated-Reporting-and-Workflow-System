-- Create enum types
CREATE TYPE run_status AS ENUM ('QUEUED', 'RUNNING', 'SUCCESS', 'FAILED');
CREATE TYPE notification_channel AS ENUM ('EMAIL', 'LOG');
CREATE TYPE notification_status AS ENUM ('SENT', 'FAILED');

-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sql_query TEXT NOT NULL,
    schedule_cron VARCHAR(100) NOT NULL,
    output_format VARCHAR(50) DEFAULT 'CSV',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create report_runs table
CREATE TABLE IF NOT EXISTS report_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    finished_at TIMESTAMP WITH TIME ZONE,
    status run_status NOT NULL DEFAULT 'QUEUED',
    row_count INTEGER,
    output_path VARCHAR(500),
    error_message TEXT
);

-- Create notification_log table
CREATE TABLE IF NOT EXISTS notification_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_run_id UUID NOT NULL REFERENCES report_runs(id) ON DELETE CASCADE,
    channel notification_channel NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status notification_status NOT NULL,
    message TEXT
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_report_runs_report_id ON report_runs(report_id);
CREATE INDEX IF NOT EXISTS idx_report_runs_status ON report_runs(status);
CREATE INDEX IF NOT EXISTS idx_report_runs_started_at ON report_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_reports_is_active ON reports(is_active);
CREATE INDEX IF NOT EXISTS idx_notification_log_report_run_id ON notification_log(report_run_id);

-- Insert sample data for testing
INSERT INTO reports (name, description, sql_query, schedule_cron, output_format, is_active) VALUES
(
    'Daily User Count',
    'Report showing daily active user count',
    'SELECT CURRENT_DATE as report_date, COUNT(DISTINCT user_id) as active_users FROM users WHERE last_active >= CURRENT_DATE',
    '0 9 * * *',
    'CSV',
    TRUE
),
(
    'Weekly Revenue Summary',
    'Weekly revenue aggregation report',
    'SELECT DATE_TRUNC(''week'', order_date) as week, SUM(amount) as total_revenue, COUNT(*) as order_count FROM orders GROUP BY DATE_TRUNC(''week'', order_date) ORDER BY week DESC',
    '0 8 * * 1',
    'CSV',
    TRUE
),
(
    'Monthly Product Sales',
    'Monthly breakdown of product sales',
    'SELECT product_id, product_name, SUM(quantity) as total_quantity, SUM(amount) as total_amount FROM order_items oi JOIN products p ON oi.product_id = p.id GROUP BY product_id, product_name ORDER BY total_amount DESC',
    '0 7 1 * *',
    'CSV',
    FALSE
)
ON CONFLICT DO NOTHING;
