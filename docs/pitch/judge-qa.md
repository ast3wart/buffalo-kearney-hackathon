# Judge questions to prep

| Question | Answer sketch |
|---|---|
| There was no data. Isn't this all fake? | Generated data with **planted correct answers**, so accuracy is measurable. It's calibrated to SEC and NHTSA numbers. The input format matches ERP flat-file exports, so it runs on a client's real exports. |
| Isn't it just tuned to your own fake data? | Three companies with different industries, noise levels, and part mixes. We tuned on one and report accuracy on the other two. The third has no planted problem, and the tool correctly raises no alerts. |
| Why match at all if SAP POs carry the material number? | At the main plant they mostly do. The hard cases are acquired plants on legacy systems, service purchases typed as free text, and warranty claims, which never carry a PO. Ironridge shows all three. |
| How do you know it's that supplier and not the other one? | The part is dual-sourced, and lot records show which supplier's batch each build used. Claims jump only on builds using Supplier A's lots from a specific PO, not Supplier B's. With serial-to-batch traceability, attribution becomes exact. |
| Can it read a real client extract? | Ironridge arrives as a raw SAP extract (EKPO/EKKO/LFA1/MARA field names, zero-padded numbers, YYYYMMDD dates). An adapter maps it on load, and nothing else changes. No live connector needed for a diagnostic. |
| Could the AI be making up numbers? | Every number in the brief comes from the results database, and a test checks it. AI only proposes tie-breaks, measured against the answer key. |
| What if a claim can't be matched? | It drops into a low-confidence bucket for human review. We report coverage honestly. |
| How is the spike not just noise? | Claims are pooled across products and normalized per 1,000 units built, with a minimum claim count. We show the planted spike is caught and report false alarms. |
| Does this scale to millions of rows? | Matching is narrowed by product BOM and category first. Fuzzy matching only runs on a few candidates, and the LLM only on ties. |
| Why doesn't SAP or a warranty tool already do this? | Warranty tools stay inside the service team. Procurement tools don't see claims. The link between them is the gap (see Velocity market research). |
| How sure are the savings? | Spare-part overspend is a direct price comparison. Warranty $ are **recovery opportunities**: linked claim cost × a 25–50% **scenario** capture rate, shown as a range. We never claim a supplier owes it. |
| So you're saying the supplier is at fault? | No. Afterlife links claims to a **candidate** part and supplier with a confidence score. Fault depends on returned-part analysis, engineering review, and the supply contract. We produce the evidence pack that starts that review. |
| Suppliers only pay ~10% of warranty. Isn't the gap to 37% huge? | Warranty Week's 37% is a hypothetical ceiling based on share of sales, not proof of fault, so we don't claim it. Our pitch is speed and evidence: finding the right cases to review, early. |
| What doesn't your tool handle? | Contract terms, returned-part test results, and dispute workflow. A next step would be a small supplier-terms table (recovery clause, cost-share %) so briefs reflect what each contract allows. |
| How would Kearney use this? | As a week-1 diagnostic in a cost or aftermarket engagement, replacing weeks of manual Excel matching. |
