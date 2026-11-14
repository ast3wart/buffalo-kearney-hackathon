# Schedule

Threads: 🛠 Warranty / 💲 Spend. Owners are in [../team/roles.md](../team/roles.md).

| When | 🛠 Warranty | 💲 Spend |
|---|---|---|
| **Fri night** | Together: primer, data contract, API contract, app layout and style (≈1 h). Then start `match_claims` on `data/sample/` | Together (same). Then start `generate_spend` |
| **Sat 9–12:30** | `match_claims` + `detect` on sample data. `/alerts` endpoint | `generate_spend` done. `match_spend` + unit conversion. `/overview` endpoint |
| **Sat 12:30** | 🔗 **Integration #1:** run on generated spend data. Warranty starts `generate_claims` against the real BOM | |
| **Sat 1:30–6** | `generate_claims` with the spike. Early-warning screen + chart. **Stop tuning matching at 5** | `cost` + markups. Overview screen. `/markups` |
| **Sat 6 PM** | 🔗 **Integration #2:** full `afterlife.run` on generated data. Both screens live | |
| **Sat 7–10** | Brief warranty section. Linking explorer (shared) | Brief pricing section. `POST /brief` + Brief screen (shared) |
| **Sat 10 PM** | 🧊 **Feature freeze** | |
| **Sat night** | Velocity 2/4/5. Accuracy slide | Velocity 3/6/7. Deck. Practice ×2 |
| **Sun AM** | Backup demo video. **Submit by 8:30** | |
