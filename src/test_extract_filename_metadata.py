"""
test_extract_filename_metadata.py — unit tests for the H-004 filename parser.

Covers DOW / DOS / NASA happy paths, observed edge cases (year-only dates,
day-precision dates, the literal-"NA" date sentinel, the "Correspondance"
spelling variant), and negative cases for filenames that should never match
(FBI, DOD videos, plain garbage).

Run from project root:
    python src/test_extract_filename_metadata.py
"""
from __future__ import annotations

import unittest

from extract_filename_metadata import (
    parse_dow,
    parse_dos,
    parse_filename,
    parse_nasa,
)


class TestDOW(unittest.TestCase):
    def test_dow_mission_report_month_year(self):
        result = parse_dow("DOW-UAP-D65-Mission-Report-Persian-Gulf-July-2020.pdf")
        self.assertEqual(
            result,
            {
                "agency": "DOW",
                "country": "Persian-Gulf",
                "date": "2020-07-01",
                "date_precision": "month",
                "item_type": "Mission-Report",
            },
        )

    def test_dow_mission_report_multiword_location(self):
        result = parse_dow(
            "DOW-UAP-D23-Mission-Report-United-Arab-Emirates-October-2023.pdf"
        )
        self.assertEqual(result["country"], "United-Arab-Emirates")
        self.assertEqual(result["date"], "2023-10-01")
        self.assertEqual(result["date_precision"], "month")
        self.assertEqual(result["item_type"], "Mission-Report")

    def test_dow_mission_report_gulf_of_aden(self):
        # Location with internal "of" — confirms greedy stripping doesn't over-eat
        result = parse_dow(
            "DOW-UAP-D75-Mission-Report-Gulf-of-Aden-July-2024.pdf"
        )
        self.assertEqual(result["country"], "Gulf-of-Aden")
        self.assertEqual(result["date"], "2024-07-01")


class TestDOWEdgeCases(unittest.TestCase):
    def test_dow_year_only_precision(self):
        # No month in filename — date_precision must be "year", not "month"
        result = parse_dow("DOW-UAP-D8-Mission-Report-Djibouti-2025.pdf")
        self.assertEqual(result["country"], "Djibouti")
        self.assertEqual(result["date"], "2025-01-01")
        self.assertEqual(result["date_precision"], "year")

    def test_dow_day_precision(self):
        result = parse_dow(
            "DOW-UAP-D19-Mission-Report-Syria-February-21-2023.pdf"
        )
        self.assertEqual(result["country"], "Syria")
        self.assertEqual(result["date"], "2023-02-21")
        self.assertEqual(result["date_precision"], "day")

    def test_dow_na_date_sentinel(self):
        # Filename ends with literal "NA" — date should be blank, not 2025-01-01
        result = parse_dow(
            "DOW-UAP-D54-Mission-Report-Mediterranean-Sea-NA.pdf"
        )
        self.assertEqual(result["country"], "Mediterranean-Sea")
        self.assertEqual(result["date"], "")
        self.assertEqual(result["date_precision"], "")
        self.assertEqual(result["item_type"], "Mission-Report")

    def test_dow_email_correspondance_typo_variant(self):
        # D52 uses "Correspondance" not "Correspondence" — must still parse
        result = parse_dow(
            "DOW-UAP-D52-Email-Correspondance-NA-August-2024.pdf"
        )
        self.assertEqual(result["item_type"], "Email-Correspondance")
        self.assertEqual(result["country"], "NA")
        self.assertEqual(result["date"], "2024-08-01")

    def test_dow_range_fouler_debrief_prefix_precedence(self):
        # "Range-Fouler-Debrief" must win over "Range-Fouler" (longer-first)
        result = parse_dow(
            "DOW-UAP-D38-Range-Fouler-Debrief-Middle-East-May-2020.pdf"
        )
        self.assertEqual(result["item_type"], "Range-Fouler-Debrief")
        self.assertEqual(result["country"], "Middle-East")

    def test_dow_comma_artifact(self):
        # D32 has "Mission-Report,-Syria" with a literal comma — observed
        # in the source release; the parser must tolerate it.
        result = parse_dow(
            "DOW-UAP-D32-Mission-Report,-Syria-October-2024.pdf"
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["item_type"], "Mission-Report")
        self.assertEqual(result["country"], "Syria")
        self.assertEqual(result["date"], "2024-10-01")

    def test_dow_range_fouler_no_debrief(self):
        # D44 has Range-Fouler without Debrief — must not absorb location
        result = parse_dow(
            "DOW-UAP-D44-Range-Fouler-Arabian-Sea-October-2020.pdf"
        )
        self.assertEqual(result["item_type"], "Range-Fouler")
        self.assertEqual(result["country"], "Arabian-Sea")

    def test_dow_launch_summary_blank_country(self):
        # H-004a: source filename has no location between item_type and
        # date. Parser yields blank country rather than failing the parse;
        # date and item_type are still extracted.
        result = parse_dow("DOW-UAP-D49-Launch-Summary-February-2000.pdf")
        self.assertEqual(
            result,
            {
                "agency": "DOW",
                "country": "",
                "date": "2000-02-01",
                "date_precision": "month",
                "item_type": "Launch-Summary",
            },
        )

    def test_dow_bare_report_blank_country(self):
        # H-004a: same shape as Launch-Summary above; "Report" is a known
        # item_type and "September-1996" parses as a month/year date.
        result = parse_dow("DOW-UAP-D48-Report-September-1996.pdf")
        self.assertEqual(
            result,
            {
                "agency": "DOW",
                "country": "",
                "date": "1996-09-01",
                "date_precision": "month",
                "item_type": "Report",
            },
        )


