# FEMB QC Parameter Evaluation - Report Section 3.2: SE OFF Power Measurement

**Board version:** FEMB-IO 1826-1L  
**Boards used:** 44 (latest passing test per board; excluded: 00046)  
**Test period:** 2026-07-27 23:48 - 2026-10-15 17:19  
**Generated:** 2026-10-16 16:37  
**Script:** `eval_3_2_se_off_power.py`

## 1. Scope

Section 3.2 of the per-board checkout report is the power-supply reading taken after the FEMB is configured for the SE OFF noise measurement (single-ended, SE buffer OFF, 200 mV baseline, 14 mV/fC, 2 µs). It has the same 17 numbers as section 2.1: V_set / V_meas / I_meas / P_meas for the 4 rails (BIAS, LArASIC, ColdDATA, ColdADC), plus Total Power.

| Category | Parameters | Treatment |
|---|---|---|
| Core | I_meas & V_meas of LArASIC / ColdDATA / ColdADC, Total Power (7) | Statistical judgement |
| Auxiliary | V_meas & I_meas of BIAS (2) | Shown for reference; I_BIAS ≈ 0 is better served by a fixed limit |
| Not evaluated | V_set (4) | Configuration setpoints, constant |
| Not evaluated | P_meas (4) | Redundant (P = V × I) |

## 2. Judgement Method

For each parameter, mean and standard deviation (σ) are computed over all boards; each board is graded by its deviation |x − mean| / σ.

| Level | Deviation | Plot background |
|---|---|---|
| PASS | ≤ 3σ | green |
| WARN | 3σ – 5σ | yellow |
| ALERT | 5σ – 7σ | red |
| FAIL | > 7σ | dark red |

## 3. Summary

| Parameter | Role | Mean | Std | Min | Max | N unique | PASS | WARN | ALERT | FAIL | Flagged boards |
|---|---|---|---|---|---|---|---|---|---|---|---|
| I_LArASIC | core | 0.4224 A | 0.0028 | 0.4180 | 0.4270 | 4 | 44 | 0 | 0 | 0 | – |
| I_ColdDATA | core | 0.2320 A | 0.0075 | 0.2230 | 0.2750 | 8 | 43 | 0 | 1 | 0 | 00051 (ALERT 5.7σ) |
| I_ColdADC | core | 1.5958 A | 0.0342 | 1.5260 | 1.7400 | 7 | 43 | 1 | 0 | 0 | 00031 (WARN 4.2σ) |
| V_LArASIC | core | 2.9513 V | 0.0046 | 2.9430 | 2.9570 | 11 | 44 | 0 | 0 | 0 | – |
| V_ColdDATA | core | 2.9733 V | 0.0088 | 2.9540 | 2.9800 | 10 | 44 | 0 | 0 | 0 | – |
| V_ColdADC | core | 3.4217 V | 0.0075 | 3.4080 | 3.4300 | 16 | 44 | 0 | 0 | 0 | – |
| Total_Power | core | 7.402 W | 0.113 | 7.135 | 7.862 | 36 | 43 | 1 | 0 | 0 | 00031 (WARN 4.1σ) |
| V_BIAS | aux | 4.9996 V | 0.0005 | 4.9990 | 5.0000 | 2 | 44 | 0 | 0 | 0 | – |
| I_BIAS | aux | 0.0010 A | 0.0022 | 0.0000 | 0.0060 | 3 | 44 | 0 | 0 | 0 | – |

### Criteria (limits)

| Parameter | Unit | −7σ | −5σ | −3σ | Mean | +3σ | +5σ | +7σ |
|---|---|---|---|---|---|---|---|---|
| I_LArASIC | A | 0.4027 | 0.4083 | 0.4140 | 0.4224 | 0.4309 | 0.4365 | 0.4422 |
| I_ColdDATA | A | 0.1795 | 0.1945 | 0.2095 | 0.2320 | 0.2544 | 0.2694 | 0.2844 |
| I_ColdADC | A | 1.3566 | 1.4250 | 1.4933 | 1.5958 | 1.6983 | 1.7667 | 1.8350 |
| V_LArASIC | V | 2.9193 | 2.9284 | 2.9375 | 2.9513 | 2.9650 | 2.9741 | 2.9832 |
| V_ColdDATA | V | 2.9120 | 2.9295 | 2.9470 | 2.9733 | 2.9996 | 3.0171 | 3.0346 |
| V_ColdADC | V | 3.3696 | 3.3845 | 3.3994 | 3.4217 | 3.4441 | 3.4590 | 3.4739 |
| Total_Power | W | 6.609 | 6.836 | 7.062 | 7.402 | 7.742 | 7.968 | 8.195 |
| V_BIAS | V | 4.9961 | 4.9971 | 4.9981 | 4.9996 | 5.0011 | 5.0020 | 5.0030 |
| I_BIAS | A | -0.0145 | -0.0100 | -0.0056 | 0.0010 | 0.0077 | 0.0121 | 0.0165 |

