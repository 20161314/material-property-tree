# Current project user-authorized research policy

Applies to the object/material project identified in SKILL.md. These later user decisions override older clauses in this skill or project references where they conflict. They do not grant publication rights, invent source facts, or establish completion.

## Material labels and physical values are different evidence products

- Preserve an author's explicit material at its supported granularity. Never upgrade wood to oak, metal to an alloy grade, or generic glass to a named formulation without supporting identity evidence.
- When no object-specific material document exists, admit a reasonable broad material option for a source-enumerated object or component. Mark it as user-authorized semantic approximation, with the source UID, object role, basis, scope and reviewer. Lack of a dedicated category/material paper alone is not a reason for HOLD.
- A source's human-verified category can support object-role classification without requiring a generic or hashed title to repeat that category. Use its concept ID, synset/definition and source version where available. Concrete author descriptions and images may expose a category mismatch; preserve both and correct only the current interpretation.
- Distinguish interchangeable plausible materials from nonexclusive local materials within a complex assembly. Do not claim that local metal/plastic possibilities describe alternative whole-object constructions. Do not enumerate combinations of incomplete material options as new geometry.
- Real plants, animals, food, carved replicas, toys, characters and visual effects need different role handling. A plastic physical proxy for a fictional character is a hypothetical materialization option, not biological composition or an author declaration.
- An unresolved physical sample may retain a source identity while its material relation is HOLD. Keep that HOLD outside accepted material links, with a specific reason. WHOLE is a whole-asset fallback, not verified internal parts.

### Dataset-native handling clarification (2026-11-19)

- For the object table, an original paper or dataset's documented material-assignment procedure is an admissible mapping basis. Preserve whether it is an author declaration, dataset rule, model/VLM output, or user-authorized semantic approximation; do not relabel these as product measurements.
- If the source represents several materials as coexisting component or surface labels, retain that dataset-native relation. Do not force those labels into a whole-object mutually exclusive option group merely because the current projection uses a `WHOLE` fallback.
- If the source provides only an object category and generated or candidate materials, a reasonable broad family label may pass as an approximate object-table relation when object role, physical plausibility, scope, and reviewer rationale are explicit. Ambiguous local scope may remain coarse; it is not automatically a HOLD. Narrow alloy, species, formulation, layer, or exact face claims still require matching source support.
- Reject or hold only concrete conflicts: impossible physical role, incompatible source identity, missing stable object identity, an unresolvable cross-object mix, or a claim stronger than the source representation. Lack of a dedicated material paper alone is not a blocker.
- This clarification does not relax numerical evidence. Model/VLM/LLM outputs, simulation inputs, solver defaults, and semantic approximations remain ineligible as E/nu/rho evidence.

## Complete and partial property evidence both remain active

- Collect complete source groups and partial source groups concurrently. Do not wait for a complete-triplet numerical milestone before preserving real single-property or two-property evidence. The user explicitly broadened this requirement.
- Complete means the source reports E, nu and rho for the same identified material/result group. Never splice unrelated rows, samples or papers into a complete group.
- Partial means one or two reported properties for an identified material/result group. Multiple independently reported groups in one document can be separate rows. Several values belonging to one group remain subresults unless the source establishes different groups.
- Per-property coverage can combine separate documents. It is not the same statistic as having a complete same-source group. Report complete groups, partial groups, covered materials, documents and independent lineages separately.
- Keep experimental conditions and definitions, including unknown conditions. Unknown conditions alone do not invalidate a real reported value for a research range. Distinguish directions, density definitions and modulus methods rather than discarding records or silently mixing them.
- A paper's reported values can be admitted on that paper's own authority even if its older citation chain is unresolved. Record its reporting role and unresolved lineage; do not claim independent experimental measurement when the paper merely compiles data.
- Numerical E/nu/rho still require real accessible source evidence. User-authorized approximate labels do not authorize generated values, default solver inputs, arbitrary simulation parameters, missing-as-zero, or numerical inheritance from a broad parent.

## Tree, counts and current working data

- Read the current working delivery summary and the published release pointer separately. A working-data receipt does not prove that GitHub has been updated. Never quote an old website count as the current working inventory.
- Research nodes may contain finer subtypes from newly found evidence even without objects. Upward subtype aggregation is allowed only along reviewed IS_A edges; deduplicate record IDs. Never copy broad ranges downward.
- Source identity, downloaded payload, globally unique geometry, real internal component, whole fallback, material option, complete group and partial group remain separate counters. A green structure check is not completion.
- Preserve frozen packages. New semantic or bilingual fixes use exact-preimage sidecars across inventory display, source relations and reviewed links. Preserve author text, source locators, hashes, access and numerical evidence.
- Refer to the current project additions: `rsi_harness/RSI_2_4_3_CATEGORY_SYNSET_DEFINITION_POLICY_2026-11-15.md` and the applicable frozen correction receipts. Do not infer source-wide perfection from a targeted audit.

## Publication boundary

### Website content clarification (2026-11-20)

Follow `rsi_harness/WEBSITE_CONTENT_POLICY.md` for public presentation. Preserve the current approved visual style; publish concise Chinese object/component/material/source summaries rather than raw database rows. Hide internal review/install codes, local paths and hashes from the interface while retaining them internally. Preserve distinctions between source labels, approximations, alternatives and style options, and retain numerical conditions needed to interpret E/nu/rho. Publication must consume approved data; hiding review fields does not promote unresolved records.

The existing publication gate still applies. Do not change incomplete flags to true or bypass a blocked gate to publish a working batch. A revised publication policy requires an explicit contract change and independent validation; report working and published state separately meanwhile.
