# Open questions

## For mentors (Sat morning)
- [ ] What counts as "using" Velocity for judging?
- [ ] What are the judging criteria and weights? Pitch length? Does the demo have to be live?
- [ ] What do real client BOM and warranty files look like? (We'll say a mentor confirmed the format.)
- [ ] Are LLM APIs allowed?
- [ ] Does the submission need a public repo?

## For us (decide tonight)
- [x] Who owns 🛠 Warranty and who owns 💲 Spend? → Brandon / Asher
- [ ] Visual style for the app (colors, font, component set)
- [ ] Does the submission need a live URL? (If so, deploy: Vercel for web/, Railway or Render for api/)
- [x] Which LLM API for the brief, and who has a key? → Claude, pinned `claude-sonnet-5-5` (`.env.example`), Brandon has the key
- [ ] Fictional company name and the 3 products

## Accounting (🛠, research running Sat AM, see docs/research/warranty-accounting.md)
- [ ] Verify the accounting-standard references (ASC 460 / 606, ASC 460 rollforward + XBRL payments tag, IAS 37 "virtually certain", ASC 450-30 recoveries, campaigns reserved separately, goodwill not recoverable)
- [ ] Spend-side accounting factors that change "true cost" (PPV, landed cost, rebates, FX, transfer prices) and which could double count with warranty
- [ ] Are supplier warranty terms, `claim_type`, in-service date and serial-to-batch traceability realistically available in enterprise systems? Decides cp0-proposal item 21g
- [ ] CP2 with Asher: `products.net_price` (21a), double-count rule (21b), `claim_type` (21c)
