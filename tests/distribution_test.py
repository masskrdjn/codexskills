"""Keep version references and independently installed distribution copies aligned."""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/codexskills'
TEMPLATES = PLUGIN / 'templates'


class Distribution(unittest.TestCase):
    def test_current_version_matches_readmes_and_changelog(self):
        version = json.loads((PLUGIN / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))['version']
        self.assertRegex(version, r'^\d+\.\d+\.\d+$')
        for filename, label in (('README.md', 'Current plugin version'),
                                ('README.fr.md', 'Version actuelle du plugin')):
            text = (ROOT / filename).read_text(encoding='utf-8')
            match = re.search(re.escape(label) + r'\s*:\s*\*\*([^*]+)\*\*', text)
            self.assertIsNotNone(match, filename)
            self.assertEqual(match[1], version, filename)
        entries = re.findall(r'^## (\d+\.\d+\.\d+) — \d{4}-\d{2}-\d{2}',
                             (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8'), re.MULTILINE)
        self.assertTrue(entries, 'Missing dated changelog entry')
        self.assertEqual(entries[0], version)
        self.assertEqual(len(entries), len(set(entries)), 'Duplicate changelog version')

    def test_installed_sources_match_repository_sources(self):
        expected = {Path('AGENTS.md'), Path('.codex/config.toml'),
                    Path('.agents/skills/quota-orchestrator/SKILL.md')}
        expected.update(path.relative_to(ROOT) for path in (ROOT / '.codex/agents').glob('*.toml'))
        actual = {path.relative_to(TEMPLATES) for path in TEMPLATES.rglob('*') if path.is_file()}
        self.assertEqual(actual, expected)
        for relative in sorted(expected):
            with self.subTest(path=relative):
                self.assertEqual((ROOT / relative).read_bytes(), (TEMPLATES / relative).read_bytes())

    def test_installers_differ_only_in_source_location(self):
        repository = (ROOT / 'install.py').read_text(encoding='utf-8')
        bundled = (PLUGIN / 'scripts/install.py').read_text(encoding='utf-8')
        source = 'SOURCE = Path(__file__).resolve().parent\n'
        self.assertEqual(repository.count(source), 1)
        self.assertEqual(repository.replace(source,
                         'SOURCE = Path(__file__).resolve().parent.parent / "templates"\n', 1), bundled)


if __name__ == '__main__':
    unittest.main()
