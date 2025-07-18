import pandas as pd
import numpy as np

# Load your input CSV
csv_path =(r"C:\Users\Maxdesk\Desktop\Webeet\berlin_schools\final\berlin_schools.csv")
df = pd.read_csv(csv_path)

# Map of districts → IDs (with leading zeros)
district_map = {
    "Mitte": "01",
    "Friedrichshain-Kreuzberg": "02",
    "Pankow": "03",
    "Charlottenburg-Wilmersdorf": "04",
    "Spandau": "05",
    "Steglitz-Zehlendorf": "06",
    "Tempelhof-Schöneberg": "07",
    "Neukölln": "08",
    "Treptow-Köpenick": "09",
    "Marzahn-Hellersdorf": "10",
    "Lichtenberg": "11",
    "Reinickendorf": "12"
}

# Add the `district_id` column based on name → ID map
df["district_id"] = df["district"].map(district_map)

# Fill *only* truly empty (blank) fields with np.nan (do NOT touch zeros)
df.replace(r'^\s*$', np.nan, regex=True, inplace=True)

# Drop geometry if present
df.drop(columns=[col for col in df.columns if "geometry" in col.lower()], errors="ignore", inplace=True)

# keep district_id as string for the future 
df["district_id"] = df["district_id"].astype(str).str.zfill(2)

# Save final version
df.to_csv("berlin_schools_did.csv", index=False)
print("✅ Saved with NaN-filled blanks and proper district IDs.")
