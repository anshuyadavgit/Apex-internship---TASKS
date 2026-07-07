-- Q1: Top 5 products by revenue in the last 6 months of data
SELECT
        p.Product,
        p.Category,
        SUM(f.Total_Sales)          AS total_revenue,
        SUM(f.Quantity)             AS total_units_sold,
        COUNT(DISTINCT f.Order_ID)  AS num_orders
    FROM fact_sales f
    JOIN dim_products p ON f.Product = p.Product
    WHERE f.Order_Date >= date((SELECT MAX(Order_Date) FROM fact_sales), '-6 months')
    GROUP BY p.Product, p.Category
    ORDER BY total_revenue DESC
    LIMIT 5;

-- Q2: Monthly revenue trend across the full period
SELECT
        Order_Year,
        Order_Month,
        ROUND(SUM(Total_Sales), 2) AS monthly_revenue,
        COUNT(DISTINCT Order_ID)   AS num_orders
    FROM fact_sales
    GROUP BY Order_Year, Order_Month
    ORDER BY Order_Year, Order_Month;

-- Q3: Which city generates the highest total revenue and highest average order value?
SELECT
        c.City,
        COUNT(DISTINCT f.Order_ID)        AS num_orders,
        ROUND(SUM(f.Total_Sales), 2)      AS total_revenue,
        ROUND(AVG(f.Total_Sales), 2)      AS avg_order_value
    FROM fact_sales f
    JOIN dim_customers c ON f.Customer_ID = c.Customer_ID
    GROUP BY c.City
    ORDER BY total_revenue DESC;

-- Q4: Which customer age group contributes the most revenue, and what is their AOV?
SELECT
        CASE
            WHEN c.Age BETWEEN 18 AND 25 THEN '18-25'
            WHEN c.Age BETWEEN 26 AND 35 THEN '26-35'
            WHEN c.Age BETWEEN 36 AND 45 THEN '36-45'
            WHEN c.Age BETWEEN 46 AND 55 THEN '46-55'
            WHEN c.Age BETWEEN 56 AND 65 THEN '56-65'
            ELSE '65+'
        END AS age_group,
        COUNT(DISTINCT f.Order_ID)   AS num_orders,
        ROUND(SUM(f.Total_Sales), 2) AS total_revenue,
        ROUND(AVG(f.Total_Sales), 2) AS avg_order_value
    FROM fact_sales f
    JOIN dim_customers c ON f.Customer_ID = c.Customer_ID
    GROUP BY age_group
    ORDER BY total_revenue DESC;

-- Q5: Gender-wise revenue and units sold, broken down by category
SELECT
        c.Gender,
        p.Category,
        SUM(f.Quantity)              AS units_sold,
        ROUND(SUM(f.Total_Sales), 2) AS total_revenue
    FROM fact_sales f
    JOIN dim_customers c ON f.Customer_ID = c.Customer_ID
    JOIN dim_products  p ON f.Product = p.Product
    GROUP BY c.Gender, p.Category
    ORDER BY c.Gender, total_revenue DESC;

-- Q6: Top 10 customers by total spend, with city and preferred category
SELECT
        c.Customer_ID,
        c.Customer_Name,
        c.City,
        ROUND(SUM(f.Total_Sales), 2)   AS total_spend,
        COUNT(DISTINCT f.Order_ID)     AS num_orders,
        (SELECT p2.Category
           FROM fact_sales f2
           JOIN dim_products p2 ON f2.Product = p2.Product
          WHERE f2.Customer_ID = c.Customer_ID
          GROUP BY p2.Category
          ORDER BY SUM(f2.Total_Sales) DESC
          LIMIT 1)                     AS preferred_category
    FROM fact_sales f
    JOIN dim_customers c ON f.Customer_ID = c.Customer_ID
    GROUP BY c.Customer_ID, c.Customer_Name, c.City
    ORDER BY total_spend DESC
    LIMIT 10;

-- Q7: Weekday vs weekend sales pattern (order count, revenue, AOV)
SELECT
        CASE WHEN Is_Weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
        COUNT(DISTINCT Order_ID)     AS num_orders,
        ROUND(SUM(Total_Sales), 2)   AS total_revenue,
        ROUND(AVG(Total_Sales), 2)   AS avg_order_value
    FROM fact_sales
    GROUP BY day_type;

