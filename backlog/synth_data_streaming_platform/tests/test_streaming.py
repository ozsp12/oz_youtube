import ast
import json
import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from synthetic_data import StreamingConfig, StreamingPlatformGenerator


POPULATION_PATH = ROOT / "streaming_platform" / "estimativa_dou_2021.csv"
NOTEBOOK_PATH = ROOT / "streaming_platform" / "streaming_music_data.ipynb"


class GeneratorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = StreamingConfig()
        cls.generator = StreamingPlatformGenerator(cls.config)
        cls.tables = cls.generator.generate(POPULATION_PATH)

    def test_population_source(self):
        population = self.tables["state_population"]
        self.assertEqual(len(population), 27)
        self.assertEqual(int(population["population"].sum()), 213_317_639)
        self.assertAlmostEqual(population["sampling_probability"].sum(), 1.0)

    def test_expected_table_sizes(self):
        self.assertEqual(len(self.tables["catalog"]), 360)
        self.assertEqual(len(self.tables["users"]), 1_000)
        self.assertEqual(len(self.tables["events"]), 2_992)

    def test_relational_integrity(self):
        report = self.generator.quality_report(self.tables)
        integrity_fields = [
            "duplicate_user_ids",
            "duplicate_track_ids",
            "duplicate_event_ids",
            "unknown_event_users",
            "unknown_event_tracks",
            "missing_event_values",
        ]
        self.assertTrue(report[integrity_fields].eq(0).all())

    def test_generation_is_reproducible(self):
        replicated = StreamingPlatformGenerator(self.config).generate(POPULATION_PATH)
        for name in self.tables:
            with self.subTest(table=name):
                pd.testing.assert_frame_equal(self.tables[name], replicated[name])

    def test_different_seed_changes_stochastic_tables(self):
        alternative = StreamingPlatformGenerator(
            StreamingConfig(seed=7)
        ).generate(POPULATION_PATH)
        self.assertFalse(self.tables["users"].equals(alternative["users"]))
        self.assertFalse(self.tables["events"].equals(alternative["events"]))

    def test_invalid_configuration_is_rejected(self):
        with self.assertRaises(ValueError):
            StreamingConfig(n_users=0)
        with self.assertRaises(ValueError):
            StreamingConfig(sex_probabilities=(0.7, 0.7))


class NotebookTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))

    def test_notebook_structure(self):
        self.assertEqual(self.notebook.get("nbformat"), 4)
        self.assertIsInstance(self.notebook.get("cells"), list)
        self.assertGreater(len(self.notebook["cells"]), 0)

    def test_required_sections(self):
        markdown = "\n".join(
            "".join(cell.get("source", []))
            for cell in self.notebook["cells"]
            if cell.get("cell_type") == "markdown"
        )
        for heading in (
            "## tl;dr",
            "## Context & Methods",
            "## Data",
            "## Results",
            "## Takeaways",
        ):
            self.assertIn(heading, markdown)

    def test_code_cell_syntax(self):
        for index, cell in enumerate(self.notebook["cells"]):
            if cell.get("cell_type") == "code":
                with self.subTest(cell=index):
                    ast.parse("".join(cell.get("source", [])))

    def test_no_stored_errors(self):
        errors = [
            output
            for cell in self.notebook["cells"]
            for output in cell.get("outputs", [])
            if output.get("output_type") == "error"
        ]
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