class TestDOS(unittest.TestCase):
    def test_dos_kazakhstan(self):
        result = parse_dos("DOS-UAP-D2-Cable-2-Kazakhstan-January-1994.pdf")
        self.assertEqual(
            result,
            {
                "agency": "DOS",
                "country": "Kazakhstan",
                "date": "1994-01-01",
                "date_precision": "month",
                "item_type": "Cable",
            },
        )

    def test_dos_multiword_country(self):
        # "Papua-New-Guinea" must be captured as a single hyphenated country
        result = parse_dos(
            "DOS-UAP-D1-Cable-1-Papua-New-Guinea-January-1985.pdf"
        )
        self.assertEqual(result["country"], "Papua-New-Guinea")
        self.assertEqual(result["date"], "1985-01-01")


class TestNASA(unittest.TestCase):
    def test_nasa_image_vm3(self):
        result = parse_nasa("NASA-UAP-VM3-Apollo-12-1969.jpg")
        self.assertEqual(
            result,
            {
                "agency": "NASA",
                "country": "",
                "date": "1969-01-01",
                "date_precision": "year",
                "item_type": "VM3",
            },
        )

    def test_nasa_pdf_skylab(self):
        result = parse_nasa(
            "NASA-UAP-D7-Skylab-Technical-Crew-Debriefing-1973.pdf"
        )
        self.assertEqual(result["item_type"], "D7")
        self.assertEqual(result["date"], "1973-01-01")

    def test_nasa_pdf_apollo_with_descriptor(self):
        result = parse_nasa(
            "NASA-UAP-D5-Apollo-17-Crew-Debriefing-for-Science-1973.pdf"
        )
        self.assertEqual(result["item_type"], "D5")
        self.assertEqual(result["date"], "1973-01-01")
        self.assertEqual(result["country"], "")


class TestNegatives(unittest.TestCase):
    def test_fbi_case_file_returns_none(self):
        self.assertIsNone(
            parse_filename("65_HS1-834228961_62-HQ-83894_Section_2.pdf")
        )
        self.assertIsNone(parse_filename("FBI-Photo-B15.pdf"))

    def test_dod_video_returns_none(self):
        self.assertIsNone(parse_filename("DOD_111688723.mp4"))

    def test_usper_returns_none(self):
        self.assertIsNone(parse_filename("USPER-Statement-Redacted.pdf"))

    def test_misc_returns_none(self):
        self.assertIsNone(parse_filename("059UAP00011.pdf"))
        self.assertIsNone(parse_filename("Serial-4-Redacted_Redacted.pdf"))
        self.assertIsNone(parse_filename("Western_US_Event_Slides_5.08.2026.pdf"))


class TestDispatch(unittest.TestCase):
    def test_dispatch_routes_dow(self):
        result = parse_filename("DOW-UAP-D16-Mission-Report-Syria-July-2022.pdf")
        self.assertEqual(result["agency"], "DOW")

    def test_dispatch_routes_dos(self):
        result = parse_filename(
            "DOS-UAP-D1-Cable-1-Papua-New-Guinea-January-1985.pdf"
        )
        self.assertEqual(result["agency"], "DOS")

    def test_dispatch_routes_nasa(self):
        result = parse_filename("NASA-UAP-VM6-Apollo-17-1972.jpg")
        self.assertEqual(result["agency"], "NASA")


if __name__ == "__main__":
    unittest.main(verbosity=2)
