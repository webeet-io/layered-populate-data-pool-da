# Green Spaces Segmentation Module

## 🌳 Green Space Labels
### 🔍 Label Categories
The module generates the following tags for neighborhoods based on their green spaces:

- **Maintenance Quality**:
  - `*well_maintained`: Above median maintenance score
  - `*needs_attention`: Below 70% of median maintenance score

- **Park Size**:
  - `*large_park`: Above median average park size

- **Space Availability**:
  - `*spacious`: Above median green space per capita
  - `*crowded`: Below 50% of median green space per capita

- **Quantity**:
  - `*many_parks`: Above median number of green spaces

## 🛠 Implementation Details
### Data Processing
1. Pulls from `test_berlin_data.green_spaces` joined with regional statistics
2. Calculates key metrics:
   - Number of green spaces per neighborhood
   - Total and average green area
   - Years since last renovation
   - Green space per capita (using population data)

### Segmentation Approaches
#### Machine Learning (KMeans)
- Clusters neighborhoods based on:
  - Green space per capita
  - Maintenance score
  - Average park size
  - Number of green spaces
- Generates dynamic tags based on feature comparisons to global medians

#### Rule-Based
- Uses fixed thresholds based on median values
- Applies same tag categories as ML approach but with simpler rules

## 📊 Usage
```python
# For ML-based segmentation
from segmentation.green_spaces.ml_segmenter import GreenSpacesMLSegmenter
ml_segmenter = GreenSpacesMLSegmenter(n_clusters=3)
ml_tags = ml_segmenter.segment(features_df)

# For rule-based segmentation  
from segmentation.green_spaces.rule_based_segmenter import GreenSpacesRuleBasedSegmenter
rule_segmenter = GreenSpacesRuleBasedSegmenter()
rule_tags = rule_segmenter.segment(features_df)
```

## ⚠️ Edge Cases
- Handles neighborhoods with no green spaces (returns empty tags)
- Adjusts for varying population sizes in per-capita calculations
- Uses COALESCE to avoid division by zero in population calculations