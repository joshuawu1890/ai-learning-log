# monthly_sales_report.py
# Written by a colleague last year. It works, but nobody documented it.
# Your job this week: read it, run it, and explain what every part does.

import csv
import sys
from datetime import datetime
from collections import defaultdict

INPUT_FILE = "transactions.csv"
SUMMARY_FILE = "monthly_summary.csv"
REPORT_FILE = "summary_report.txt"
TARGET_MONTH = "2026-10"   # hard-coded: change this to report another month

rows = []
skipped = 0

# --- 1. read the file -------------------------------------------------------
try:
    f = open(INPUT_FILE, newline="", encoding="utf-8")
except FileNotFoundError:
    print("ERROR: cannot find " + INPUT_FILE)
    sys.exit(1)

reader = csv.DictReader(f)
for line in reader:
    # skip rows with missing values
    if line["date"] == "" or line["units"] == "" or line["unit_price"] == "":
        skipped = skipped + 1
        continue
    # keep only the target month
    if not line["date"].startswith(TARGET_MONTH):
        continue
    try:
        units = int(line["units"])
        price = float(line["unit_price"])
    except ValueError:
        skipped = skipped + 1
        continue
    line["units"] = units
    line["unit_price"] = price
    line["amount"] = round(units * price, 2)
    rows.append(line)
f.close()

print("rows loaded:", len(rows), "| rows skipped:", skipped)

if len(rows) == 0:
    print("No data for month " + TARGET_MONTH + ". Nothing to do.")
    sys.exit(0)

# --- 2. totals --------------------------------------------------------------
total_amount = 0.0
total_units = 0
for r in rows:
    total_amount = total_amount + r["amount"]
    total_units = total_units + r["units"]
total_amount = round(total_amount, 2)
avg_order = round(total_amount / len(rows), 2)

# --- 3. group by category ---------------------------------------------------
by_category = defaultdict(float)
for r in rows:
    by_category[r["category"]] = by_category[r["category"]] + r["amount"]
for k in by_category:
    by_category[k] = round(by_category[k], 2)

# --- 4. group by region -----------------------------------------------------
by_region = defaultdict(float)
for r in rows:
    by_region[r["region"]] = by_region[r["region"]] + r["amount"]
for k in by_region:
    by_region[k] = round(by_region[k], 2)

# --- 5. top 3 products by amount -------------------------------------------
product_totals = defaultdict(float)
for r in rows:
    product_totals[r["product"]] = product_totals[r["product"]] + r["amount"]
sorted_products = sorted(product_totals.items(), key=lambda x: x[1], reverse=True)
top3 = sorted_products[:3]

# --- 6. best single day ------------------------------------------------------
by_day = defaultdict(float)
for r in rows:
    by_day[r["date"]] = by_day[r["date"]] + r["amount"]
best_day = None
best_day_amount = -1
for day in by_day:
    if by_day[day] > best_day_amount:
        best_day_amount = by_day[day]
        best_day = day

# --- 7. write monthly_summary.csv -------------------------------------------
out = open(SUMMARY_FILE, "w", newline="", encoding="utf-8")
writer = csv.writer(out)
writer.writerow(["group_type", "group_name", "total_amount"])
for name, amt in sorted(by_category.items()):
    writer.writerow(["category", name, amt])
for name, amt in sorted(by_region.items()):
    writer.writerow(["region", name, amt])
out.close()

# --- 8. write summary_report.txt --------------------------------------------
now = datetime.now().strftime("%Y-%m-%d %H:%M")
rep = open(REPORT_FILE, "w", encoding="utf-8")
rep.write("Monthly Sales Report - " + TARGET_MONTH + "\n")
rep.write("Generated: " + now + "\n")
rep.write("-" * 45 + "\n")
rep.write("Orders:        " + str(len(rows)) + "\n")
rep.write("Units sold:    " + str(total_units) + "\n")
rep.write("Total amount:  $" + str(total_amount) + "\n")
rep.write("Average order: $" + str(avg_order) + "\n")
rep.write("Best day:      " + str(best_day) + " ($" + str(round(best_day_amount, 2)) + ")\n")
rep.write("\nBy category:\n")
for name, amt in sorted(by_category.items()):
    rep.write("  " + name + ": $" + str(amt) + "\n")
rep.write("\nBy region:\n")
for name, amt in sorted(by_region.items()):
    rep.write("  " + name + ": $" + str(amt) + "\n")
rep.write("\nTop 3 products:\n")
for i in range(len(top3)):
    rep.write("  " + str(i + 1) + ". " + top3[i][0] + " - $" + str(round(top3[i][1], 2)) + "\n")
rep.close()

print("Done. Wrote " + SUMMARY_FILE + " and " + REPORT_FILE)
