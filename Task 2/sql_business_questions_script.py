"""
ApexPlanet Data Analytics Internship — Task 2
SQL for Business Questions

Builds a small relational schema (fact + 2 dimension tables) in SQLite from
the Task 1 cleaned dataset, then runs 7 business-question queries that
exercise filtering, aggregation, and multi-table joins.

Schema:
  dim_customers(Customer_ID PK, Customer_Name, Age, Gender, City)
  dim_products(Product PK, Category)
  fact_sales(Order_ID PK, Order_Date, Customer_ID FK, Product FK,
             Quantity, Unit_Price, Total_Sales, Order_Year, Order_Month,
             Order_Weekday, Is_Weekend)
"""

import pandas as pd
import sqlite3

DB_PATH = "apexplanet_sales.db"
SRC = "ApexPlanet_Cleaned_Dataset.xlsx"

df = pd.read_excel(SRC)

# ---------------------------------------------------------------------------
# BUILD NORMALIZED SCHEMA
# ---------------------------------------------------------------------------
dim_customers = (
    df.sort_values("Order_Date")
    .drop_duplicates(subset=["Customer_ID"], keep="first")[["Customer_ID", "Customer_Name", "Age", "Gender", "City"]]
    .reset_index(drop=True)
)

dim_products = (
    df.drop_duplicates(subset=["Product"])[["Product", "Category"]]
    .reset_index(drop=True)
)

fact_sales = df[[
    "Order_ID", "Order_Date", "Customer_ID", "Product", "Quantity",
    "Unit_Price", "Total_Sales", "Order_Year", "Order_Month",
    "Order_Weekday", "Is_Weekend",
]].copy()
fact_sales["Order_Date"] = fact_sales["Order_Date"].astype(str)

conn = sqlite3.connect(DB_PATH)
dim_customers.to_sql("dim_customers", conn, if_exists="replace", index=False)
dim_products.to_sql("dim_products", conn, if_exists="replace", index=False)
fact_sales.to_sql("fact_sales", conn, if_exists="replace", index=False)
conn.execute("CREATE INDEX IF NOT EXISTS idx_fact_customer ON fact_sales(Customer_ID)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_fact_product ON fact_sales(Product)")
conn.commit()
print(f"Schema built: dim_customers({len(dim_customers)}), dim_products({len(dim_products)}), "
      f"fact_sales({len(fact_sales)})")

# ---------------------------------------------------------------------------
# 7 BUSINESS QUESTIONS
# ---------------------------------------------------------------------------
QUERIES = {

"Q1: Top 5 products by revenue in the last 6 months of data": """
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
""",

"Q2: Monthly revenue trend across the full period": """
    SELECT
        Order_Year,
        Order_Month,
        ROUND(SUM(Total_Sales), 2) AS monthly_revenue,
        COUNT(DISTINCT Order_ID)   AS num_orders
    FROM fact_sales
    GROUP BY Order_Year, Order_Month
    ORDER BY Order_Year, Order_Month;
""",

"Q3: Which city generates the highest total revenue and highest average order value?": """
    SELECT
        c.City,
        COUNT(DISTINCT f.Order_ID)        AS num_orders,
        ROUND(SUM(f.Total_Sales), 2)      AS total_revenue,
        ROUND(AVG(f.Total_Sales), 2)      AS avg_order_value
    FROM fact_sales f
    JOIN dim_customers c ON f.Customer_ID = c.Customer_ID
    GROUP BY c.City
    ORDER BY total_revenue DESC;
""",

"Q4: Which customer age group contributes the most revenue, and what is their AOV?": """
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
""",

"Q5: Gender-wise revenue and units sold, broken down by category": """
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
""",

"Q6: Top 10 customers by total spend, with city and preferred category": """
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
""",

"Q7: Weekday vs weekend sales pattern (order count, revenue, AOV)": """
    SELECT
        CASE WHEN Is_Weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
        COUNT(DISTINCT Order_ID)     AS num_orders,
        ROUND(SUM(Total_Sales), 2)   AS total_revenue,
        ROUND(AVG(Total_Sales), 2)   AS avg_order_value
    FROM fact_sales
    GROUP BY day_type;
""",
}

# ---------------------------------------------------------------------------
# RUN + SAVE RESULTS
# ---------------------------------------------------------------------------
with open("sql_business_questions.sql", "w") as f:
    for title, query in QUERIES.items():
        f.write(f"-- {title}\n{query.strip()}\n\n")

results_html = []
for title, query in QUERIES.items():
    print(f"\n=== {title} ===")
    result = pd.read_sql_query(query, conn)
    print(result.to_string(index=False))
    results_html.append((title, result))

conn.close()

# save all results to a single Excel workbook, one sheet per question
with pd.ExcelWriter("sql_query_results.xlsx", engine="openpyxl") as writer:
    for i, (title, result) in enumerate(results_html, start=1):
        sheet_name = f"Q{i}"
        result.to_excel(writer, sheet_name=sheet_name, index=False)

print("\nSaved: sql_business_questions.sql, sql_query_results.xlsx, apexplanet_sales.db")
