import pandas as pd
import glob
from pathlib import Path

def process_soul_foods_data(data_dir="data", output_filename="formatted_pink_morsel_sales.csv"):
    """
    Combines sales data from multiple CSV files, filters for "Pink Morsel",
    calculates sales, and outputs a cleaned CSV with Sales, Date, and Region.

    Args:
        data_dir (str): The directory containing the input CSV files.
        output_filename (str): The name for the final output CSV file.
    """
    # --- 1. Locate and Load Data ---
    search_pattern = Path(data_dir) / "daily_sales_data_*.csv"
    csv_files = sorted(glob.glob(str(search_pattern))) # glob returns a list of strings

    if not csv_files:
        print(f"No CSV files found in '{data_dir}' matching 'daily_sales_data_*.csv'")
        return None

    print(f"Found files: {csv_files}")

    all_dataframes = []
    for file_path in csv_files:
        try:
            print(f"Reading {file_path}...")
            df = pd.read_csv(file_path)
            all_dataframes.append(df)
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    if not all_dataframes:
        print("No dataframes were loaded. Exiting.")
        return None

    # Concatenate all dataframes into one
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    print(f"\nSuccessfully combined {len(csv_files)} files. Total rows: {len(combined_df)}")

    # --- 2. Filter for "Pink Morsel" products ---
    # Make a copy to avoid SettingWithCopyWarning if you do further chained assignments
    pink_morsels_df = combined_df[combined_df['product'].str.lower() == 'pink morsel'].copy()
    print(f"Rows after filtering for 'pink morsel': {len(pink_morsels_df)}")

    if pink_morsels_df.empty:
        print("No 'pink morsel' products found. Exiting.")
        return None

    # --- 3. Data Type Conversion and Cleaning ---
    # Clean 'price' column: remove '$' and convert to float
    # Use .loc to ensure modifications are made on the DataFrame itself
    print("Cleaning 'price' column...")
    pink_morsels_df.loc[:, 'price'] = pink_morsels_df['price'].replace({'\$': ''}, regex=True).astype(float)

    # Ensure 'quantity' is numeric
    print("Ensuring 'quantity' column is numeric...")
    pink_morsels_df.loc[:, 'quantity'] = pd.to_numeric(pink_morsels_df['quantity'], errors='coerce')

    # Convert 'date' column to datetime objects
    print("Converting 'date' column to datetime objects...")
    pink_morsels_df.loc[:, 'date'] = pd.to_datetime(pink_morsels_df['date'])

    # --- 4. Calculate "sales" field ---
    print("Calculating 'sales' field (price * quantity)...")
    pink_morsels_df.loc[:, 'sales'] = pink_morsels_df['price'] * pink_morsels_df['quantity']

    # --- 5. Select and Rename Final Columns ---
    # The requirement is "Sales", "Date", "Region" for the output file.
    # We'll select the 'date' and 'region' columns as they are, and the newly created 'sales'.
    # Pandas will use these names as headers in the CSV.
    final_df = pink_morsels_df[['sales', 'date', 'region']].copy()

    # If specific capitalization is needed for output columns different from DataFrame columns:
    # final_df = final_df.rename(columns={'sales': 'Sales', 'date': 'Date', 'region': 'Region'})
    # However, the prompt implies the field names are what matter. Let's match case for clarity.
    final_df.rename(columns={'sales': 'Sales', 'date': 'Date', 'region': 'Region'}, inplace=True)

    print(f"\nFinal DataFrame for output has {len(final_df)} rows.")
    print("First 5 rows of the final data:")
    print(final_df.head())

    # --- 6. Save the Output ---
    # Create an output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_filename

    try:
        final_df.to_csv(output_path, index=False)
        print(f"\nSuccessfully saved formatted data to: {output_path}")
    except Exception as e:
        print(f"Error saving data to {output_path}: {e}")

    return final_df

# --- Main execution block ---
if __name__ == "__main__":
    print("Starting Soul Foods data processing...")
    # Assuming your CSVs are in a 'data' subdirectory relative to this script
    processed_data = process_soul_foods_data(data_dir="data", output_filename="soul_foods_pink_morsel_sales.csv")

    if processed_data is not None:
        print("\nData processing complete.")
    else:
        print("\nData processing failed or produced no output.")