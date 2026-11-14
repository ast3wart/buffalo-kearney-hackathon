# Data sources and calibration

No dataset was provided, so we **generate** one and calibrate it to real public numbers.

## Verified sources (tested Nov 13)
### SEC company filings: real warranty spend ✅
- US public companies report warranty payments in their filings (XBRL tag `ProductWarrantyAccrualPayments`).
- `python scripts/fetch_sec_warranty.py 2024` → `data/reference/sec_warranty_2024.csv`
- **2024 results:** 217 companies report warranty payments. Median ≈ **0.6% of revenue**, but equipment and vehicle makers run much higher:

| Company | Warranty paid (2024) | % of revenue |
|---|---|---|
| Ford | $5.83B | 3.15% |
| CNH Industrial | $570M | 2.87% |
| **Polaris** | in file | **2.56%** |
| Cummins | $704M | 2.06% |
| Caterpillar | $824M | 1.27% |

- **Calibration:** our fictional utility-vehicle maker spends **~2.5% of revenue on warranty**, matching Polaris.
- Caveat: revenue is matched from the first available revenue tag, so double-check any single number before putting it on a slide.

### NHTSA vehicle complaints: real failure patterns ✅
- `https://api.nhtsa.gov/complaints/complaintsByVehicle?make=TOYOTA&model=CAMRY&modelYear=2020`
- Example: 2020 Camry has 276 complaints. Electrical 68, engine 60, airbags 49, fuel/propulsion 37, powertrain 33.
- Use: shape the **mix of failure systems** in generated claims so it isn't uniform random.
- Note: some make/model strings return 0 results (e.g. FORD F-150), so try variants.

## To check by hand (Role A, about 20 min)
- **Spare-part markups:** pick 5–10 common parts (bearing, seal kit, filter, belt). Compare an OEM parts-store price to a general distributor price. Record them in `data/reference/spare_markups.csv` (part, oem_price, distributor_price, source_url). This backs up the 2–5× claim.

## Realism checklist for the generator
- [ ] Part descriptions in ERP shorthand (`BRG,BALL,6204-2RS`), supplier descriptions in plain words
- [ ] Units of measure vary (EA vs BX10), and prices are per unit of measure
- [ ] About 40% of parts are shared across products
- [ ] Spare-part prices are 1.5–5× production prices for the same part
- [ ] `causal_part_no` is blank about 60% of the time, wrong about 10%
- [ ] Claim text has typos and abbreviations (`hyd`, `cyl`, `brg`, `repl`)
- [ ] Failure-system mix follows the NHTSA-style distribution
- [ ] **One planted spike:** a shared part from one supplier, 3× claim rate from a given build month, across all products that use it
- [ ] Total warranty cost ≈ 2.5% of (units × price)
