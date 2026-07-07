"""
ApexPlanet Data Analytics Internship — Task 2
Exploratory Data Analysis (EDA) & Business Intelligence

Reads the Task 1 cleaned dataset and produces:
  - Descriptive statistics (numerical + categorical)
  - Univariate visualizations (histograms, bar charts)
  - Multivariate visualizations (scatter, correlation heatmap, pair plot)
All charts are saved as PNGs into ./charts/ for reuse in the report/dashboard.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_style("whitegrid")
plt.rcParams["font.family"] = "DejaVu Sans"
os.makedirs("charts", exist_ok=True)

PALETTE = ["#1F4E78", "#2E86AB", "#4FA3C7", "#8FC1DA", "#F2A65A", "#C0392B"]

df = pd.read_excel("ApexPlanet_Cleaned_Dataset.xlsx")

# ---------------------------------------------------------------------------
# 1. DESCRIPTIVE STATISTICS
# ---------------------------------------------------------------------------
numerical_cols = ["Age", "Quantity", "Unit_Price", "Total_Sales", "Revenue_Per_Unit"]
categorical_cols = ["Gender", "City", "Product", "Category", "Age_Group", "Price_Tier"]

num_summary = df[numerical_cols].describe().T
num_summary["skew"] = df[numerical_cols].skew()
num_summary["missing"] = df[numerical_cols].isnull().sum()
num_summary.to_csv("charts/numerical_summary.csv")
print("=== NUMERICAL SUMMARY ===")
print(num_summary.round(2))

cat_summary_rows = []
for col in categorical_cols:
    vc = df[col].value_counts()
    top = vc.index[0]
    top_pct = round(100 * vc.iloc[0] / len(df), 1)
    cat_summary_rows.append([col, df[col].nunique(), top, f"{top_pct}%"])
cat_summary = pd.DataFrame(cat_summary_rows, columns=["Column", "Unique_Values", "Most_Common", "Most_Common_Share"])
cat_summary.to_csv("charts/categorical_summary.csv", index=False)
print("\n=== CATEGORICAL SUMMARY ===")
print(cat_summary)

# ---------------------------------------------------------------------------
# 2. UNIVARIATE VISUALIZATIONS
# ---------------------------------------------------------------------------
# Histograms for numerical fields
fig, axes = plt.subplots(2, 2, figsize=(11, 8))
for ax, col in zip(axes.flat, ["Age", "Quantity", "Unit_Price", "Total_Sales"]):
    sns.histplot(df[col], bins=20, color=PALETTE[0], kde=True, ax=ax)
    ax.set_title(f"Distribution of {col}", fontweight="bold")
plt.tight_layout()
plt.savefig("charts/01_histograms_numerical.png", dpi=150)
plt.close()

# Bar charts for categorical fields
fig, axes = plt.subplots(2, 2, figsize=(12, 9))
cat_plot_cols = ["Category", "City", "Gender", "Age_Group"]
for ax, col in zip(axes.flat, cat_plot_cols):
    order = df[col].value_counts().index
    sns.countplot(data=df, y=col, order=order, palette=PALETTE, ax=ax, hue=col, legend=False)
    ax.set_title(f"Order Count by {col}", fontweight="bold")
    ax.set_xlabel("Number of Orders")
plt.tight_layout()
plt.savefig("charts/02_barcharts_categorical.png", dpi=150)
plt.close()

# Revenue by Category / Product (business-relevant univariate view)
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
cat_rev = df.groupby("Category")["Total_Sales"].sum().sort_values(ascending=False)
sns.barplot(x=cat_rev.values, y=cat_rev.index, hue=cat_rev.index, palette=PALETTE, ax=axes[0], legend=False)
axes[0].set_title("Total Revenue by Category", fontweight="bold")
axes[0].set_xlabel("Total Sales (INR)")

prod_rev = df.groupby("Product")["Total_Sales"].sum().sort_values(ascending=False)
sns.barplot(x=prod_rev.values, y=prod_rev.index, hue=prod_rev.index, palette=PALETTE, ax=axes[1], legend=False)
axes[1].set_title("Total Revenue by Product", fontweight="bold")
axes[1].set_xlabel("Total Sales (INR)")
plt.tight_layout()
plt.savefig("charts/03_revenue_by_category_product.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 3. MULTIVARIATE ANALYSIS
# ---------------------------------------------------------------------------
# Correlation heatmap
corr_cols = ["Age", "Quantity", "Unit_Price", "Total_Sales", "Revenue_Per_Unit"]
corr = df[corr_cols].corr()
plt.figure(figsize=(7, 6))
sns.heatmap(corr, annot=True, cmap="RdBu_r", center=0, fmt=".2f", square=True, linewidths=0.5)
plt.title("Correlation Heatmap — Numerical Variables", fontweight="bold")
plt.tight_layout()
plt.savefig("charts/04_correlation_heatmap.png", dpi=150)
plt.close()

# Scatter: Age vs Total_Sales, colored by Category
plt.figure(figsize=(9, 6))
sns.scatterplot(data=df, x="Age", y="Total_Sales", hue="Category", palette=PALETTE, alpha=0.7)
plt.title("Age vs Total Sales by Category", fontweight="bold")
plt.tight_layout()
plt.savefig("charts/05_scatter_age_vs_sales.png", dpi=150)
plt.close()

# Scatter: Unit_Price vs Quantity
plt.figure(figsize=(9, 6))
sns.scatterplot(data=df, x="Unit_Price", y="Quantity", hue="Category", palette=PALETTE, alpha=0.7)
plt.title("Unit Price vs Quantity Purchased", fontweight="bold")
plt.tight_layout()
plt.savefig("charts/06_scatter_price_vs_quantity.png", dpi=150)
plt.close()

# Age distribution by product category (box plot) — "age vs product category"
plt.figure(figsize=(10, 6))
order = df.groupby("Category")["Age"].median().sort_values().index
sns.boxplot(data=df, x="Category", y="Age", order=order, hue="Category", palette=PALETTE, legend=False)
plt.title("Age Distribution by Product Category", fontweight="bold")
plt.tight_layout()
plt.savefig("charts/07_boxplot_age_by_category.png", dpi=150)
plt.close()

# Pair plot across key numerical variables
pp = sns.pairplot(df[["Age", "Quantity", "Unit_Price", "Total_Sales", "Category"]],
                   hue="Category", palette=PALETTE, plot_kws={"alpha": 0.6, "s": 25})
pp.fig.suptitle("Pair Plot — Age, Quantity, Unit Price, Total Sales", y=1.02, fontweight="bold")
pp.savefig("charts/08_pairplot.png", dpi=150)
plt.close()

# Monthly revenue trend (time-based multivariate view)
monthly = df.groupby(["Order_Year", "Order_Month"])["Total_Sales"].sum().reset_index()
monthly["Period"] = monthly["Order_Year"].astype(str) + "-" + monthly["Order_Month"].astype(str).str.zfill(2)
plt.figure(figsize=(12, 5))
sns.lineplot(data=monthly, x="Period", y="Total_Sales", marker="o", color=PALETTE[0])
plt.title("Monthly Revenue Trend", fontweight="bold")
plt.xticks(rotation=45)
plt.ylabel("Total Sales (INR)")
plt.tight_layout()
plt.savefig("charts/09_monthly_revenue_trend.png", dpi=150)
plt.close()

print("\nAll charts saved to ./charts/")
