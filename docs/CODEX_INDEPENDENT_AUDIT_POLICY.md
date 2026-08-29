# Independent Phase-Gate Audit Policy

> Historical filename note: this file keeps the name `CODEX_INDEPENDENT_AUDIT_POLICY.md` so existing links and audit records remain stable. The policy itself is tool-neutral.

## Purpose

Independent audits are high-cost phase-gate reviews. They are not routine per-slice or per-pull-request code review.

Use ordinary repository review, protected tests, CI, and issue tracking for normal design and implementation work. Reserve an independent audit for a completed design boundary or implementation candidate that is ready to be accepted or frozen as a whole.

The purpose of independence is to reduce implementation-context bias. It is **not** to require a particular product, model, or vendor, and it is not a reason to reread unrelated repository history.

## Independence is role-based

An audit is independent only when the reviewer:

- did not author or materially implement the exact candidate being certified;
- starts from a fresh review context rather than relying on the implementation conversation or private implementation reasoning;
- audits one exact commit read-only;
- records evidence, findings, and a gate conclusion durably;
- does not repair the candidate while acting as the independent reviewer.

Eligible reviewers may include Codex, a fresh ChatGPT conversation, another model or tool, or a human reviewer.

A separate fresh ChatGPT conversation is eligible to audit a candidate authored in another ChatGPT conversation when the audit conversation does not rely on the implementation conversation and reconstructs its judgment from repository state, the exact candidate, and the audit packet.

A reviewer is not made independent merely by changing tools if the reviewer is still relying on the implementation conversation or acting as the author of the candidate.

## Default cadence

Do not request an independent phase-gate audit for every:

- implementation slice;
- pull request;
- ordinary bug fix;
- documentation update;
- intermediate repair commit;
- design edit between planned gates.

Use independent audits at meaningful acceptance or freeze boundaries. Avoid audit-repair-reaudit ping-pong. A repeat audit is justified when the previous conclusion blocks the gate, the evidence was insufficient, or a repair materially changes a boundary that the audit was asked to certify.

## Risk-scoped reconstruction

Independent audits use **risk-scoped reading by default**.

Always inspect the material needed to answer the gate question:

1. the exact base/head and candidate diff;
2. the changed files and reachable behavior relevant to those changes;
3. the scope authorization or design decision governing the candidate;
4. directly applicable contract, ADR, matrix, or evidence-map requirements;
5. frozen invariants that the diff could plausibly affect;
6. relevant tests, exact-candidate CI, and useful adversarial cases;
7. current Issue, PR, and handoff state needed to identify the gate and candidate.

Do **not** require a reviewer to read every historical ADR, implementation slice, previous audit, obsolete handoff, research note, or unrelated phase document merely because it exists.

Expand into older or broader material when there is a concrete reason, including:

- the diff touches or may cross that boundary;
- two authoritative sources appear to conflict;
- the provenance of a relevant invariant cannot otherwise be established;
- a finding requires historical reconstruction;
- the reviewer has evidence of a hidden cross-boundary effect.

Skipping irrelevant history is allowed. Skipping a materially affected authority, security, persistence, checkpoint, rollback, resource, evaluator, frozen-control, or other gate-critical boundary is not.

## Audit packet

Each gate Issue should provide a compact audit packet containing, as applicable:

- exact base and head;
- primary audit question;
- changed-file list or bounded diff scope;
- scope authorization;
- directly governing normative references;
- frozen invariants plausibly at risk;
- exact-candidate CI and test evidence;
- explicit capability-absence, authority, security, privacy, cost, or resource checks when relevant;
- finding format;
- allowed gate conclusions.

The audit packet and this policy take precedence over the ordinary repository-wide collaborator cold-start reading order for a read-only phase-gate audit. `AGENTS.md` continues to govern repository work generally.

The packet is an entry point, not a blind trust boundary. The reviewer must inspect the exact candidate and may expand scope whenever evidence warrants it.

## Test and CI evidence

A phase-gate audit must verify that appropriate protected evidence exists for the exact candidate.

The reviewer does not have to rerun the complete protected suite solely to duplicate an already trustworthy exact-candidate CI run. Rerun the relevant suite or additional checks when:

- exact-candidate CI is missing, stale, incomplete, or failing;
- a finding calls the existing test evidence into question;
- the candidate touches a boundary whose protection is not demonstrated by the recorded CI;
- the audit Issue explicitly requires an independent rerun for a concrete gate-level reason.

Targeted adversarial tests are encouraged where they probe the actual risk more directly than a ritual full rerun.

## Required audit behavior

Each independent audit must:

- remain read-only unless a separate implementation task is explicitly authorized after the audit role ends;
- identify the exact audited commit;
- distinguish verified evidence from assumptions;
- inspect important cross-boundary interactions relevant to the candidate, not only expected paths;
- report important risk areas inspected where no issue was found when useful to the gate decision;
- use exact file and symbol or document references for findings;
- avoid weakening tests, redefining the contract, or introducing the next phase to make a finding disappear.

Every finding should include:

- severity;
- affected invariant or requirement;
- exact file and symbol or document section;
- evidence and reasoning;
- minimal reproduction when possible;
- whether current protected evidence catches it;
- recommended disposition.

The gate Issue may require a more specific finding format or a fixed set of conclusion phrases.

## Historical completed audits

### Phase 1 closure

Issue #56 completed the final Phase 1 audit at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`, resolved the reported findings, and confirmed the protected 152-test baseline before Phase 1 freeze.

### Phase 2 design and implementation

Phase 2 used separate design and implementation phase-gate audits. The final implementation closure audit in Issue #127 checked exact candidate `12de7b7d7413f343b2e5a74df369c26a5896c865` and concluded the complete Phase 2 baseline was ready to freeze.

These historical audits remain valid records. This policy change alters the method for future audits; it does not retroactively reinterpret their conclusions.

## Current Phase 3 application

Issue #147 remains the independent read-only audit record for PR #146 exact candidate `1eba3308b01de2b31ffa58b4157105984a376400`.

For that audit, the substantive Phase 3 risks listed in #147 remain in scope. The reviewer should prioritize the exact Phase 3 diff, Issue #145 authorization, directly governing accepted Phase 3 design material, frozen Phase 1/2 invariants plausibly affected by the additive package, and exact-candidate test/CI evidence. Historical material should be opened when a concrete audit question requires it rather than read exhaustively by default.

Issue #148 records the adoption of this role-based, risk-scoped policy.