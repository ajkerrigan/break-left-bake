from collections import Counter
from pathlib import Path
import pprint


def main(path="defsec"):
    rules_dir = Path(path) / "internal" / "rules"

    rules = []
    stats = Counter()
    for provider in ("aws", "azure", "google"):
        provider_dir = rules_dir / provider
        for rule_file in provider_dir.rglob("*.go"):

            if "test" in rule_file.name:
                continue
            if ".tf." in rule_file.name:
                continue
            if ".cf." in rule_file.name:
                continue

            rule = extract_rule(rule_file.read_text().splitlines())
            if rule:
                stats[provider] += 1
                rules.append(rule)

    print(stats)


#    print(len(rules))


def extract_rule(lines):

    start_token = "scan.Rule{"
    end_token = "},"

    start_pos = None
    end_pos = None
    rule_keys = (
        "AVDID",
        "Provider",
        "Service",
        "ShortCode",
        "Summary",
        "Impact",
        "Resolution",
        "Explanation",
        "Severity",
    )

    for idx, line in enumerate(lines):
        if start_token in line:
            start_pos = (idx, line.index(start_token))
        if not start_pos:
            continue
        if end_token == line.strip() and line.index(end_token) == start_pos[-1]:
            end_pos = idx
            break

    if not start_pos:
        return
    if not end_pos:
        return
    rule = {}
    block = lines[start_pos[0] + 1 : end_pos]

    for l in block:
        for k in rule_keys:
            if l.strip().startswith(k):
                v = l.split(":", 1)[-1]
                v = v.strip().strip('"').strip(",")
                rule[k.lower()] = v
    return rule


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback, pdb, sys

        traceback.print_exc()
        pdb.post_mortem(sys.exc_info()[-1])
