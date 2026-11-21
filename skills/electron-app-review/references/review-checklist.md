Read the sections for checklist areas that the review target affects.

# Electron review checklist

Use the application's installed Electron version and effective configuration. Use [Electron's security guide](https://www.electronjs.org/docs/latest/tutorial/security) as a reference when checking Electron-specific safeguards. Verify defaults against the API documentation for the application's Electron version. Do not assume that development and packaged builds use the same entry points or settings.

## Windows and content

- Inspect each affected window or embedded view and any child-window configuration. Verify effective sandboxing, context isolation, Node integration, and preload selection. Account for session partitions and remote frames when present.
- Identify local and remote content sources. Check navigation, redirects, new windows, custom protocols, and external URL handling against the intended policy. Check content security policy and permission checks and requests for the affected sessions.

## Preload and IPC

- Inventory exposed bridge methods, IPC channels, and event subscriptions. Check that each method exposes only the capability the renderer needs, not arbitrary transport access.
- Inspect the receiving handler. Verify the allowed sender frame or origin, runtime payload validation, and authorization for the selected resource. Repeat the authority check at any forwarding boundary where the receiver cannot rely on a trusted earlier check.
- Inspect event routing and subscription cleanup. Check that replies and events reach only the intended window or frame and do not expose credentials or other workspaces' data.

## Local authority

- Trace filesystem operations to their effective roots and check containment, including link handling when relevant. Inspect how dialogs, file selections, and workspace identifiers establish authority.
- Check whether credentials cross to a renderer, subprocess, log, or persistent store. Verify that each destination receives only what it needs.
- Inspect the executable, arguments, working directory, and inherited environment of affected subprocesses. Verify that renderer input cannot silently widen a user-approved operation.
- For privileged operations that modify state, check what remains after interruption or partial failure. Verify rollback or recovery and check that retries do not repeat completed side effects unless repetition is safe.

## Desktop lifecycle and distribution

- Check close, crash, restart, and cancellation paths for affected processes. Verify ownership and cleanup of child processes, ports, listeners, and pending requests. Check how overlapping requests and late events affect newer operations.
- If packaged behavior changes, inspect the release configuration and artifacts or existing build evidence. Check shipped resources, effective window settings, and platform-specific entry points. Inspect the effective [Electron fuses](https://www.electronjs.org/docs/latest/tutorial/fuses) and ASAR integrity and loading policy for the shipped artifacts. Evaluate applicable fuses against the release policy, including Run as Node, Node options and inspector support, and cookie encryption. Check whether packaged builds expose DevTools or Node debugging beyond the intended release policy. If signing or updates change, inspect artifact authenticity, update source and channel selection, and failure recovery for the affected platforms.

## Examples

- A new workspace action is in scope even if the window configuration is unchanged. Trace the bridge method to its handler and verify the selected workspace at the point of use.
- A renderer-only copy change that does not alter content sources or privileged behavior is out of scope.
- If a diff declares a sandbox but omits a packaged configuration that can override it, mark Windows and content `Blocked` when the missing configuration prevents assessment and the affected control's failure could support a finding. If the impact cannot be bounded below `HIGH`, return `BLOCK`. Do not report a confirmed defect based on the omission alone.
- If missing evidence about a secondary safeguard could support at most a `LOW` finding, mark the area `Blocked` and return `CONCERNS` unless another finding or another `Blocked` area requires `BLOCK`.
- If one unassessed control has a concrete failure path bounded at `LOW` and another unassessed control in the same area has no concrete failure path, disclose both. The second control does not escalate the verdict to `BLOCK`.
- A lifecycle-only change keeps Desktop lifecycle and distribution applicable, but its packaging, signing, and update controls can be `n/a`; justify each `n/a` control instead of marking the area `Not applicable`.
