"""
Updated Bundesanzeiger module compatible with unternehmensregister.de

This module provides a compatibility layer that uses the new unternehmensregister.de
website while maintaining the old Bundesanzeiger API interface.

The old bundesanzeiger.de website has been replaced by unternehmensregister.de,
which is a modern Next.js/React application. This implementation adapts to the new structure.
"""

import warnings
from deutschland.unternehmensregister import Unternehmensregister as UnternehmensregisterClient
from deutschland.unternehmensregister import Report
from deutschland.config import Config


class BundesanzeigerV2:
    """
    Updated Bundesanzeiger client that works with the new unternehmensregister.de website.

    This class provides backward compatibility with the old Bundesanzeiger API while
    using the new unternehmensregister.de backend.

    Example:
        >>> from deutschland.bundesanzeiger import BundesanzeigerV2
        >>> ba = BundesanzeigerV2()
        >>> reports = ba.get_reports("Deutsche Bahn AG")
    """

    def __init__(self, on_captcha_callback=None, config: Config = None):
        """
        Initialize the BundesanzeigerV2 client.

        Note: The new website doesn't use captchas in the same way as the old one,
        so the on_captcha_callback parameter is deprecated but kept for compatibility.

        :param on_captcha_callback: Deprecated - kept for backward compatibility
        :param config: Optional Config object for proxy settings, etc.
        """
        if on_captcha_callback is not None:
            warnings.warn(
                "The on_captcha_callback parameter is deprecated. "
                "The new unternehmensregister.de website uses a different structure.",
                DeprecationWarning,
                stacklevel=2
            )

        # Use the new Unternehmensregister client under the hood
        self._client = UnternehmensregisterClient(config=config)

    def get_reports(self, company_name: str, *, page_limit: int = 1):
        """
        Fetch all reports for this company name.

        This method maintains compatibility with the old Bundesanzeiger API while
        using the new unternehmensregister.de backend.

        :param company_name: The company name to search for
        :param page_limit: Maximum number of pages to fetch (default: 1).
            Each page typically has 10-20 reports.
            Pass float('inf') to fetch all pages (this might take a while).
        :return: Dict of all reports, keyed by report hash
        """
        warnings.warn(
            "The Bundesanzeiger API now uses unternehmensregister.de. "
            "Consider using deutschland.unternehmensregister.Unternehmensregister directly.",
            FutureWarning,
            stacklevel=2
        )

        return self._client.get_reports(
            company_name,
            page_limit=page_limit,
            fetch_content=False,  # Don't fetch full content by default for compatibility
            areas="all"
        )


# Export the Report class for compatibility
__all__ = ['BundesanzeigerV2', 'Report']