## 4. Core Parameters

### 4.1 LArASIC Current (`I_LArASIC`)

LArASIC rail current.  
Mean = 0.4224 A, σ = 0.0028 A, range [0.4180, 0.4270], 4 distinct values over 44 boards.

All boards within 3σ.

![I_LArASIC](output/plot_3_2_I_LArASIC.png)

### 4.2 ColdDATA Current (`I_ColdDATA`)

ColdDATA rail current.  
Mean = 0.2320 A, σ = 0.0075 A, range [0.2230, 0.2750], 8 distinct values over 44 boards.

| FEMB SN | Value | Deviation | Level |
|---|---|---|---|
| BNL_FEMB_IO-1826-1L_00051 | 0.2750 A | 5.7σ | **ALERT** |

![I_ColdDATA](output/plot_3_2_I_ColdDATA.png)

### 4.3 ColdADC Current (`I_ColdADC`)

ColdADC rail current.  
Mean = 1.5958 A, σ = 0.0342 A, range [1.5260, 1.7400], 7 distinct values over 44 boards.

| FEMB SN | Value | Deviation | Level |
|---|---|---|---|
| BNL_FEMB_IO-1826-1L_00031 | 1.7400 A | 4.2σ | **WARN** |

![I_ColdADC](output/plot_3_2_I_ColdADC.png)

### 4.4 LArASIC Voltage (`V_LArASIC`)

LArASIC rail voltage at the supply.  
Mean = 2.9513 V, σ = 0.0046 V, range [2.9430, 2.9570], 11 distinct values over 44 boards.

All boards within 3σ.

![V_LArASIC](output/plot_3_2_V_LArASIC.png)

### 4.5 ColdDATA Voltage (`V_ColdDATA`)

ColdDATA rail voltage at the supply.  
Mean = 2.9733 V, σ = 0.0088 V, range [2.9540, 2.9800], 10 distinct values over 44 boards.

All boards within 3σ.

![V_ColdDATA](output/plot_3_2_V_ColdDATA.png)

### 4.6 ColdADC Voltage (`V_ColdADC`)

ColdADC rail voltage at the supply.  
Mean = 3.4217 V, σ = 0.0075 V, range [3.4080, 3.4300], 16 distinct values over 44 boards.

All boards within 3σ.

![V_ColdADC](output/plot_3_2_V_ColdADC.png)

### 4.7 Total Power (`Total_Power`)

Sum of rail powers.  
Mean = 7.402 W, σ = 0.113 W, range [7.135, 7.862], 36 distinct values over 44 boards.

| FEMB SN | Value | Deviation | Level |
|---|---|---|---|
| BNL_FEMB_IO-1826-1L_00031 | 7.862 W | 4.1σ | **WARN** |

![Total_Power](output/plot_3_2_Total_Power.png)

## 5. Auxiliary Parameters

### 5.1 BIAS Voltage (`V_BIAS`)

BIAS rail voltage.  
Mean = 4.9996 V, σ = 0.0005 V, range [4.9990, 5.0000], 2 distinct values over 44 boards.

All boards within 3σ.

![V_BIAS](output/plot_3_2_V_BIAS.png)

### 5.2 BIAS Current (`I_BIAS`)

BIAS rail current (≈ 0).  
Mean = 0.0010 A, σ = 0.0022 A, range [0.0000, 0.0060], 3 distinct values over 44 boards.

All boards within 3σ.

![I_BIAS](output/plot_3_2_I_BIAS.png)

## 6. Observations

- **BNL_FEMB_IO-1826-1L_00031**: I_ColdADC 4.2σ (WARN); Total_Power 4.1σ (WARN)
- **BNL_FEMB_IO-1826-1L_00051**: I_ColdDATA 5.7σ (ALERT)
- Readout resolution is coarse (≤ 10 distinct values) for: I_LArASIC, I_ColdDATA, I_ColdADC, V_ColdDATA. σ is therefore small and quantized; a minimum tolerance tied to instrument resolution should be considered before using these limits.
- Flagged boards are still included in the statistics and inflate σ; re-deriving limits without them would tighten the criteria.

## Appendix A: Per-Board Judgement (core parameters)

