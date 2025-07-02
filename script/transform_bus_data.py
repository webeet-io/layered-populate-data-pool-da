
import pandas as pd

def transform_bus_data_subset(input_path, output_path):
    df = pd.read_csv(input_path)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    df.drop_duplicates(inplace=True)
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df.to_csv(output_path, index=False)

if __name__ == "__main__":
    transform_bus_data_subset("public_bus_data_cleaned.csv", "transformed_bus_data_subset.csv")
