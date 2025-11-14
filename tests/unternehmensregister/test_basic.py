"""
Basic tests for the Unternehmensregister module.

Note: Since unternehmensregister.de is a client-side rendered React app,
these tests verify that the API client can handle various scenarios.
"""
import pytest
from deutschland.unternehmensregister import Unternehmensregister, Report


def test_import():
    """Test that the module can be imported"""
    from deutschland import unternehmensregister
    assert hasattr(unternehmensregister, 'Unternehmensregister')
    assert hasattr(unternehmensregister, 'Report')


def test_report_creation():
    """Test Report object creation"""
    from datetime import datetime

    report = Report(
        date=datetime.now(),
        name="Test Report",
        content_url="https://example.com/report",
        company="Test Company GmbH",
        report="Test content",
        publication_type="Jahresabschluss"
    )

    assert report.company == "Test Company GmbH"
    assert report.name == "Test Report"
    assert report.publication_type == "Jahresabschluss"


def test_report_to_dict():
    """Test Report serialization"""
    from datetime import datetime

    date = datetime(2024, 1, 1)
    report = Report(
        date=date,
        name="Test Report",
        content_url="https://example.com/report",
        company="Test Company GmbH"
    )

    report_dict = report.to_dict()
    assert isinstance(report_dict, dict)
    assert report_dict["company"] == "Test Company GmbH"
    assert report_dict["name"] == "Test Report"
    assert report_dict["date"] == date


def test_report_hash():
    """Test Report hash generation"""
    from datetime import datetime

    date = datetime(2024, 1, 1)
    report1 = Report(
        date=date,
        name="Test Report",
        content_url="https://example.com/report",
        company="Test Company GmbH"
    )

    report2 = Report(
        date=date,
        name="Test Report",
        content_url="https://example.com/different",  # Different URL
        company="Test Company GmbH"
    )

    # Same data should produce same hash (URL not included in hash)
    hash1 = report1.to_hash()
    hash2 = report2.to_hash()

    assert isinstance(hash1, str)
    assert len(hash1) == 32  # MD5 hash length
    assert hash1 == hash2  # Content URL not part of hash


def test_unternehmensregister_init():
    """Test Unternehmensregister initialization"""
    ur = Unternehmensregister()
    assert ur.session is not None
    assert ur.BASE_URL == "https://www.unternehmensregister.de"


@pytest.mark.skip(reason="Integration test - requires network access and may be flaky")
def test_search_company():
    """
    Integration test - searches for a real company.
    Skipped by default as it requires network access.
    """
    ur = Unternehmensregister()
    reports = ur.get_reports("Deutsche Bahn AG", page_limit=1)

    # The test passes if we can make the request without errors
    # We can't assert specific results as the data may change
    assert isinstance(reports, dict)
