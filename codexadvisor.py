import json
from pathlib import Path
import argparse
import re

class CodexAdvisor:
    def __init__(self, metrics_path, comments_path, codex_path, protocol_path):
        self.metrics_path = Path(metrics_path)
        self.comments_path = Path(comments_path)
        self.codex_lines = Path(codex_path).read_text().splitlines()
        self.protocol_lines = Path(protocol_path).read_text().splitlines()
        self.metrics = json.loads(self.metrics_path.read_text())
        self.comments = json.loads(self.comments_path.read_text())

    def _find_line(self, phrase):
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        for idx, line in enumerate(self.protocol_lines, start=1):
            if pattern.search(line):
                return idx, line.strip()
        return None, ""

    def recommend(self):
        recs = []
        rr = self.metrics.get("retention_rate", 0)
        if rr < 70:
            ln, text = self._find_line("Hook Supremacy")
            recs.append({
                "reason": f"Retention rate {rr}% below target 70%",
                "source": f"Proof_AI_Advisor_Protocol.txt:{ln}",
                "source_text": text,
                "suggestion": "Tighten the hook (<0.3s) and add a retention trap"
            })
        ctr = self.metrics.get("click_through_rate", 0)
        if ctr < 0.05:
            ln, text = self._find_line("Retention First, Then Engagement")
            recs.append({
                "reason": f"Click-through rate {ctr*100:.1f}% below target 5%",
                "source": f"Proof_AI_Advisor_Protocol.txt:{ln}",
                "source_text": text,
                "suggestion": "Improve CTA that challenges identity"
            })
        for c in self.comments:
            if re.search(r"editing", c["comment"], re.IGNORECASE):
                ln, text = self._find_line("Retention Burst Edit")
                recs.append({
                    "reason": "Comment trend: requests for better editing",
                    "source": f"Proof_AI_Advisor_Protocol.txt:{ln}",
                    "source_text": text,
                    "suggestion": "Apply Retention Burst Edit with faster cuts"
                })
                break
        return recs


def main():
    parser = argparse.ArgumentParser(description="Analyze Codex performance data")
    parser.add_argument("--metrics", default="data/metrics.json")
    parser.add_argument("--comments", default="data/comments.json")
    parser.add_argument("--codex", default="Proof_Codex_3.0_Full_Master_Playbook.txt")
    parser.add_argument("--protocol", default="Proof_AI_Advisor_Protocol.txt")
    args = parser.parse_args()

    advisor = CodexAdvisor(args.metrics, args.comments, args.codex, args.protocol)
    recs = advisor.recommend()
    for r in recs:
        print("- Reason:", r["reason"])
        print("  Source:", r["source"])
        print("  Source Text:", r["source_text"])
        print("  Suggestion:", r["suggestion"])
        print()

if __name__ == "__main__":
    main()
