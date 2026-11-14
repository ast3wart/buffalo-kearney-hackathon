# Judge questions to prep

| Question | Answer sketch |
|---|---|
| There was no data. Isn't this all fake? | Generated data with **planted correct answers**, so accuracy is measurable. It's calibrated to SEC and NHTSA numbers. The input format matches ERP flat-file exports, so it runs on a client's real exports. |
| What if a claim can't be matched? | It drops into a low-confidence bucket for human review. We report coverage honestly. |
| How is the spike not just noise? | Claims are pooled across products and normalized per 1,000 units built, with a minimum claim count. We show the planted spike is caught and report false alarms. |
| Does this scale to millions of rows? | Matching is narrowed by product BOM and category first. Fuzzy matching only runs on a few candidates, and the LLM only on ties. |
| Why doesn't SAP or a warranty tool already do this? | Warranty tools stay inside the service team. Procurement tools don't see claims. The link between them is the gap (see Velocity market research). |
| How sure are the savings? | Shown as ranges with a capture rate from published benchmarks. |
| How would Kearney use this? | As a week-1 diagnostic in a cost or aftermarket engagement, replacing weeks of manual Excel matching. |
