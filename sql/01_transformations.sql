DROP VIEW IF EXISTS customer_features;
DROP VIEW IF EXISTS monthly_revenue;

CREATE VIEW customer_features AS
SELECT
    month,
    customer_id,
    region,
    segment,
    tenure_months,
    products_held,
    transactions,
    engagement_score,
    support_tickets,
    marketing_touch,
    monthly_revenue,
    churned,
    LAG(monthly_revenue, 1) OVER (PARTITION BY customer_id ORDER BY month) AS revenue_lag_1,
    AVG(monthly_revenue) OVER (
        PARTITION BY customer_id ORDER BY month ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
    ) AS revenue_rolling_3,
    AVG(engagement_score) OVER (
        PARTITION BY customer_id ORDER BY month ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) AS engagement_rolling_4
FROM customer_monthly;

CREATE VIEW monthly_revenue AS
SELECT
    month,
    ROUND(SUM(monthly_revenue), 2) AS revenue,
    COUNT(DISTINCT customer_id) AS active_customers,
    ROUND(AVG(churned), 4) AS churn_rate
FROM customer_monthly
GROUP BY month;

