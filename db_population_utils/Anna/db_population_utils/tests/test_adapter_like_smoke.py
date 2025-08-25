import pandas as pd
from db_population_utils import DataProcessor, GeoBounds

def test_delegators_smoke_paths():
    df = pd.DataFrame({"plz": ["10115","99999"], "lat": [52.5,60.0], "lng": [13.4,13.4], "scraped": ["N/A",""]})
    dp = DataProcessor(verbose=False)

    # webscraping delegator
    out_ws = dp.clean_webscraping_artifacts(df, custom_null_values=[""])
    assert out_ws["scraped"].isna().any()

    # geo delegator (nur report)
    b = GeoBounds(lat_min=52.3, lat_max=52.7, lng_min=13.0, lng_max=13.8)
    rep = dp.validate_berlin_data(df, action="mark", berlin_only_plz=True, bounds=b)
    assert isinstance(rep, dict)

    # ml-prep delegator
    out_ml, info_ml = dp.prepare_for_ml(df, strategy="minimal", null_strategy="preserve")
    assert isinstance(out_ml, pd.DataFrame) and "strategy_info" in info_ml
