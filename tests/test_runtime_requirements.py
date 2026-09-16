from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PACKAGES = {"fastapi", "uvicorn", "pydantic"}


class RuntimeRequirementsTest(unittest.TestCase):
    def test_production_requirements_are_pinned_and_runtime_only(self):
        requirements = [
            line.strip()
            for line in (REPOSITORY_ROOT / "requirements.txt").read_text().splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]

        package_names = {requirement.split("==", 1)[0].lower() for requirement in requirements}

        self.assertEqual(package_names, RUNTIME_PACKAGES)
        self.assertTrue(all("==" in requirement for requirement in requirements))


if __name__ == "__main__":
    unittest.main()
