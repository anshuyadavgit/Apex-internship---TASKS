# ApexPlanet Data Analytics Internship — Task 1: Data Immersion & Wrangling

## 📌 Objective
Get hands-on with a real-world sales transactions dataset and practice the critical first step of any analytics project: **acquiring, profiling, cleaning, and preparing data for analysis.**

## 📂 Dataset
**Source file:** `ApexPlanet_DataAnalytics_Dataset.xlsx` (sheet: `Sales_Dataset`)
**Size:** 1,000 rows × 12 columns
**Domain:** Retail sales transactions — order details, customer demographics, product/category, pricing, and revenue.

| Column | Description |
|---|---|
| Order_ID | Unique transaction identifier |
| Order_Date | Date the order was placed |
| Customer_ID / Customer_Name | Customer identifiers |
| Age, Gender, City | Customer demographics |
| Product, Category | What was purchased |
| Quantity, Unit_Price, Total_Sales | Order economics |

Full column-by-column definitions, data types, and business relevance are documented in the **Data Dictionary** sheet of the deliverable workbook.

## 🔍 Data Quality Issues Found
| Issue | Detail |
|---|---|
| Missing values | Age missing in 20 rows (2.0%); City missing in 13 rows (1.3%) |
| Duplicate IDs | 9 rows shared the same `Order_ID` (`ORD100050`) despite being distinct transactions — a source-system ID collision, not a true duplicate |
| Referential inconsistency | 52 `Customer_ID`s were linked to more than one `Customer_Name` (105 rows) |
| Outliers | 19 legitimate high-value transactions flagged in `Total_Sales` via the 1.5×IQR rule (no outliers in Age, Quantity, or Unit_Price) |
| Formatting | Dates and categorical text fields were already consistently formatted |
| Business-logic check | Verified `Total_Sales = Quantity × Unit_Price` holds across all 1,000 rows — 0 mismatches |

Full findings and the action taken for each issue are documented in the **Data Quality Report** sheet.

## 🛠️ Cleaning & Transformation Steps
1. Converted `Order_Date` from text to a proper datetime type
2. Trimmed whitespace / standardized casing on all text fields
3. Imputed missing `Age` using the median age for the customer's city (fallback: overall median)
4. Filled missing `City` with `"Unknown"` rather than guessing or dropping rows
5. Disambiguated colliding `Order_ID`s with a traceable suffix (e.g. `ORD100050-1`, `-2`, …)
6. Flagged (not silently corrected) `Customer_ID`→`Customer_Name` conflicts for analyst review
7. Flagged statistical outliers in Age, Quantity, Unit_Price, and Total_Sales without removing them
8. **Feature engineering:** `Order_Year`, `Order_Month`, `Order_Month_Name`, `Order_Quarter`, `Order_Weekday`, `Is_Weekend`, `Age_Group`, `Price_Tier`, `Revenue_Per_Unit`

Every change is logged in plain English in the **Cleaning Log** sheet for full transparency and reproducibility.

## 📦 Task 1 Deliverables
| File | Description |
|---|---|
| `ApexPlanet_Task1_Deliverable.xlsx` | Multi-sheet workbook: Data Dictionary → Data Quality Report → Cleaning Log → final Cleaned Dataset |
| `data_cleaning_script.py` | Standalone, reproducible Python/Pandas script that performs the full profiling, cleaning, and transformation pipeline |

### Final Cleaned Dataset
- **1,000 rows × 28 columns**
- 0 missing values in all core business columns
- Transparent flags (`*_Imputed`, `*_Outlier`, `Customer_ID_Name_Conflict`) preserve full auditability — nothing was silently altered or dropped

### ▶️ How to Run
```bash
pip install pandas openpyxl numpy
python data_cleaning_script.py
```
This regenerates `ApexPlanet_Cleaned_Dataset.xlsx` from the raw source file.

---

# Task 2: Exploratory Data Analysis (EDA) & Business Intelligence

