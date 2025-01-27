# Minecraft Resource Top List

A tool for aggregating and analyzing popular Minecraft resources from various platforms.

## Project Structure

```
mc-top-list/
├── scraper/                   # Main package
│   ├── scraper.py            # Core implementation and entry point
│   ├── platforms/            # Platform-specific implementations
│   ├── contracts/            # Interface definitions
│   ├── models/               # Data models
│   └── utils/                # Utility functions
├── data/                     # Data storage
│   ├── raw/                  # Raw data from platforms
│   ├── normalized/           # Standardized data
│   └── aggregated/          # Combined data from all platforms
├── docs/                     # Documentation
└── tests/                    # Test suite
```

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd mc-top-list
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   cd scraper
   pip install -r requirements.txt
   ```

4. Configure API keys:
   - Create `scraper/config/api_config.yml` with the following structure:
     ```yaml
     hangar:
       api_key: "your_hangar_api_key"  # From https://hangar.papermc.io/account/apiKeys
     modrinth:
       api_key: "your_modrinth_api_key"  # From https://modrinth.com/settings/account
     ```

## Usage

To scrape resources from all supported platforms:

1. Ensure you're in the project root directory:
   ```bash
   cd /path/to/mc-top-list
   ```

2. Activate the virtual environment (if not already activated):
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Run the scraper:
   ```bash
   python -m scraper.scraper
   ```

This will:
1. Connect to supported platforms (Hangar, Modrinth)
2. Fetch new and popular resources
3. Transform data into a standardized format
4. Save both raw and processed data
5. Generate an aggregated view

### Output Files

After running the scraper, you can find the following data files:
- Raw data: `scraper/data/raw/`
  - `hangar.json`: Raw data from Hangar
  - `modrinth.json`: Raw data from Modrinth
- Normalized data: `scraper/data/normalized/`
  - Platform-specific normalized data
- Aggregated data: `scraper/data/aggregated/`
  - Combined data from all platforms

## Development

The project follows a modular design:
- Each platform has its own client implementation
- Data transformers standardize platform-specific data
- JSON schemas validate data structure
- Logging provides detailed execution information
