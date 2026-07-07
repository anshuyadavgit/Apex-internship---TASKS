"""
ApexPlanet Data Analytics Internship — Task 1
Data Immersion & Wrangling
Dataset: ApexPlanet_DataAnalytics_Dataset.xlsx (Sales_Dataset, 1000 rows x 12 cols)

This script:
  1. Loads the raw sales-transactions dataset
  2. Profiles it for data-quality issues
  3. Cleans, standardizes and transforms it
  4. Engineers new analysis-ready features
  5. Writes out a final, analysis-ready dataset + a cleaning log
"""

import pandas as pd
import numpy as np

RAW_PATH = "ApexPlanet_DataAnalytics_Dataset.xlsx"
OUT_PATH = "ApexPlanet_Cleaned_Dataset.xlsx"

log = []  # keeps a plain-English record of every change made, for the Cleaning_Log sheet


def note(msg):
    print(msg)
    log.append(msg)


# ---------------------------------------------------------------------------
# 1. LOAD
# ---------------------------------------------------------------------------
df = pd.read_excel(RAW_PATH)
note(f"Loaded raw dataset: {df.shape[0]} rows, {df.shape[1]} columns")

# ---------------------------------------------------------------------------
# 2. DATA QUALITY PROFILING (pre-clean snapshot)
# ---------------------------------------------------------------------------
missing_before = df.isnull().sum()
dupe_order_ids_before = df.duplicated(subset=["Order_ID"]).sum()
full_dupes_before = df.duplicated().sum()

note(f"Missing values before cleaning:\n{missing_before[missing_before > 0].to_dict()}")
note(f"Fully duplicated rows before cleaning: {full_dupes_before}")
note(f"Duplicate Order_IDs before cleaning: {dupe_order_ids_before}")

# ---------------------------------------------------------------------------
# 3. STANDARDIZE DATA TYPES / FORMATS
# ---------------------------------------------------------------------------
# Order_Date already in ISO yyyy-mm-dd text; convert to real datetime
df["Order_Date"] = pd.to_datetime(df["Order_Date"], format="%Y-%m-%d", errors="coerce")
bad_dates = df["Order_Date"].isnull().sum()
note(f"Order_Date converted to datetime. Unparseable dates: {bad_dates}")

# Trim stray whitespace / normalize case on text fields (defensive — protects
# against inconsistent formatting even though none was found in this batch)
text_cols = ["Customer_Name", "Gender", "City", "Product", "Category"]
for col in text_cols:
    df[col] = df[col].astype(str).str.strip()
    df.loc[df[col].isin(["nan", "None", ""]), col] = np.nan
note("Trimmed whitespace and normalized blank markers on text columns")

# Title-case City / Product / Category for consistent display
for col in ["City", "Product", "Category"]:
    df[col] = df[col].str.title()

# ---------------------------------------------------------------------------
# 4. HANDLE MISSING VALUES
# ---------------------------------------------------------------------------
# Age (20 missing, ~2%): impute with the median age for that customer's City;
# fall back to overall median if City is also unknown. Flag every imputed row
# so downstream analysis can exclude/include them transparently.
df["Age_Imputed"] = df["Age"].isnull()
city_median_age = df.groupby("City")["Age"].median()
overall_median_age = df["Age"].median()
df["Age"] = df.apply(
    lambda r: city_median_age.get(r["City"], overall_median_age) if pd.isnull(r["Age"]) else r["Age"],
    axis=1,
)
df["Age"] = df["Age"].round().astype(int)
note(f"Imputed {df['Age_Imputed'].sum()} missing Age values using median age per City")

# City (13 missing, ~1.3%): too few to safely impute a specific city, so label
# explicitly as 'Unknown' rather than guessing or dropping rows.
df["City_Imputed"] = df["City"].isnull()
df["City"] = df["City"].fillna("Unknown")
note(f"Filled {df['City_Imputed'].sum()} missing City values with 'Unknown'")

# ---------------------------------------------------------------------------
# 5. DE-DUPLICATION
# ---------------------------------------------------------------------------
# No fully duplicated rows exist, but 9 rows share the Order_ID 'ORD100050'
# even though they represent distinct transactions (different customers,
# products, dates). This is a source-system ID collision, not a duplicate
# record, so we preserve every row but issue each a unique, traceable ID.
dupe_mask = df.duplicated(subset=["Order_ID"], keep=False)
dupe_counter = {}
new_ids = []
for idx, row in df.iterrows():
    oid = row["Order_ID"]
    if dupe_mask[idx]:
        dupe_counter[oid] = dupe_counter.get(oid, 0) + 1
        new_ids.append(f"{oid}-{dupe_counter[oid]}")
    else:
        new_ids.append(oid)
