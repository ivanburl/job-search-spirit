"""Exercise PDF evidence collection with synthetic fixtures, never personal CVs."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from reportlab.pdfgen import canvas


SCRIPT = Path(__file__).resolve().parents[1] / "skills/cv-reader/scripts/extract_pdf.py"
spec = importlib.util.spec_from_file_location("cv_pdf", SCRIPT)
cv_pdf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cv_pdf)


class PdfEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_pages_hidden_links_and_bullet_continuation(self):
        pdf = self.root / "resume.pdf"
        doc = canvas.Canvas(str(pdf))
        doc.drawString(40, 780, "Jane Doe")
        doc.drawString(40, 750, "GitHub")
        doc.linkURL("https://github.com/example", (40, 748, 90, 765))
        doc.drawString(40, 720, "Engineer - Example Company")
        doc.drawString(40, 700, "- Reduced build time by 30% using")
        doc.drawString(50, 685, "Python and CI pipelines.")
        doc.showPage()
        doc.drawString(40, 780, "Education")
        doc.drawString(40, 760, "Example University, 2018-2022")
        doc.save()
        result = cv_pdf.extract_pdf(pdf)
        self.assertEqual(result["page_count"], 2)
        self.assertEqual([p["page"] for p in result["pages"]], [1, 2])
        self.assertIn("30%", result["pages"][0]["text"])
        self.assertIn("Python and CI pipelines.", result["pages"][0]["text"])
        self.assertNotIn("https://github.com/example", result["pages"][0]["text"])
        self.assertEqual(result["pages"][0]["links"][0]["uri"], "https://github.com/example")
        self.assertIn("Example University", result["pages"][1]["text"])

    def test_columns_retain_positions_for_agent_review(self):
        pdf = self.root / "columns.pdf"
        doc = canvas.Canvas(str(pdf))
        doc.drawString(40, 750, "SKILLS")
        doc.drawString(320, 750, "EXPERIENCE")
        doc.drawString(40, 730, "Python")
        doc.drawString(320, 730, "Engineer")
        doc.save()
        words = {w["text"]: w for w in cv_pdf.extract_pdf(pdf)["pages"][0]["words"]}
        self.assertLess(words["Python"]["x0"], words["Engineer"]["x0"])
        self.assertAlmostEqual(words["Python"]["top"], words["Engineer"]["top"])

    def test_image_only_page_is_flagged_and_rendered(self):
        image_path = self.root / "scan.png"
        Image.new("RGB", (200, 100), "white").save(image_path)
        pdf = self.root / "scan.pdf"
        doc = canvas.Canvas(str(pdf))
        doc.drawImage(str(image_path), 40, 600)
        doc.save()
        page = cv_pdf.extract_pdf(pdf, self.root / "rendered")["pages"][0]
        self.assertEqual(page["text"], "")
        self.assertEqual(page["image_count"], 1)
        self.assertTrue(any("OCR" in reason for reason in page["review_reasons"]))
        with Image.open(page["rendered_image"]) as rendered:
            self.assertGreater(rendered.width, 0)
            self.assertGreater(rendered.height, 0)

    def test_corrupt_pdf_fails_instead_of_returning_empty_cv(self):
        pdf = self.root / "bad.pdf"
        pdf.write_bytes(b"not a PDF")
        with self.assertRaises(Exception):
            cv_pdf.extract_pdf(pdf)

    def test_existing_render_is_preserved(self):
        pdf = self.root / "resume.pdf"
        doc = canvas.Canvas(str(pdf))
        doc.drawString(40, 750, "Jane Doe")
        doc.save()
        render_dir = self.root / "rendered"
        render_dir.mkdir()
        output = render_dir / "page-001.png"
        output.write_bytes(b"existing")
        with self.assertRaises(FileExistsError):
            cv_pdf.extract_pdf(pdf, render_dir)
        self.assertEqual(output.read_bytes(), b"existing")


if __name__ == "__main__":
    unittest.main()
