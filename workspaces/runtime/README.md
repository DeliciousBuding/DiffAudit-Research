# Runtime Workspace

This directory is reserved for runtime integration notes and stable handoff
documents.

Raw runtime job queue dumps are local machine artifacts. They can contain
absolute paths, local failure details, and command tails, so they are ignored by
git under `workspaces/runtime/jobs/`.

Commit durable runtime evidence as sanitized summaries under the relevant
`experiments/` or `workspaces/<lane>/runs/` evidence anchor instead.
