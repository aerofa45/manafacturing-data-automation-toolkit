# Manufacturing Data Automation Toolkit

Manufacturing teams often collect shift data in separate spreadsheets, operator logs, and manual trackers. That makes reporting slower, increases the chance of formula errors, and makes it harder to see scrap, downtime, and line performance in one place. This project is a small operations toolkit built to solve that problem.

The repository combines Python, SQL, and Excel VBA to show how fragmented production data can be cleaned, standardized, and consolidated into one reporting structure that is easier to review in Excel, Power BI, or a database-backed dashboard.

## What this project does

This toolkit simulates a simple manufacturing reporting workflow:

- reads raw production data from CSV files
- validates required fields and cleans data types
- calculates core shop-floor KPIs
- flags downtime severity for quick review
- loads the final dataset into SQLite for reporting
- includes an Excel VBA macro for weekly tracker consolidation

## KPIs included

The Python pipeline calculates metrics that are commonly useful in manufacturing reporting:

- Quality Yield
- Scrap Rate
- Run Time
- Availability
- Performance
- Estimated OEE

The OEE logic here is designed as a practical demonstration for a portfolio project. In a real plant environment, the exact formula would be aligned with machine definitions, ideal cycle assumptions, and line-specific standards.

## Repository structure

- `README.md` — project overview, setup, and usage
- `production_integrator.py` — Python ETL script for production data consolidation
- `vba_tracker_consolidation.bas` — Excel VBA macro to combine shift tabs into a weekly summary
- `mock_production_data.csv` — sample manufacturing dataset for testing
- `requirements.txt` — Python dependencies
- `.gitignore` — recommended ignores for local database and cache files

## Sample input fields

The included mock dataset uses the following columns:

- `Timestamp`
- `Shift`
- `Machine_ID`
- `Product_Code`
- `Total_Produced`
- `Good_Units`
- `Scrap_Count`
- `Downtime_Minutes`
- `Planned_Production_Minutes`
- `Ideal_Run_Rate_Per_Min`

## How to run

Create and activate a virtual environment, then install dependencies:

```bash
pip install -r requirements.txt
```

Run the ETL pipeline:

```bash
python production_integrator.py --input mock_production_data.csv --database factory_ops.db
```

## Output

The script creates or updates a SQLite database named `factory_ops.db` and loads the processed records into a table called `master_production`.

It also prints a short process summary to the terminal so you can quickly verify row counts, machine counts, and average KPIs.

## Why this project is relevant

This project is useful for roles involving manufacturing operations, production reporting, process improvement, supply chain support, industrial analytics, or continuous improvement. It demonstrates:

- Python data cleaning with pandas
- SQL database loading with sqlite3
- KPI logic for production environments
- Excel macro automation
- reporting-oriented thinking instead of just raw coding

## Possible next improvements

A stronger second version of this project could include:

- multiple input files from separate shifts or lines
- Power BI dashboard connection
- Excel export for supervisors
- scrap reason categorization
- downtime Pareto reporting
- automated exception report for low-yield or high-downtime runs


