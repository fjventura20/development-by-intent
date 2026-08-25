# Development by Intent — Working Theory

## Definition

Development by Intent is an experimental software-development approach in which application behavior is produced by expressing, refining, constraining, testing, and preserving intent against a general-purpose AI substrate.

The developer is not necessarily constructing all of the mechanisms that produce the behavior. Instead, the developer specifies the desired behavior and governs an intelligent mechanism that already possesses many of the required capabilities.

## Architectural distinction

A simplified conventional model is:

`domain intent → requirements → implementation → executable behavior`

A simplified Development by Intent model is:

`domain intent → conversational refinement + constraints + tests → AI-mediated executable behavior`

This does not imply that conventional code disappears. Deterministic algorithms, integrations, security boundaries, storage, interfaces, and infrastructure may still require conventional implementation.

## Candidate advantages

Development by Intent may reduce the distance between domain knowledge and executable behavior. Candidate effects include:

- shorter initial development cycles
- shorter debug/correction loops
- faster modification of requirements and output behavior
- reduced translation between domain expert and programmer
- reduced bespoke implementation for capabilities the model already possesses
- lower cost of experimentation
- easier exploration of alternate application behavior

These are hypotheses to be measured, not assumed benefits.

## The durability problem

Conversational development introduces a source-of-truth problem. Behavior can emerge from multiple sources:

- the original development conversation
- examples and counterexamples
- explicit rules
- corrections
- persistent instructions or memory
- model capabilities and interpretation
- generated code or artifacts
- behavior that was never explicitly requested but appeared in one generation

Therefore a central DbI research problem is:

> What must be preserved so that another capable system can reconstruct the intended application with acceptable behavioral fidelity?

## The behavioral portability hypothesis

Early cross-platform reconstruction experiments suggest a stronger possibility than recovery within one AI environment: a durable package may preserve enough governed intent for a different AI platform to reconstruct recognizably equivalent application behavior using a different implementation mechanism.

The proposed invariant is therefore **behavior**, not source code or runtime structure.

A candidate portability path is:

`conversational development → governed behavioral contract → durability package → different AI platform → platform-selected implementation → validated application behavior`

Under this hypothesis, the durable asset is the application's governed behavioral contract: intent, constraints, examples, acceptance criteria, tests, provenance, and evidence. Generated code, skills, workflows, prompts, and integrations may be deployment artifacts selected or recreated by the receiving AI system.

This is provisionally termed **behavioral portability** or **intent portability**. If repeated experiments support it across more complex applications, durability packages could function as an AI-native application portability layer: applications would be migrated by reconstructing validated behavior rather than by porting a particular implementation.

This remains a research hypothesis. Current evidence does not establish exact equivalence, deterministic portability, or suitability for transactional, regulated, safety-critical, or high-assurance systems.

## The generation-artifact hypothesis

A failed reconstruction does not automatically prove that a derived specification omitted information from the original conversation. At least three explanations exist:

1. the conversation contained the behavior and the derived artifact omitted it;
2. the derived artifact contained the behavior but the reconstructing model failed to execute it;
3. neither contained the behavior because it was an accidental artifact of the original generation.

Experiments should distinguish these cases wherever possible.

## Scope

Development by Intent is most plausible for applications whose value is dominated by language understanding, research, synthesis, classification, transformation, planning, judgment, and flexible output rather than strict deterministic computation or safety-critical control.

Determining the actual boundary is part of the project.
