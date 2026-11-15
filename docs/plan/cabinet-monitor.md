# Cabinet Monitor: health-sensing hardware (theoretical prototype)

**Status:** design only (no hardware was built at the hackathon). The demo uses **simulated** readings in exactly the format this device would send (`data/seed/demo/<plant>/condition.csv`, every row `simulated = yes`). The **health model that consumes them is real code**: `xray/condition.py`.

## Why this device
The registry already knows **what** is in every cabinet (identity, lifecycle, spares). What was missing is **how healthy each part is**:
- **Newer networked drives and PLCs report their own health** (capacitor and fan life, heatsink temperature, faults). We read that over the network; no hardware needed.
- **Old parts, which are the risky, discontinued ones, report nothing.** For electronics the main aging driver and failure symptom is **heat** (capacitors and fans age faster when hot; loose connections run hot).
- **Motors** fail mechanically (bearings, alignment, load). Their condition shows up in the **motor current**, which can be measured from inside the cabinet with no sensor on the motor.

So: **one small box per cabinet** that adds thermal + current sensing and collects the self-reported diagnostics. It's not one vibration sensor per machine.

## Architecture
```
  CONTROL CABINET                                              EQUIPMENT X-RAY
  ┌──────────────────────────────────────────────┐
  │  [thermal array camera] on the door, sees all │
  │  parts; emissivity tape dots on key parts     │
  │  [ambient temp/humidity]                      │──► health score per part
  │  [split-core current clamps] on drive outputs │    (xray/condition.py)
  │  [edge MCU + 24 VDC tap] ── read-only Ethernet│      │
  │      ↳ reads drive/PLC diagnostics (EtherNet/IP│      ▼
  │        / PROFINET / Modbus, read-only)         │   status, order-by date, where to spend
  └──────────────────────────────────────────────┘
       one-way, outbound only (cellular or a DMZ gateway); never writes to the control network
```

## Bill of materials (per cabinet, estimates, to be sourced)
| Part | Example | Why | Est. cost |
|---|---|---|---|
| Thermal array camera | Melexis MLX90640 (32×24, 110° lens) or FLIR Lepton 3.5 (160×120, radiometric) | Sees every component's surface temperature at once | $60–250 |
| Edge microcontroller | ESP32-S3 (Wi-Fi/Ethernet) or Raspberry Pi CM4 for on-device processing | Reads sensors + diagnostics, sends summaries | $10–90 |
| Current sensing | 2–4 split-core CTs (e.g. SCT-013 class) on drive output phases + ADC | Motor current signature analysis (MCSA) | $15–60 |
| Ambient sensor | SHT40 temp/humidity | Temperature rise over ambient; condensation risk | $5 |
| Power | DIN-rail 24 VDC → 5 V converter (cabinets already have 24 VDC) | No new wiring | $15 |
| Enclosure + mount | Magnetic or DIN mount, IP54 | Survives the cabinet | $20 |
| **Total hardware** | | | **~$125–440** |

Rough comparison (estimates, to be sourced): a wireless vibration sensor program is priced **per machine per year**, and an inspection service is priced **per visit**. One Cabinet Monitor covers a whole cabinet (5–20 parts). It's worth installing only where the "where to spend" math says the line-stop exposure justifies it. **Everywhere else, a thermal photo on the walkthrough is enough.**

## What each sensor contributes to the health score
| Evidence | What the device sends | How the model uses it | Weight |
|---|---|---|---|
| Self-reported diagnostics (newer parts) | capacitor life used, fan life used, heatsink °C, run hours, faults (12 mo) | Life used taken **at face value**; faults lower health | highest |
| Plant records | install year (from CMMS work orders / purchase orders) | Real age | medium |
| Label date code (from the photo) | manufacture year | Age **floor** when there are no records | low |
| Thermal camera | per-part °C (mapped to parts using the registry + label photo), ambient °C | **Heat aging:** life roughly halves per +10 °C above the design point (datasheet rule of thumb). **Anomalies:** see below | medium; continuous > one-time snapshot |
| Current clamps | daily load-normalized RMS current + sideband energy | Mahalanobis distance from the drive's own baseline | low–medium |

## Statistical anomaly detection (`xray/anomaly.py`)
The device sends one summary per part per day. A 30-day baseline teaches each part its normal behavior; then:
| Detector | Catches | Alarm |
|---|---|---|
| Expected temperature: OLS of (temp − ambient) on load | Removes hot days and busy shifts, leaving the residual | (model) |
| EWMA chart on residuals (λ 0.2, 3σ) | Sudden shift (a fan dies) | above the limit all of the last 7 days |
| CUSUM on residuals (k 0.5σ, h 5σ) | Slow drift (capacitors aging, a connection loosening) | above 5 all of the last 7 days |
| Trend test (OLS slope of residuals) | Steady warming, °C/month | ≥ 1 °C/month and t > 3 |
| Robust z vs identical parts (median/MAD) | One part running hotter than the same model elsewhere | z > 3 |
| Mahalanobis on current features | Motor bearing / alignment / load change | d > 3 |

Each detector gives a severity 0–1 (0 at the alarm, rising toward 1). The part's **anomaly severity is the max**, and **45 × severity** health points come off the wear score. Results on the simulated demo: all 4 planted patterns caught (severity ≥ 0.98); 2 of the other 125 parts flagged. One is real: self-reported fan 97% used *and* running hot against peers. The other is a false alarm (about 1 in 40 monitored series, consistent with these SPC settings). Thresholds are standard SPC defaults; calibrate in the pilot.

**Output per part:** health 0–100, remaining-life range (years), confidence (high / medium / low, from which evidence exists), and the **drivers** in plain words ("22 °C hotter than identical parts: fan or connection problem?").

## Installation and safety
- Installed by the plant's electrician during a planned stop (lockout/tagout). Clamp-on sensors only: no rewiring of the control circuit.
- **Read-only:** never writes to PLCs or drives. Outbound-only connection (cellular or the plant's DMZ), so it doesn't open a path into the control network.
- Thermal camera on the door's inside: no line of sight issues with the door closed (normal operation).

## Honest limits
- Gives **risk and remaining-life ranges**, not exact failure dates. Sudden electronic failures with no heat signature still happen, so **spares and sourcing still matter** (that's the rest of the product).
- Temperature history before installation is unknown: the model counts only part of today's extra heat for the past (`xray/condition.py`).
- Thermal reads surfaces: shiny metal needs emissivity tape; parts hidden behind others need a second camera angle.

## Validation plan (after the hackathon)
1. Pilot on 10 line-stopper cabinets in one portfolio plant for 90 days.
2. Compare health scores with what the maintenance team finds (fans, capacitors, connections) and with failures.
3. Calibrate the thresholds (anomaly °C, fault penalty, current index) and the design-point temperatures per part family.
4. Fleet learning: identical parts across many plants give the baseline. This only exists because we work across PE portfolios.
