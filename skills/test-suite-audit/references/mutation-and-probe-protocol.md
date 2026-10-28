When to read: before executing semantic mutations or targeted reproductions during an audit.

# Mutation and Probe Protocol

This procedure binds conclusions to the actual source, runtime, exercised path, and observation; it does not require a particular mutation tool or live service. The core owns completion rules; [report contract](report-contract.md) owns evidence statuses and report fields.

## 1. Bound and preserve the experiment

- Record revision, relevant source hashes, existing working-tree changes, selected fault/contract, commands, test filters, requested/resolved runtime versions, and profile settings.
- Follow repository permissions. Use disposable local data and resources; do not access production, real user data, or shared services to test a failure.
- Prefer an isolated source overlay or disposable worktree. If a temporary local edit is permitted, save the exact original bytes, protect unrelated changes, and arrange restoration even after command failure or interruption. The audit does not authorize permanent remediation edits.
- Keep the subject real where possible and substitute only the boundary needed for isolation. Record substituted boundaries and what they cannot establish.

## 2. Establish a usable baseline and control

- Run the unmodified relevant tests under the same profile/filter used for the proposed mutant. Record exit code, selected tests, assertions where available, skips, errors, and observed behavior.
- A failing baseline makes the mutation experiment Blocked. Do not count unrelated failures, bootstrap mismatches, or zero selected tests as fault detection.
- Baselines may be reused only while relevant source, dependencies, profile, and test selection remain identical; record the reuse.
- Include a known-detectable control: a separate valid semantic fault that a specific existing assertion is expected to reject. Confirm its path is exercised and the assertion fails for that reason. Run it once per unchanged experimental setup rather than after every edit.
- If the control cannot be shown to work, label the affected fault experiments Blocked; preserve raw outcomes, but do not promote them to Observed survivor or Killed. Do not treat an intentional syntax error as a behavioral control.

## 3. Verify the actual fault and its activation

- Apply one independently interpretable semantic fault. Record exact old/new text or patch and replacement count, and verify the applied bytes in the runtime-visible source.
- Confirm the mutant loads and the relevant path is reached. Use test trace, scoped instrumentation, a boundary observation, or a verified fixture-to-source execution trace. Merely selecting a test class or seeing a green exit is insufficient.
- Verify the relevant tests actually ran. Zero selected or only-skipped tests are Blocked, not evidence of survival or detection.
- If setup, baseline, or control is invalid, use Blocked. Otherwise, if the valid fault is skipped, unloaded, or unreached, use Not exercised. A syntax/load failure or unrelated crash is Blocked, not Killed.
- A passing baseline plus a valid applied/exercised fault and passing tests supports Observed survivor. A new behavior-relevant assertion failure supports Killed. Record failure reasons, not only exit codes.

## 4. Broaden only as needed for the claim

- Begin with the relevant component tests. Neighboring tests may reject a fault even when the targeted class does not.
- Before making a suite-wide claim, execute the relevant broader suite against the individual mutant and a matching baseline. Do not combine separate edits and then imply each was independently tested.
- Qualify results by profile: single-site is not multisite; reduced dependency loading is not the default environment. List skipped contracts and unavailable backends.
- Report experiment runs and distinct edits separately; repeated filters/profiles of the same edit are not new independent faults. Selected suspected gaps are not a random mutation score.

## 5. Reproduce suspected existing defects separately

- Use unmodified production code with an independently specified expected outcome. Verify that the outcome is contractual; unresolved product decisions remain open questions.
- Keep a valid positive control where meaningful. For rejection, change only the intended guard; for cleanup, create and observe a disposable resource before asserting its disappearance.
- For races, use independent actors and a deterministic interleaving at the contested operation, backed by an owned disposable backend shared by those actors. Do not use a pre-existing shared service. Serial simulation supports only serial behavior.
- For protocol/transport probes, preserve canonical response shapes, status distinctions, and the subject's downstream behavior. Inspect exact targets or payload bytes instead of inferring them from metadata or call counts.
- Treat a reproduced defect as Current defect with evidence status Not applicable, since no fault was injected. Record the actual violation and scope in Real observation. A local probe does not establish deployment exposure, incident frequency, live vendor behavior, or every supported runtime.

## 6. Restore and retain evidence

- Restore original source bytes or discard the isolated overlay/worktree in failure-safe cleanup. Verify the source hashes and confirm unrelated working-tree content is unchanged.
- Release only resources created and owned by this experiment. Do not infer ownership from a familiar fixed name.
- If restoration or resource cleanup cannot be verified, stop further experiments and report the problem and exact residual state. Do not claim the audit left the workspace unchanged.
- Until restoration and resource cleanup are verified, classify the affected mutation experiment as Blocked while preserving its raw observations. Direct unmodified-code probe rows remain Not applicable with the cleanup limitation disclosed. Apply the core's Partial rule after meaningful inspection for either kind of experiment.
- Retain commands, source changes, baseline/control/mutant or probe results, logs or exact summaries, path-activation evidence, and cleanup verification in the audit evidence record.
- Use evidence statuses from the report contract and completion rules from the core. A blocked experiment makes an audit Partial when that execution was requested; it need not invalidate independent static findings. Unverified restoration or resource cleanup makes the audit Partial after meaningful inspection even for an optional experiment.