## 📌 Objective
Uncover patterns, trends, and relationships within the cleaned dataset, and build proficiency in SQL for data extraction and basic dashboarding.

## 🔎 What Was Done
1. **Descriptive Statistics & Univariate Analysis** — summary stats for all numerical fields (Age, Quantity, Unit_Price, Total_Sales) and categorical fields (Gender, City, Product, Category, Age_Group, Price_Tier), with histograms and bar charts of each distribution.
2. **SQL for Business Questions** — built a normalized relational schema (`dim_customers`, `dim_products`, `fact_sales`) in SQLite and answered 7 business questions using filtering, aggregation, and multi-table joins:
   - Top 5 products by revenue in the last 6 months
   - Monthly revenue trend across the full period
   - Revenue & average order value by city
   - Revenue contribution by customer age group
   - Gender × category revenue/units breakdown
   - Top 10 customers by total spend (with preferred category)
   - Weekday vs. weekend sales pattern
3. **Multivariate Analysis & Correlation** — correlation heatmap, Age vs. Total Sales scatter plot, Unit Price vs. Quantity scatter plot, Age-by-Category boxplot, and a full pair plot across key numerical variables.
4. **Static Dashboard Mock-up** — a 3-slide PowerPoint mock-up of an executive KPI dashboard (KPI cards, revenue trend, category/city breakdowns, gender and weekday/weekend splits) plus a slide proposing the KPIs worth tracking going forward.

## 📊 Key Insights
- **Electronics** (led by Mobile and Laptop) is the strongest category by both order volume and revenue (~36% of total revenue).
- `Total_Sales` correlates moderately with `Quantity` (r≈0.65) and `Unit_Price` (r≈0.69) — expected, since it's their product — but **Age has no meaningful relationship with spend** (|r| < 0.03).
- **Kolkata, Bengaluru, and Patna** are the top three cities by revenue; **Pune** has the highest average order value despite fewer orders.
- The **26–35 age group** is the single largest revenue contributor; the **18–25 group** spends the most per order on average.
- Revenue is fairly stable month-to-month with no strong seasonality; weekday/weekend split roughly matches the 5:2 day-count ratio.

## 📦 Task 2 Deliverables
| File | Description |
|---|---|
| `ApexPlanet_Task2_EDA_Report.docx` | Full report: descriptive stats, univariate & multivariate charts, SQL question results, key takeaways |
| `eda_analysis_script.py` | Python/Pandas + Matplotlib/Seaborn script generating all summary stats and charts |
| `sql_business_questions_script.py` | Builds the SQLite relational schema and runs all 7 business-question queries |
| `sql_business_questions.sql` | Raw SQL text for all 7 queries (schema: `dim_customers`, `dim_products`, `fact_sales`) |
| `sql_query_results.xlsx` | Query results, one sheet per question |
| `apexplanet_sales.db` | The SQLite database itself (browsable with any SQLite client) |
| `ApexPlanet_Task2_Dashboard_Mockup.pptx` | Static KPI dashboard mock-up + proposed-KPIs slide |

### ▶️ How to Run
```bash
pip install pandas openpyxl numpy matplotlib seaborn
python eda_analysis_script.py              # generates ./charts/*.png + summary CSVs
python sql_business_questions_script.py    # builds apexplanet_sales.db + runs all 7 queries
```

## 🧰 Tools Used
- Python 3 (Pandas, NumPy, Matplotlib, Seaborn)
- SQL (SQLite)
- PowerPoint (dashboard mock-up)

## 📁 Project Roadmap
- ✅ **Task 1** — Data Immersion & Wrangling
- ✅ **Task 2** — Exploratory Data Analysis (EDA) & Business Intelligence *(this repo)*
- ⬜ Task 3 — Deep-Dive Analysis & Interactive Dashboarding
- ⬜ Task 4 — Data Storytelling & Statistical Validation
- ⬜ Task 5 — Capstone Integration & Portfolio Finalization

---
*Part of the ApexPlanet Data Analytics Internship program.*
