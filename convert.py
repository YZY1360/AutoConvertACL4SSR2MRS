#!/usr/bin/env python3
"""
ACL4SSR → Mihomo MRS Rule-Set Converter

Converts ACL4SSR Clash-format .list files to Mihomo binary MRS format.
MRS only supports domain and ipcidr behaviors separately, so mixed files
are split into two MRS outputs:
  - <name>.mrs       → domain rules (DOMAIN, DOMAIN-SUFFIX, DOMAIN-KEYWORD, DOMAIN-REGEX)
  - <name>_ip.mrs    → IP CIDR rules (IP-CIDR, IP-CIDR6, SRC-IP-CIDR)

Usage:
  python3 convert.py <source_dir> <output_dir> [mihomo_bin]

Requirements:
  - mihomo binary (download from https://github.com/MetaCubeX/mihomo/releases)
"""

import sys
import os
import re
import subprocess
import shutil
import tempfile
from pathlib import Path


# Rules that mihomo domain converter accepts (Clash format)
DOMAIN_RULE_TYPES = {'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'DOMAIN-REGEX'}

# Rules that mihomo ipcidr converter accepts (plain CIDR only)
IP_RULE_TYPES = {'IP-CIDR', 'IP-CIDR6', 'SRC-IP-CIDR'}

# Comment/empty line pattern
COMMENT_RE = re.compile(r'^\s*(#|$)')


def parse_list_file(filepath: str) -> tuple[list[str], list[str]]:
    """Parse an ACL4SSR .list file, return (domain_rules, ip_rules)."""
    domain_rules = []
    ip_rules = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.strip()
            if COMMENT_RE.match(line):
                continue

            # Split on first comma to get rule type
            parts = line.split(',', 1)
            if not parts:
                continue

            rule_type = parts[0].strip().upper()

            if rule_type in DOMAIN_RULE_TYPES:
                domain_rules.append(line)
            elif rule_type in IP_RULE_TYPES:
                # Extract plain CIDR: strip "IP-CIDR," prefix and ",no-resolve" suffix
                cidr = parts[1].split(',')[0].strip() if len(parts) > 1 else ''
                if cidr:
                    ip_rules.append(cidr)

    return domain_rules, ip_rules


def convert_to_mrs(mihomo_bin: str, rule_type: str, text_file: str, output_file: str) -> bool:
    """Run mihomo convert-ruleset. Returns True on success."""
    cmd = [mihomo_bin, 'convert-ruleset', rule_type, 'text', text_file, output_file]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"  ERROR converting {rule_type}: {result.stderr[:200]}", file=sys.stderr)
        return False
    return True


def find_mihomo() -> str:
    """Find mihomo binary in PATH or common locations."""
    for candidate in ['mihomo', './mihomo', '/tmp/mihomo']:
        if shutil.which(candidate) or os.path.isfile(candidate):
            return candidate
    return 'mihomo'


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <source_dir> <output_dir> [mihomo_bin]")
        sys.exit(1)

    source_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    mihomo_bin = sys.argv[3] if len(sys.argv) > 3 else find_mihomo()

    output_dir.mkdir(parents=True, exist_ok=True)

    # Collect all .list files (top-level and Ruleset/)
    list_files = sorted(source_dir.glob('*.list')) + sorted(source_dir.glob('Ruleset/*.list'))

    stats = {'total': 0, 'domain_mrs': 0, 'ip_mrs': 0, 'skipped': 0, 'errors': 0}

    for list_file in list_files:
        name = list_file.stem  # filename without .list
        is_ruleset = list_file.parent.name == 'Ruleset'

        # Output paths
        if is_ruleset:
            out_subdir = output_dir / 'Ruleset'
        else:
            out_subdir = output_dir
        out_subdir.mkdir(parents=True, exist_ok=True)

        print(f"Processing: {list_file.relative_to(source_dir)}")

        domain_rules, ip_rules = parse_list_file(str(list_file))

        if not domain_rules and not ip_rules:
            print(f"  SKIP: no rules found")
            stats['skipped'] += 1
            continue

        stats['total'] += 1

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)

            # Convert domain rules
            if domain_rules:
                domain_txt = tmp / f"{name}_domain.txt"
                domain_txt.write_text('\n'.join(domain_rules) + '\n', encoding='utf-8')
                domain_mrs = out_subdir / f"{name}.mrs"
                if convert_to_mrs(mihomo_bin, 'domain', str(domain_txt), str(domain_mrs)):
                    stats['domain_mrs'] += 1
                    print(f"  -> {domain_mrs.relative_to(output_dir.parent) if output_dir.parent != Path('.') else domain_mrs.name} ({len(domain_rules)} domain rules)")
                else:
                    stats['errors'] += 1

            # Convert IP rules
            if ip_rules:
                ip_txt = tmp / f"{name}_ip.txt"
                ip_txt.write_text('\n'.join(ip_rules) + '\n', encoding='utf-8')
                ip_mrs = out_subdir / f"{name}_ip.mrs"
                if convert_to_mrs(mihomo_bin, 'ipcidr', str(ip_txt), str(ip_mrs)):
                    stats['ip_mrs'] += 1
                    print(f"  -> {ip_mrs.relative_to(output_dir.parent) if output_dir.parent != Path('.') else ip_mrs.name} ({len(ip_rules)} IP rules)")
                else:
                    stats['errors'] += 1

    print()
    print("=" * 50)
    print(f"Summary: {stats['total']} files processed")
    print(f"  Domain MRS created: {stats['domain_mrs']}")
    print(f"  IP CIDR MRS created: {stats['ip_mrs']}")
    print(f"  Skipped (empty):    {stats['skipped']}")
    print(f"  Errors:             {stats['errors']}")

    if stats['errors'] > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
