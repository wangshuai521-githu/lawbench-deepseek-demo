# Changelog

This file tracks all changes and updates to LegalBench data.
## March 29, 2026

### MAUD passage mismatches (7 tasks)

The ~40 MAUD tasks in LegalBench are derived from the [Atticus Project MAUD dataset](https://zenodo.org/records/6553578), which contains merger agreement excerpts annotated with answers to 92 legal questions. Each LegalBench MAUD task corresponds to one MAUD question: the model reads a merger agreement passage and selects the best answer from a set of multiple-choice options.

We identified 7 tasks where passages were incorrectly assigned to the wrong MAUD questions during the original dataset construction. 

We re-extracted the correct passages from the raw MAUD train/dev/test CSVs, filtering to `data_type="main"` and mapping each MAUD answer to the corresponding LegalBench option letter. The affected tasks are:

- `maud_knowledge_definition`
- `maud_liability_standard_for_no-shop_breach_by_target_non-do_representatives`
- `maud_definition_contains_knowledge_requirement_-_answer`
- `maud_intervening_event_-_required_to_occur_after_signing_-_answer`
- `maud_definition_includes_stock_deals`
- `maud_definition_includes_asset_deals`
- `maud_accuracy_of_target_capitalization_rw_(outstanding_shares)_bringdown_standard_answer`

### OPP-115 segment upgrade (all 9 tasks)

The 9 OPP-115 tasks are derived from the [OPP-115 corpus](https://usableprivacy.org/data), which contains 115 website privacy policies with expert annotations. Each policy is divided into segments (delimited by `|||` in the source HTML), and annotators highlighted specific text spans within segments and tagged them with categories (e.g., Data Retention, Data Security) and attributes. Each LegalBench OPP-115 task asks: "Does this clause describe [category]?" (Yes/No).

The original LegalBench construction used the short `selectedText` spans from annotations as the input clauses. These spans had a median length of only 31 characters — many were too short to reason about in isolation (e.g., the 9-character span `"including"` was a positive example for First Party Collection/Use). Additionally, `opp115_data_retention` used spans from all annotation attributes (including "Personal Information Type" spans like "your email address") rather than just retention-relevant attributes, causing 61% of "Yes" examples to have no retention content.

Instead of using the short `selectedText` spans, we now use the full `|||`-delimited segment (natural paragraph) containing the annotation as the input clause. Segments have a median length of ~570 characters, providing sufficient context for the classification task. A segment is labeled "Yes" for a category if any annotation of that category falls within it, and "No" if it has annotations for other (non-Other) categories but not the target category. Test sets are class-balanced by downsampling the majority class. The affected tasks are:

- `opp115_data_retention`
- `opp115_data_security`
- `opp115_do_not_track`
- `opp115_first_party_collection_use`
- `opp115_international_and_specific_audiences`
- `opp115_policy_change`
- `opp115_third_party_sharing_collection`
- `opp115_user_access,_edit_and_deletion`
- `opp115_user_choice_control`

## June 30, 2024

- We have removed the `train.tsv` files for `scalr` and `rule_qa`. Both these tasks were intended to be zero-shot and hence have no samples in their `train.tsv` files. We have removed these files to avoid any confusion.
- We noticed an error in `unfair_tos` whereby labels were not correctly assigned for some samples. We have fixed this issue and uploaded a new version of the data with corrected labels.