df["Order_ID"] = new_ids
note(f"Resolved {dupe_mask.sum()} colliding Order_IDs by appending a disambiguating suffix (e.g. ORD100050-1)")

# Customer_ID mapped to more than one Customer_Name (52 IDs / 105 rows): flag
# for analyst awareness rather than silently rewriting names, since we cannot
# know which name is correct from the data alone.
name_counts = df.groupby("Customer_ID")["Customer_Name"].transform("nunique")
df["Customer_ID_Name_Conflict"] = name_counts > 1
note(f"Flagged {df['Customer_ID_Name_Conflict'].sum()} rows where Customer_ID maps to more than one Customer_Name")

# ---------------------------------------------------------------------------
# 6. OUTLIER CHECK
# ---------------------------------------------------------------------------
def iqr_outlier_flag(series):
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    return (series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)

for col in ["Age", "Quantity", "Unit_Price", "Total_Sales"]:
    flag_col = f"{col}_Outlier"
    df[flag_col] = iqr_outlier_flag(df[col])
    note(f"{col}: {df[flag_col].sum()} statistical outliers flagged (1.5x IQR rule)")

# Business-logic check: Total_Sales should equal Quantity * Unit_Price
df["_calc_total"] = (df["Quantity"] * df["Unit_Price"]).round(2)
mismatch = (df["_calc_total"] - df["Total_Sales"]).abs() > 0.01
note(f"Rows where Total_Sales != Quantity x Unit_Price: {mismatch.sum()}")
df.drop(columns=["_calc_total"], inplace=True)

# ---------------------------------------------------------------------------
# 7. FEATURE ENGINEERING
# ---------------------------------------------------------------------------
df["Order_Year"] = df["Order_Date"].dt.year
df["Order_Month"] = df["Order_Date"].dt.month
df["Order_Month_Name"] = df["Order_Date"].dt.strftime("%b")
df["Order_Quarter"] = "Q" + df["Order_Date"].dt.quarter.astype(str)
df["Order_Weekday"] = df["Order_Date"].dt.day_name()
df["Is_Weekend"] = df["Order_Date"].dt.dayofweek >= 5

age_bins = [0, 25, 35, 45, 55, 65, 200]
age_labels = ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
df["Age_Group"] = pd.cut(df["Age"], bins=age_bins, labels=age_labels, right=True)

price_bins = [0, 5000, 20000, 40000, np.inf]
price_labels = ["Budget (<5K)", "Mid (5K-20K)", "Premium (20K-40K)", "Luxury (40K+)"]
df["Price_Tier"] = pd.cut(df["Unit_Price"], bins=price_bins, labels=price_labels, right=False)

df["Revenue_Per_Unit"] = (df["Total_Sales"] / df["Quantity"]).round(2)
note("Engineered: Order_Year, Order_Month, Order_Month_Name, Order_Quarter, "
     "Order_Weekday, Is_Weekend, Age_Group, Price_Tier, Revenue_Per_Unit")

# ---------------------------------------------------------------------------
# 8. FINAL COLUMN ORDER
# ---------------------------------------------------------------------------
final_cols = [
    "Order_ID", "Order_Date", "Order_Year", "Order_Month", "Order_Month_Name",
    "Order_Quarter", "Order_Weekday", "Is_Weekend",
    "Customer_ID", "Customer_Name", "Customer_ID_Name_Conflict",
    "Age", "Age_Imputed", "Age_Group", "Gender",
    "City", "City_Imputed",
    "Product", "Category",
    "Quantity", "Unit_Price", "Price_Tier", "Total_Sales", "Revenue_Per_Unit",
    "Age_Outlier", "Quantity_Outlier", "Unit_Price_Outlier", "Total_Sales_Outlier",
]
df = df[final_cols]

# ---------------------------------------------------------------------------
# 9. POST-CLEAN VALIDATION
# ---------------------------------------------------------------------------
missing_after = df[["Order_ID", "Order_Date", "Customer_ID", "Age", "Gender",
                     "City", "Product", "Category", "Quantity", "Unit_Price",
                     "Total_Sales"]].isnull().sum().sum()
note(f"Missing values remaining in core business columns after cleaning: {missing_after}")
note(f"Final analysis-ready dataset: {df.shape[0]} rows, {df.shape[1]} columns")

# ---------------------------------------------------------------------------
# 10. SAVE
# ---------------------------------------------------------------------------
df.to_excel(OUT_PATH, index=False, sheet_name="Cleaned_Data")
with open("cleaning_log.txt", "w") as f:
    f.write("\n".join(log))

print("\nDone. Cleaned file saved to:", OUT_PATH)
