# Development by Intent Discussions

This repository uses GitHub Discussions to examine the architectural implications of Development by Intent (DbI) and AI-native application development.

The purpose is not to promote a predetermined conclusion. It is to make important claims explicit, expose them to technical criticism, compare them with conventional software-development practice, and identify experiments that can strengthen, narrow, or falsify them.

## How to participate

When possible, separate:

- **Observed result** — something directly demonstrated or experienced.
- **Verified fact** — something supported by reproducible evidence or an authoritative source.
- **Interpretation** — what the observation appears to mean.
- **Hypothesis** — a proposed explanation that still requires testing.
- **Future possibility** — what might become possible if the hypothesis holds.

Strong disagreement is welcome. The most useful responses explain where a claim fails, provide a counterexample, or propose a test.

## Initial architectural questions

1. **What is the correct human-machine development boundary when the execution environment itself is intelligent?**
2. **Are we leaving AI intelligence on the table by primarily using it to generate code?**
3. **If AI already provides a functioning capability fabric, should applications still be constructed primarily through predefined software architectures?**
4. **Can behavioral correction replace some classes of implementation debugging?**

## Current DbI working proposition

Development by Intent explores a development boundary in which the human governs intent, constraints, evaluation, and acceptance while AI assumes the burden of implementation.

This does **not** assert that code, architecture, testing, or debugging disappear. The question is whether implementation artifacts should remain the primary interface through which humans define and modify applications when the execution environment can interpret intent and select implementation paths itself.
