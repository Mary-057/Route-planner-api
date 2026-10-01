import pandas as pd
fuel_csv_name = "fuel-prices-for-be-assessment.csv"


fuel_df = pd.read_csv(fuel_csv_name)
cities_df = pd.read_csv("uscities.csv")

cities_df = cities_df[["city", "state_id", "lat", "lng"]]

fuel_df["City_clean"] = fuel_df["City"].astype(str).str.strip().str.title()
fuel_df["State_clean"] = fuel_df["State"].astype(str).str.strip().str.upper()

cities_df["city_clean"] = cities_df["city"].astype(str).str.strip().str.title()
cities_df["state_clean"] = cities_df["state_id"].astype(str).str.strip().str.upper()


merged_df = pd.merge(
    fuel_df,
    cities_df,
    left_on=["City_clean", "State_clean"],
    right_on=["city_clean", "state_clean"],
    how="left",
)

merged_df = merged_df.drop(
    columns=["City_clean", "State_clean", "city_clean", "state_clean", "city", "state_id"]
)
merged_df.to_csv("stations_with_coords.csv", index=False)

print(f"Generated stations_with_coords.csv successfully! Total rows: {len(merged_df)}")
print(f"Rows with matched coordinates: {merged_df['lat'].notna().sum()}")