| FEMB SN | Test time | I_LArASIC | I_ColdDATA | I_ColdADC | V_LArASIC | V_ColdDATA | V_ColdADC | Total_Power | Worst |
|---|---|---|---|---|---|---|---|---|---|
| BNL_FEMB_IO-1826-1L_00001 | 2026-07-28 15:21 | 1.6σ | 0.0σ | 0.3σ | 0.3σ | 0.5σ | 0.7σ | 0.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00003 | 2026-07-28 15:21 | 0.6σ | 0.4σ | 0.3σ | 0.6σ | 2.1σ | 0.8σ | 0.0σ | PASS |
| BNL_FEMB_IO-1826-1L_00004 | 2026-08-03 22:20 | 1.6σ | 0.0σ | 1.2σ | 1.0σ | 0.3σ | 1.1σ | 1.0σ | PASS |
| BNL_FEMB_IO-1826-1L_00006 | 2026-07-28 20:07 | 0.6σ | 0.4σ | 1.2σ | 0.4σ | 2.1σ | 0.4σ | 1.1σ | PASS |
| BNL_FEMB_IO-1826-1L_00007 | 2026-09-11 18:46 | 0.5σ | 0.0σ | 1.2σ | 1.6σ | 0.7σ | 1.2σ | 1.4σ | PASS |
| BNL_FEMB_IO-1826-1L_00008 | 2026-07-28 20:24 | 0.5σ | 0.4σ | 1.2σ | 1.6σ | 0.7σ | 1.4σ | 1.5σ | PASS |
| BNL_FEMB_IO-1826-1L_00010 | 2026-07-28 00:58 | 0.5σ | 1.2σ | 0.6σ | 1.8σ | 0.4σ | 1.7σ | 0.6σ | PASS |
| BNL_FEMB_IO-1826-1L_00012 | 2026-07-29 22:28 | 0.6σ | 0.4σ | 0.3σ | 1.3σ | 0.3σ | 1.1σ | 0.1σ | PASS |
| BNL_FEMB_IO-1826-1L_00013 | 2026-07-28 14:53 | 1.6σ | 1.2σ | 1.2σ | 0.8σ | 0.4σ | 0.8σ | 1.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00014 | 2026-07-28 20:07 | 0.5σ | 0.4σ | 0.3σ | 1.0σ | 0.2σ | 0.7σ | 0.2σ | PASS |
| BNL_FEMB_IO-1826-1L_00017 | 2026-09-11 19:03 | 0.5σ | 0.8σ | 0.6σ | 1.6σ | 0.7σ | 1.4σ | 0.5σ | PASS |
| BNL_FEMB_IO-1826-1L_00019 | 2026-07-28 15:07 | 0.5σ | 0.0σ | 0.3σ | 1.8σ | 0.5σ | 1.6σ | 0.5σ | PASS |
| BNL_FEMB_IO-1826-1L_00020 | 2026-09-11 19:03 | 0.5σ | 0.0σ | 0.6σ | 0.3σ | 0.5σ | 0.8σ | 0.7σ | PASS |
| BNL_FEMB_IO-1826-1L_00021 | 2026-07-29 22:36 | 0.6σ | 0.4σ | 0.6σ | 1.0σ | 0.4σ | 1.0σ | 0.7σ | PASS |
| BNL_FEMB_IO-1826-1L_00024 | 2026-09-11 19:03 | 0.6σ | 0.0σ | 0.3σ | 0.8σ | 0.2σ | 0.7σ | 0.2σ | PASS |
| BNL_FEMB_IO-1826-1L_00026 | 2026-07-28 15:21 | 0.5σ | 0.4σ | 1.5σ | 1.6σ | 0.7σ | 1.8σ | 1.2σ | PASS |
| BNL_FEMB_IO-1826-1L_00027 | 2026-09-11 18:46 | 1.6σ | 0.4σ | 0.3σ | 0.8σ | 0.3σ | 0.7σ | 0.2σ | PASS |
| BNL_FEMB_IO-1826-1L_00028 | 2026-07-28 00:03 | 0.5σ | 0.8σ | 0.6σ | 0.3σ | 0.7σ | 0.7σ | 0.5σ | PASS |
| BNL_FEMB_IO-1826-1L_00029 | 2026-07-28 19:55 | 1.6σ | 0.4σ | 0.3σ | 1.6σ | 0.7σ | 1.3σ | 0.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00031 | 2026-07-28 00:58 | 1.6σ | 0.4σ | **4.2σ WARN** | 0.3σ | 0.5σ | 0.5σ | **4.1σ WARN** | WARN |
| BNL_FEMB_IO-1826-1L_00032 | 2026-07-28 15:36 | 0.6σ | 0.4σ | 0.6σ | 0.8σ | 0.2σ | 0.4σ | 0.6σ | PASS |
| BNL_FEMB_IO-1826-1L_00033 | 2026-09-17 22:09 | 0.5σ | 0.4σ | 2.4σ | 1.4σ | 0.7σ | 1.6σ | 2.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00034 | 2026-09-17 22:09 | 0.5σ | 0.0σ | 0.3σ | 0.1σ | 0.7σ | 0.8σ | 0.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00035 | 2026-09-11 18:46 | 0.6σ | 0.0σ | 0.6σ | 0.6σ | 2.0σ | 0.6σ | 0.8σ | PASS |
| BNL_FEMB_IO-1826-1L_00037 | 2026-07-28 00:03 | 0.5σ | 0.4σ | 0.6σ | 0.6σ | 2.2σ | 0.9σ | 0.8σ | PASS |
| BNL_FEMB_IO-1826-1L_00039 | 2026-07-28 20:41 | 0.5σ | 0.0σ | 0.3σ | 0.5σ | 0.4σ | 1.0σ | 0.2σ | PASS |
| BNL_FEMB_IO-1826-1L_00040 | 2026-07-28 20:41 | 1.6σ | 0.8σ | 0.3σ | 0.4σ | 2.1σ | 0.6σ | 0.2σ | PASS |
| BNL_FEMB_IO-1826-1L_00041 | 2026-07-28 20:24 | 0.6σ | 0.4σ | 0.3σ | 0.8σ | 0.3σ | 0.7σ | 0.2σ | PASS |
| BNL_FEMB_IO-1826-1L_00044 | 2026-07-28 15:07 | 1.6σ | 1.2σ | 0.3σ | 0.3σ | 0.7σ | 0.7σ | 0.6σ | PASS |
| BNL_FEMB_IO-1826-1L_00045 | 2026-07-28 14:53 | 0.5σ | 0.4σ | 0.3σ | 1.4σ | 0.8σ | 1.4σ | 0.6σ | PASS |
| BNL_FEMB_IO-1826-1L_00047 | 2026-07-27 23:48 | 1.6σ | 0.4σ | 0.3σ | 0.3σ | 0.7σ | 0.7σ | 0.4σ | PASS |
| BNL_FEMB_IO-1826-1L_00048 | 2026-07-28 14:53 | 0.5σ | 0.4σ | 0.3σ | 0.3σ | 0.7σ | 0.7σ | 0.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00049 | 2026-07-28 19:55 | 1.6σ | 0.0σ | 0.3σ | 0.3σ | 0.5σ | 0.7σ | 0.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00051 | 2026-10-15 17:19 | 0.5σ | **5.7σ ALERT** | 1.2σ | 0.1σ | 0.0σ | 1.0σ | 0.1σ | ALERT |
| BNL_FEMB_IO-1826-1L_00053 | 2026-07-28 15:36 | 0.6σ | 0.4σ | 0.3σ | 1.8σ | 0.7σ | 1.4σ | 0.4σ | PASS |
| BNL_FEMB_IO-1826-1L_00054 | 2026-07-28 00:58 | 1.6σ | 0.8σ | 2.0σ | 0.6σ | 2.1σ | 0.4σ | 2.4σ | PASS |
| BNL_FEMB_IO-1826-1L_00055 | 2026-07-28 00:58 | 1.6σ | 0.0σ | 0.3σ | 1.0σ | 0.2σ | 1.0σ | 0.1σ | PASS |
| BNL_FEMB_IO-1826-1L_00056 | 2026-07-28 20:24 | 0.6σ | 0.0σ | 0.6σ | 0.4σ | 2.2σ | 0.8σ | 0.8σ | PASS |
| BNL_FEMB_IO-1826-1L_00057 | 2026-07-28 15:07 | 0.6σ | 0.8σ | 0.3σ | 0.6σ | 2.0σ | 0.6σ | 0.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00058 | 2026-09-17 22:09 | 0.6σ | 0.4σ | 0.6σ | 1.0σ | 0.3σ | 0.7σ | 0.8σ | PASS |
| BNL_FEMB_IO-1826-1L_00059 | 2026-08-03 18:53 | 1.6σ | 0.4σ | 0.6σ | 1.0σ | 0.4σ | 1.0σ | 0.5σ | PASS |
| BNL_FEMB_IO-1826-1L_00061 | 2026-10-09 17:53 | 0.6σ | 0.4σ | 0.3σ | 1.3σ | 0.4σ | 1.1σ | 0.2σ | PASS |
| BNL_FEMB_IO-1826-1L_00062 | 2026-07-27 23:48 | 0.6σ | 0.4σ | 0.3σ | 1.0σ | 0.3σ | 0.8σ | 0.2σ | PASS |
| BNL_FEMB_IO-1826-1L_00063 | 2026-07-28 19:55 | 1.6σ | 0.0σ | 0.3σ | 0.8σ | 0.3σ | 0.8σ | 0.1σ | PASS |

## Appendix B: Output Files

- `output/criteria_3_2.csv` – mean, σ and 3σ/5σ/7σ limits per parameter
- `output/judgement_3_2.csv` – value, deviation and level per board per parameter
- `output/plot_3_2_*.png` – distribution plots
