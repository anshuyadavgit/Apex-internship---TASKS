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

## 📦 Deliverables
| File | Description |
|---|---|
| `ApexPlanet_Task1_Deliverable.xlsx` | Multi-sheet workbook: Data Dictionary → Data Quality Report → Cleaning Log → final Cleaned Dataset |
| `data_cleaning_script.py` | Standalone, reproducible Python/Pandas script that performs the full profiling, cleaning, and transformation pipeline |

### Final Cleaned Dataset
- **1,000 rows × 28 columns**
- 0 missing values in all core business columns
- Transparent flags (`*_Imputed`, `*_Outlier`, `Customer_ID_Name_Conflict`) preserve full auditability — nothing was silently altered or dropped

## ▶️ How to Run
```bash
pip install pandas openpyxl numpy
python data_cleaning_script.py
```
This regenerates `ApexPlanet_Cleaned_Dataset.xlsx` from the raw source file.

## 🧰 Tools Used
- Python 3
- Pandas / NumPy
- openpyxl (Excel formatting/output)

## 📁 Project Roadmap
- ✅ **Task 1** — Data Immersion & Wrangling *(this repo)*
- ⬜ Task 2 — Exploratory Data Analysis (EDA) & Business Intelligence
- ⬜ Task 3 — Deep-Dive Analysis & Interactive Dashboarding
- ⬜ Task 4 — Data Storytelling & Statistical Validation
- ⬜ Task 5 — Capstone Integration & Portfolio Finalization

---
*Part of the ApexPlanet Data Analytics Internship program.*
