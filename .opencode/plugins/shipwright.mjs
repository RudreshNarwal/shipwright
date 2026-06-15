// shipwright — OpenCode plugin.
//
// Shipwright is an orchestrator, not a ruleset injector: it has no rules to
// inject into the system prompt (unlike, say, ponytail). OpenCode discovers the
// `skills/` in this checkout on its own. So this plugin does exactly one thing —
// it gives OpenCode the same gstack dependency check that Claude Code gets from
// hooks/hooks.json: on session start it runs scripts/preflight-gstack.sh and
// surfaces the result, so you learn up front whether Phases 5-6 (browser QA,
// ship) are available.
//
// Add it to your opencode.json:
//   { "plugin": ["./.opencode/plugins/shipwright.mjs"] }

import { execFile } from 'child_process';
import { fileURLToPath } from 'url';
import path from 'path';

// scripts/preflight-gstack.sh lives two levels up from .opencode/plugins/.
const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const preflight = path.join(repoRoot, 'scripts', 'preflight-gstack.sh');

function runPreflight() {
  return new Promise((resolve) => {
    execFile('bash', [preflight], { cwd: repoRoot, timeout: 10_000 }, (err, stdout) => {
      // The script exits 0 in every case; it prints a message only when gstack
      // is missing (and stays silent when present). Surface whatever it emits.
      resolve((stdout || '').trim());
    });
  });
}

export default async () => {
  let announced = false;
  return {
    // session.created fires when a new session begins.
    event: async ({ event } = {}) => {
      if (announced) return;
      if (event?.type !== 'session.created') return;
      announced = true;
      const message = await runPreflight();
      if (message) console.log(`[shipwright] ${message}`);
    },
  };
};
