# Implementation — Hermes-Operated Claude Portability 001

The target selected no conventional code implementation. Claude Code ran in print mode with `--allowedTools ''`, so it could not create files, execute shell commands, read additional files, search the web, spawn sub-agents, or modify persistent state.

The reconstructed Amazing Birthday application existed as a **behavioral disposition in the Claude conversation context**. That disposition was carried forward through the same session with `--resume` and invoked by the short trigger messages.

This is an important implementation-divergence result: the same governed application behavior can be realized as conversation-context behavior rather than as a standalone program or skill. Under the frozen rubric, implementation medium is not scored; behavior is.

Target configuration:

- Claude Code 2.1.170
- substantive target model `claude-sonnet-4-6`
- print mode (`-p`)
- no target tools
- same session resumed across reconstruction and tests
- only the two Phase A artifacts in the system prompt before freeze

No standalone application code was written and no reconstructed state was persisted outside the Claude session.