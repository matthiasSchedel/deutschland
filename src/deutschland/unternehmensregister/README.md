# Unternehmensregister API

This module provides access to German company registry data from [unternehmensregister.de](https://www.unternehmensregister.de).

## Background

The German company registry system has been updated. The old bundesanzeiger.de website has been replaced by unternehmensregister.de, which is a modern Next.js/React application.

This module provides programmatic access to the new website, maintaining compatibility with the old Bundesanzeiger API where possible.

## Installation

```bash
pip install deutschland
```

## Usage

### Basic Usage

```python
from deutschland.unternehmensregister import Unternehmensregister

# Initialize the client
ur = Unternehmensregister()

# Search for company reports
reports = ur.get_reports("Deutsche Bahn AG")

# Iterate through results
for report_hash, report in reports.items():
    print(f"{report['company']}: {report['name']}")
    print(f"Date: {report['date']}")
    print(f"Type: {report['publication_type']}")
    print("---")
```

### Advanced Usage

```python
from deutschland.unternehmensregister import Unternehmensregister

ur = Unternehmensregister()

# Search with pagination
reports = ur.get_reports(
    "Porsche",
    page_limit=3,  # Fetch up to 3 pages
    fetch_content=True,  # Fetch full report content (slower)
    areas="all"  # Search all areas
)

print(f"Found {len(reports)} reports")
```

### Using the Bundesanzeiger Compatibility Layer

For backward compatibility with existing code using the old Bundesanzeiger API:

```python
from deutschland.bundesanzeiger import BundesanzeigerV2

# Drop-in replacement for old Bundesanzeiger API
ba = BundesanzeigerV2()
reports = ba.get_reports("Deutsche Bahn AG")
```

**Note:** The BundesanzeigerV2 class is a compatibility wrapper that uses the new unternehmensregister.de backend. It will emit deprecation warnings.

## Parameters

### `get_reports(company_name, *, page_limit=1, fetch_content=False, areas="all")`

- **company_name** (str): The company name to search for
- **page_limit** (int, optional): Maximum number of pages to fetch (default: 1)
  - Each page typically contains 10-20 reports
  - Pass `float('inf')` to fetch all pages (may be slow)
- **fetch_content** (bool, optional): Whether to fetch full report content (default: False)
  - When `True`, makes additional requests to fetch complete report text
  - Significantly slower but provides full report data
- **areas** (str, optional): Search areas (default: "all")
  - Options: "all", "Bekanntmachungen", "Jahresabschluss", etc.

**Returns:** Dictionary of reports, keyed by MD5 hash

## Report Structure

Each report is a dictionary with the following fields:

```python
{
    "date": datetime,  # Publication date
    "name": str,  # Report title
    "company": str,  # Company name
    "report": str,  # Full report text (if fetch_content=True)
    "raw_report": str,  # Raw HTML (if fetch_content=True)
    "publication_type": str  # Type of publication
}
```

## Important Notes

1. **No Official API**: unternehmensregister.de does not provide an official API. This module uses web scraping techniques.

2. **Rate Limiting**: Be respectful of the server. The module includes built-in delays between requests.

3. **Structure Changes**: Since the website is client-side rendered with React, the structure may change. Please report issues on GitHub.

4. **Captchas**: The new website structure doesn't use captchas in the same way as the old one.

## Migration from Bundesanzeiger

If you're migrating from the old `Bundesanzeiger` class:

```python
# Old code
from deutschland.bundesanzeiger import Bundesanzeiger
ba = Bundesanzeiger()
reports = ba.get_reports("Company Name")

# New code - Option 1: Use compatibility layer
from deutschland.bundesanzeiger import BundesanzeigerV2
ba = BundesanzeigerV2()
reports = ba.get_reports("Company Name")

# New code - Option 2: Use new API directly (recommended)
from deutschland.unternehmensregister import Unternehmensregister
ur = Unternehmensregister()
reports = ur.get_reports("Company Name")
```

## Limitations

- The module relies on web scraping, which may break if the website structure changes
- Some advanced features of the website may not be accessible through this API
- Performance may be slower compared to a native API

## Contributing

If you find issues or the website structure has changed, please:
1. Report the issue on GitHub
2. Include the company name and error message
3. If possible, include a screenshot of the website

## License

Apache 2.0
