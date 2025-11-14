"""
Example usage of the Unternehmensregister API

This example demonstrates how to search for company reports from unternehmensregister.de
"""

from deutschland.unternehmensregister import Unternehmensregister


def main():
    # Initialize the client
    print("Initializing Unternehmensregister client...")
    ur = Unternehmensregister()

    # Search for a company
    company_name = "Porsche"
    print(f"\nSearching for: {company_name}")
    print("-" * 60)

    try:
        # Fetch reports (first page only)
        reports = ur.get_reports(
            company_name,
            page_limit=1,  # Only fetch first page
            fetch_content=False,  # Don't fetch full content for speed
            areas="all"
        )

        print(f"\nFound {len(reports)} reports:\n")

        # Display results
        for i, (report_hash, report) in enumerate(reports.items(), 1):
            print(f"{i}. {report['company']}")
            print(f"   Title: {report['name']}")
            print(f"   Date: {report['date']}")
            if report.get('publication_type'):
                print(f"   Type: {report['publication_type']}")
            print(f"   Hash: {report_hash[:16]}...")
            print()

        if not reports:
            print("No reports found. This may be because:")
            print("1. The company name doesn't exist in the registry")
            print("2. The website structure has changed")
            print("3. The website is temporarily unavailable")

    except Exception as e:
        print(f"\nError occurred: {e}")
        print("\nNote: unternehmensregister.de is a client-side rendered website.")
        print("Some limitations may apply when accessing data programmatically.")


def example_with_backward_compatibility():
    """Example using the Bundesanzeiger compatibility layer"""
    from deutschland.bundesanzeiger import BundesanzeigerV2
    import warnings

    print("\n" + "=" * 60)
    print("Example: Using BundesanzeigerV2 (Backward Compatibility)")
    print("=" * 60)

    # This will emit a deprecation warning
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        ba = BundesanzeigerV2()
        reports = ba.get_reports("Porsche", page_limit=1)

        if w:
            print(f"\nWarning: {w[-1].message}")

    print(f"\nFound {len(reports)} reports using BundesanzeigerV2")


if __name__ == "__main__":
    main()

    # Uncomment to see backward compatibility example
    # example_with_backward_compatibility()
