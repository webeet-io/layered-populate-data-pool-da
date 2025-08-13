# Berlin Urban Analytics Project

## Project Structure
```
.
├── segmentation/          # Neighborhood analysis modules
│   ├── crime_statistics/  # Crime pattern analysis
│   ├── green_spaces/      # Green space analysis
│   ├── land_prices/       # Real estate market analysis
│   ├── playgrounds/       # Recreational space analysis
│   ├── regional_statistics/ # Regional demographic analysis
│   ├── rent_stats/        # Rental market analysis
│   ├── short_time_listings/ # Short-term rental analysis
│   ├── ubahn/            # Public transport analysis
│   ├── README.md          # Architecture documentation
│   └── orchestrator.py    # Coordination logic

├── README.md              # This file
└── requirements.txt       # Dependencies
```

## Key Features
- Modular neighborhood segmentation
- Both rule-based and ML approaches
- Comprehensive documentation with schemas
- Standardized interfaces and SQL queries
- Unit and integration test coverage

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Configure database connection
3. Run analyses through orchestrator

```python
from segmentation.orchestrator import analyze_all

results = analyze_all(engine)
```

## Documentation
See individual module READMEs and schema.md files for implementation details.