"""Terra packaging and migration from the exact 0.8.5 routing files."""

import importlib.util
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/codexskills'
TEMPLATES = PLUGIN / 'templates'
FIXTURE = ROOT / 'fixtures/release_0_8_5'


def load_installer(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class TerraRouting(unittest.TestCase):
    def test_distributed_profile_and_instruction_copies(self):
        for role in ('visual_operator', 'writer'):
            relative = Path(f'.codex/agents/{role}.toml')
            self.assertEqual((ROOT / relative).read_bytes(), (TEMPLATES / relative).read_bytes())
            profile = tomllib.loads((TEMPLATES / relative).read_text(encoding='utf-8'))
            self.assertEqual(profile['name'], role)
            self.assertEqual(profile['model'], 'gpt-6.1-terra')
            self.assertEqual(profile['model_reasoning_effort'], 'medium')
            self.assertFalse(profile['agents']['enabled'])
        for relative in ('AGENTS.md', '.agents/skills/quota-orchestrator/SKILL.md'):
            self.assertEqual((ROOT / relative).read_bytes(), (TEMPLATES / relative).read_bytes())

    def test_upgrade_both_installers_and_scopes(self):
        for index, script in enumerate((ROOT / 'install.py', PLUGIN / 'scripts/install.py')):
            installer = load_installer(script, f'terra_installer_{index}')
            for global_scope in (False, True):
                for managed_block in (False, True):
                    with self.subTest(script=script, global_scope=global_scope, managed_block=managed_block):
                        with tempfile.TemporaryDirectory(prefix='terra-migration-') as temp:
                            target = Path(temp)
                            old_agents = (FIXTURE / 'AGENTS.md').read_bytes()
                            if managed_block:
                                old_agents = (b'# user prefix\n' + installer.START.encode() + b'\n' +
                                              old_agents.rstrip(b'\n') + b'\n' + installer.END.encode() +
                                              b'\n# user suffix\n')
                            (target / 'AGENTS.md').write_bytes(old_agents)
                            skill_relative = ('skills/quota-orchestrator/SKILL.md' if global_scope else
                                              '.agents/skills/quota-orchestrator/SKILL.md')
                            skill = target / skill_relative
                            skill.parent.mkdir(parents=True)
                            old_skill = (FIXTURE / '.agents/skills/quota-orchestrator/SKILL.md').read_bytes()
                            skill.write_bytes(old_skill)
                            agent_dir = target / ('agents' if global_scope else '.codex/agents')
                            agent_dir.mkdir(parents=True)
                            custom = agent_dir / 'builder.toml'
                            custom.write_text('name = "custom builder"\n', encoding='utf-8')
                            actions, _, warnings = installer.plan(target, global_scope)
                            self.assertEqual(len(warnings), 1, warnings)
                            self.assertIn('builder.toml', warnings[0])
                            backup = installer.apply(target, actions)
                            self.assertIsNotNone(backup)
                            self.assertEqual((backup / 'AGENTS.md').read_bytes(), old_agents)
                            self.assertEqual((backup / skill_relative).read_bytes(), old_skill)
                            self.assertEqual(skill.read_bytes(), (TEMPLATES / '.agents/skills/quota-orchestrator/SKILL.md').read_bytes())
                            self.assertIn('`visual_operator`', (target / 'AGENTS.md').read_text(encoding='utf-8'))
                            if managed_block:
                                self.assertTrue((target / 'AGENTS.md').read_bytes().startswith(b'# user prefix\n'))
                                self.assertTrue((target / 'AGENTS.md').read_bytes().endswith(b'# user suffix\n'))
                            self.assertEqual(custom.read_text(encoding='utf-8'), 'name = "custom builder"\n')
                            self.assertEqual((agent_dir / 'visual_operator.toml').read_bytes(),
                                             (TEMPLATES / '.codex/agents/visual_operator.toml').read_bytes())
                            self.assertEqual((agent_dir / 'writer.toml').read_bytes(),
                                             (TEMPLATES / '.codex/agents/writer.toml').read_bytes())
                            repeated, _, repeated_warnings = installer.plan(target, global_scope)
                            self.assertEqual(repeated, [])
                            self.assertEqual(repeated_warnings, warnings)


if __name__ == '__main__':
    unittest.main()
