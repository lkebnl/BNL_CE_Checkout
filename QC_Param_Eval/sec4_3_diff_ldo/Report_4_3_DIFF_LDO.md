# FEMB QC Parameter Evaluation - Report Section 4.3: DIFF LDO Measurement

**Board version:** FEMB-IO 1826-1L  
**Boards used:** 44 (latest passing test per board; excluded: 00046)  
**Test period:** 2026-07-27 23:48 - 2026-10-15 17:19  
**Generated:** 2026-10-16 16:37  
**Script:** `eval_4_3_diff_ldo.py`

## 1. Scope

Section 4.3 of the per-board checkout report lists the outputs of the 11 on-board LDO / monitor points, read in mV by the board monitor ADC while the FEMB is in the DIFF configuration (same configuration as 4.1 / 4.2). It is the second LDO block in the CSV (the first is 3.3, SE OFF). One value per board per point; all 11 are evaluated, using the values as reported in the CSV.

| Parameter | Description |
|---|---|
| `CDVDDA` – COLDATA VDDA | COLDATA analog supply |
| `CDVDDIO_HALF` – COLDATA VDDIO | COLDATA I/O supply |
| `ADCRVDDD1P2` – ADC-R VDDD 1.2V | Right-side ColdADC digital 1.2 V supply |
| `ADCLVDDD1P2` – ADC-L VDDD 1.2V | Left-side ColdADC digital 1.2 V supply |
| `FERVDDP` – FE-R VDDP | Right-side LArASIC supply |
| `FELVDDP` – FE-L VDDP | Left-side LArASIC supply |
| `ADCRP25V_1_HALF` – ADC-R 2.5V #1 | Right-side ColdADC 2.5 V supply #1 |
| `ADCLP25V_1_HALF` – ADC-L 2.5V #1 | Left-side ColdADC 2.5 V supply #1 |
| `ADCRP25V_HALF` – ADC-R 2.5V | Right-side ColdADC 2.5 V main supply |
| `ADCLP25V_HALF` – ADC-L 2.5V | Left-side ColdADC 2.5 V main supply |
| `GND` – Ground | Ground reference reading of the monitor ADC |

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
| CDVDDA | core | 1185.1 mV | 1.9 | 1179.0 | 1189.0 | 9 | 43 | 1 | 0 | 0 | 00051 (WARN 3.2σ) |
| CDVDDIO_HALF | core | 2232.1 mV | 5.4 | 2220.0 | 2242.0 | 19 | 44 | 0 | 0 | 0 | – |
| ADCRVDDD1P2 | core | 1097.8 mV | 1.7 | 1094.0 | 1101.0 | 8 | 44 | 0 | 0 | 0 | – |
| ADCLVDDD1P2 | core | 1097.7 mV | 1.8 | 1094.0 | 1101.0 | 8 | 44 | 0 | 0 | 0 | – |
| FERVDDP | core | 1665.5 mV | 2.4 | 1657.0 | 1670.0 | 10 | 43 | 1 | 0 | 0 | 00034 (WARN 3.5σ) |
| FELVDDP | core | 1665.2 mV | 2.8 | 1656.0 | 1670.0 | 11 | 43 | 1 | 0 | 0 | 00013 (WARN 3.3σ) |
| ADCRP25V_1_HALF | core | 2252.9 mV | 5.7 | 2242.0 | 2265.0 | 19 | 44 | 0 | 0 | 0 | – |
| ADCLP25V_1_HALF | core | 2250.6 mV | 4.8 | 2241.0 | 2260.0 | 19 | 44 | 0 | 0 | 0 | – |
| ADCRP25V_HALF | core | 2252.0 mV | 5.3 | 2237.0 | 2263.0 | 19 | 44 | 0 | 0 | 0 | – |
| ADCLP25V_HALF | core | 2251.8 mV | 5.0 | 2239.0 | 2265.0 | 17 | 44 | 0 | 0 | 0 | – |
| GND | core | 33.2 mV | 2.9 | 27.0 | 38.0 | 12 | 44 | 0 | 0 | 0 | – |

### Criteria (limits)

| Parameter | Unit | −7σ | −5σ | −3σ | Mean | +3σ | +5σ | +7σ |
|---|---|---|---|---|---|---|---|---|
| CDVDDA | mV | 1171.7 | 1175.5 | 1179.4 | 1185.1 | 1190.9 | 1194.8 | 1198.6 |
| CDVDDIO_HALF | mV | 2194.2 | 2205.0 | 2215.8 | 2232.1 | 2248.3 | 2259.1 | 2270.0 |
| ADCRVDDD1P2 | mV | 1085.8 | 1089.2 | 1092.7 | 1097.8 | 1103.0 | 1106.4 | 1109.9 |
| ADCLVDDD1P2 | mV | 1084.9 | 1088.5 | 1092.2 | 1097.7 | 1103.2 | 1106.8 | 1110.5 |
| FERVDDP | mV | 1648.4 | 1653.3 | 1658.1 | 1665.5 | 1672.8 | 1677.6 | 1682.5 |
| FELVDDP | mV | 1645.8 | 1651.3 | 1656.8 | 1665.2 | 1673.5 | 1679.0 | 1684.6 |
| ADCRP25V_1_HALF | mV | 2213.2 | 2224.5 | 2235.9 | 2252.9 | 2269.9 | 2281.3 | 2292.6 |
| ADCLP25V_1_HALF | mV | 2216.9 | 2226.5 | 2236.2 | 2250.6 | 2265.1 | 2274.7 | 2284.4 |
| ADCRP25V_HALF | mV | 2214.9 | 2225.5 | 2236.1 | 2252.0 | 2267.9 | 2278.5 | 2289.1 |
| ADCLP25V_HALF | mV | 2217.1 | 2227.0 | 2236.9 | 2251.8 | 2266.7 | 2276.7 | 2286.6 |
| GND | mV | 13.1 | 18.9 | 24.6 | 33.2 | 41.9 | 47.6 | 53.4 |

## 4. Parameters

### 4.1 COLDATA VDDA (`CDVDDA`)

COLDATA analog supply.  
Mean = 1185.1 mV, σ = 1.9 mV, range [1179.0, 1189.0], 9 distinct values over 44 boards.

| FEMB SN | Value | Deviation | Level |
|---|---|---|---|
| BNL_FEMB_IO-1826-1L_00051 | 1179.0 mV | 3.2σ | **WARN** |

![CDVDDA](output/plot_4_3_CDVDDA.png)

### 4.2 COLDATA VDDIO (`CDVDDIO_HALF`)

COLDATA I/O supply.  
Mean = 2232.1 mV, σ = 5.4 mV, range [2220.0, 2242.0], 19 distinct values over 44 boards.

All boards within 3σ.

![CDVDDIO_HALF](output/plot_4_3_CDVDDIO_HALF.png)

### 4.3 ADC-R VDDD 1.2V (`ADCRVDDD1P2`)

Right-side ColdADC digital 1.2 V supply.  
Mean = 1097.8 mV, σ = 1.7 mV, range [1094.0, 1101.0], 8 distinct values over 44 boards.

All boards within 3σ.

![ADCRVDDD1P2](output/plot_4_3_ADCRVDDD1P2.png)

### 4.4 ADC-L VDDD 1.2V (`ADCLVDDD1P2`)

Left-side ColdADC digital 1.2 V supply.  
Mean = 1097.7 mV, σ = 1.8 mV, range [1094.0, 1101.0], 8 distinct values over 44 boards.

All boards within 3σ.

![ADCLVDDD1P2](output/plot_4_3_ADCLVDDD1P2.png)

### 4.5 FE-R VDDP (`FERVDDP`)

Right-side LArASIC supply.  
Mean = 1665.5 mV, σ = 2.4 mV, range [1657.0, 1670.0], 10 distinct values over 44 boards.

| FEMB SN | Value | Deviation | Level |
|---|---|---|---|
| BNL_FEMB_IO-1826-1L_00034 | 1657.0 mV | 3.5σ | **WARN** |

![FERVDDP](output/plot_4_3_FERVDDP.png)

### 4.6 FE-L VDDP (`FELVDDP`)

Left-side LArASIC supply.  
Mean = 1665.2 mV, σ = 2.8 mV, range [1656.0, 1670.0], 11 distinct values over 44 boards.

| FEMB SN | Value | Deviation | Level |
|---|---|---|---|
| BNL_FEMB_IO-1826-1L_00013 | 1656.0 mV | 3.3σ | **WARN** |

![FELVDDP](output/plot_4_3_FELVDDP.png)

### 4.7 ADC-R 2.5V #1 (`ADCRP25V_1_HALF`)

Right-side ColdADC 2.5 V supply #1.  
Mean = 2252.9 mV, σ = 5.7 mV, range [2242.0, 2265.0], 19 distinct values over 44 boards.

All boards within 3σ.

![ADCRP25V_1_HALF](output/plot_4_3_ADCRP25V_1_HALF.png)

### 4.8 ADC-L 2.5V #1 (`ADCLP25V_1_HALF`)

Left-side ColdADC 2.5 V supply #1.  
Mean = 2250.6 mV, σ = 4.8 mV, range [2241.0, 2260.0], 19 distinct values over 44 boards.

All boards within 3σ.

![ADCLP25V_1_HALF](output/plot_4_3_ADCLP25V_1_HALF.png)

### 4.9 ADC-R 2.5V (`ADCRP25V_HALF`)

Right-side ColdADC 2.5 V main supply.  
Mean = 2252.0 mV, σ = 5.3 mV, range [2237.0, 2263.0], 19 distinct values over 44 boards.

All boards within 3σ.

![ADCRP25V_HALF](output/plot_4_3_ADCRP25V_HALF.png)

### 4.10 ADC-L 2.5V (`ADCLP25V_HALF`)

Left-side ColdADC 2.5 V main supply.  
Mean = 2251.8 mV, σ = 5.0 mV, range [2239.0, 2265.0], 17 distinct values over 44 boards.

All boards within 3σ.

![ADCLP25V_HALF](output/plot_4_3_ADCLP25V_HALF.png)

### 4.11 Ground (`GND`)

Ground reference reading of the monitor ADC.  
Mean = 33.2 mV, σ = 2.9 mV, range [27.0, 38.0], 12 distinct values over 44 boards.

All boards within 3σ.

![GND](output/plot_4_3_GND.png)

## 5. Observations

- **BNL_FEMB_IO-1826-1L_00013**: FELVDDP 3.3σ (WARN)
- **BNL_FEMB_IO-1826-1L_00034**: FERVDDP 3.5σ (WARN)
- **BNL_FEMB_IO-1826-1L_00051**: CDVDDA 3.2σ (WARN)
- Readout resolution is coarse (≤ 10 distinct values) for: CDVDDA, ADCRVDDD1P2, ADCLVDDD1P2, FERVDDP. σ is therefore small and quantized; a minimum tolerance tied to instrument resolution should be considered before using these limits.
- Flagged boards are still included in the statistics and inflate σ; re-deriving limits without them would tighten the criteria.

## Appendix A: Per-Board Judgement

| FEMB SN | Test time | CDVDDA | CDVDDIO_HALF | ADCRVDDD1P2 | ADCLVDDD1P2 | FERVDDP | FELVDDP | ADCRP25V_1_HALF | ADCLP25V_1_HALF | ADCRP25V_HALF | ADCLP25V_HALF | GND | Worst |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BNL_FEMB_IO-1826-1L_00001 | 2026-07-28 15:21 | 0.6σ | 0.9σ | 1.8σ | 0.4σ | 1.0σ | 0.7σ | 1.9σ | 0.3σ | 0.8σ | 0.4σ | 0.8σ | PASS |
| BNL_FEMB_IO-1826-1L_00003 | 2026-07-28 15:21 | 0.6σ | 0.9σ | 1.8σ | 1.8σ | 0.6σ | 0.1σ | 0.5σ | 0.5σ | 0.4σ | 2.6σ | 1.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00004 | 2026-08-03 22:20 | 1.5σ | 2.2σ | 2.2σ | 0.9σ | 1.4σ | 0.1σ | 1.0σ | 0.3σ | 0.9σ | 0.4σ | 1.5σ | PASS |
| BNL_FEMB_IO-1826-1L_00006 | 2026-07-28 20:07 | 0.1σ | 0.9σ | 0.1σ | 0.2σ | 1.0σ | 0.7σ | 1.6σ | 0.5σ | 0.4σ | 0.8σ | 1.0σ | PASS |
| BNL_FEMB_IO-1826-1L_00007 | 2026-09-11 18:46 | 1.6σ | 0.2σ | 0.1σ | 0.9σ | 0.2σ | 0.7σ | 0.0σ | 0.3σ | 0.4σ | 1.2σ | 0.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00008 | 2026-07-28 20:24 | 2.0σ | 0.4σ | 1.3σ | 0.4σ | 0.2σ | 1.0σ | 0.9σ | 1.9σ | 0.2σ | 0.8σ | 1.0σ | PASS |
| BNL_FEMB_IO-1826-1L_00010 | 2026-07-28 00:58 | 1.0σ | 0.2σ | 0.7σ | 1.8σ | 0.6σ | 1.1σ | 0.5σ | 0.3σ | 0.0σ | 1.2σ | 1.0σ | PASS |
| BNL_FEMB_IO-1826-1L_00012 | 2026-07-29 22:28 | 1.0σ | 0.2σ | 0.5σ | 0.4σ | 0.2σ | 0.3σ | 1.4σ | 1.5σ | 1.9σ | 0.8σ | 2.2σ | PASS |
| BNL_FEMB_IO-1826-1L_00013 | 2026-07-28 14:53 | 0.1σ | 1.1σ | 0.1σ | 0.9σ | 1.4σ | **3.3σ WARN** | 1.1σ | 0.1σ | 1.1σ | 0.2σ | 0.1σ | WARN |
| BNL_FEMB_IO-1826-1L_00014 | 2026-07-28 20:07 | 1.1σ | 0.9σ | 0.1σ | 2.0σ | 0.2σ | 1.5σ | 0.9σ | 1.2σ | 0.2σ | 0.6σ | 0.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00017 | 2026-09-11 19:03 | 1.1σ | 1.1σ | 0.7σ | 0.9σ | 1.0σ | 0.3σ | 1.6σ | 1.3σ | 0.2σ | 0.0σ | 1.0σ | PASS |
| BNL_FEMB_IO-1826-1L_00019 | 2026-07-28 15:07 | 0.4σ | 0.4σ | 1.1σ | 0.2σ | 1.5σ | 1.7σ | 0.3σ | 0.3σ | 0.0σ | 0.6σ | 1.0σ | PASS |
| BNL_FEMB_IO-1826-1L_00020 | 2026-09-11 19:03 | 0.4σ | 0.0σ | 0.5σ | 0.2σ | 1.0σ | 0.8σ | 0.7σ | 0.7σ | 0.6σ | 0.2σ | 1.1σ | PASS |
| BNL_FEMB_IO-1826-1L_00021 | 2026-07-29 22:36 | 1.6σ | 0.7σ | 1.6σ | 0.9σ | 1.4σ | 1.1σ | 0.5σ | 0.8σ | 0.9σ | 0.6σ | 1.8σ | PASS |
| BNL_FEMB_IO-1826-1L_00024 | 2026-09-11 19:03 | 1.5σ | 0.4σ | 1.3σ | 0.4σ | 0.6σ | 0.7σ | 0.9σ | 0.3σ | 0.6σ | 2.6σ | 0.1σ | PASS |
| BNL_FEMB_IO-1826-1L_00026 | 2026-07-28 15:21 | 0.6σ | 0.9σ | 1.1σ | 1.8σ | 0.6σ | 0.3σ | 1.3σ | 0.5σ | 0.0σ | 1.2σ | 1.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00027 | 2026-09-11 18:46 | 0.4σ | 1.7σ | 1.1σ | 0.2σ | 1.9σ | 1.0σ | 0.7σ | 0.1σ | 0.4σ | 0.0σ | 0.4σ | PASS |
| BNL_FEMB_IO-1826-1L_00028 | 2026-07-28 00:03 | 0.1σ | 1.5σ | 0.1σ | 1.5σ | 0.2σ | 1.4σ | 0.4σ | 1.0σ | 0.6σ | 0.2σ | 0.4σ | PASS |
| BNL_FEMB_IO-1826-1L_00029 | 2026-07-28 19:55 | 0.4σ | 1.3σ | 1.1σ | 0.7σ | 0.2σ | 0.8σ | 1.7σ | 1.3σ | 0.8σ | 1.0σ | 1.0σ | PASS |
| BNL_FEMB_IO-1826-1L_00031 | 2026-07-28 00:58 | 0.1σ | 0.9σ | 0.7σ | 0.2σ | 1.5σ | 0.4σ | 1.6σ | 0.9σ | 2.8σ | 1.6σ | 0.1σ | PASS |
| BNL_FEMB_IO-1826-1L_00032 | 2026-07-28 15:36 | 0.1σ | 0.2σ | 1.1σ | 0.4σ | 0.2σ | 1.0σ | 0.5σ | 0.1σ | 1.5σ | 0.6σ | 0.4σ | PASS |
| BNL_FEMB_IO-1826-1L_00033 | 2026-09-17 22:09 | 1.1σ | 0.9σ | 0.5σ | 1.3σ | 1.5σ | 1.1σ | 1.0σ | 1.7σ | 0.6σ | 1.2σ | 0.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00034 | 2026-09-17 22:09 | 1.0σ | 1.3σ | 1.8σ | 0.2σ | **3.5σ WARN** | 1.7σ | 0.2σ | 1.2σ | 0.4σ | 1.2σ | 1.5σ | WARN |
| BNL_FEMB_IO-1826-1L_00035 | 2026-09-11 18:46 | 0.1σ | 1.5σ | 0.5σ | 0.7σ | 1.0σ | 0.1σ | 0.5σ | 2.0σ | 1.3σ | 0.2σ | 0.6σ | PASS |
| BNL_FEMB_IO-1826-1L_00037 | 2026-07-28 00:03 | 0.1σ | 1.5σ | 1.1σ | 1.5σ | 0.6σ | 0.8σ | 1.2σ | 1.3σ | 2.1σ | 0.4σ | 1.7σ | PASS |
| BNL_FEMB_IO-1826-1L_00039 | 2026-07-28 20:41 | 0.4σ | 0.0σ | 0.5σ | 0.2σ | 1.0σ | 0.1σ | 1.1σ | 0.8σ | 1.1σ | 2.2σ | 0.8σ | PASS |
| BNL_FEMB_IO-1826-1L_00040 | 2026-07-28 20:41 | 1.1σ | 0.8σ | 0.1σ | 1.3σ | 0.6σ | 0.7σ | 0.3σ | 0.1σ | 1.5σ | 0.2σ | 1.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00041 | 2026-07-28 20:24 | 0.6σ | 0.2σ | 1.6σ | 0.7σ | 0.2σ | 1.1σ | 0.3σ | 1.6σ | 1.3σ | 0.6σ | 0.1σ | PASS |
| BNL_FEMB_IO-1826-1L_00044 | 2026-07-28 15:07 | 0.1σ | 0.4σ | 0.1σ | 1.8σ | 0.2σ | 0.7σ | 1.1σ | 1.8σ | 0.9σ | 1.0σ | 0.8σ | PASS |
| BNL_FEMB_IO-1826-1L_00045 | 2026-07-28 14:53 | 1.1σ | 0.2σ | 1.3σ | 0.4σ | 0.6σ | 0.3σ | 1.4σ | 0.1σ | 1.3σ | 0.4σ | 1.0σ | PASS |
| BNL_FEMB_IO-1826-1L_00047 | 2026-07-27 23:48 | 0.6σ | 1.7σ | 0.5σ | 0.4σ | 0.2σ | 0.1σ | 0.4σ | 1.0σ | 0.9σ | 0.2σ | 0.4σ | PASS |
| BNL_FEMB_IO-1826-1L_00048 | 2026-07-28 14:53 | 0.4σ | 0.9σ | 1.3σ | 1.3σ | 1.0σ | 1.1σ | 0.0σ | 0.3σ | 1.5σ | 0.2σ | 0.4σ | PASS |
| BNL_FEMB_IO-1826-1L_00049 | 2026-07-28 19:55 | 1.1σ | 1.7σ | 0.5σ | 0.9σ | 0.6σ | 0.3σ | 0.0σ | 1.4σ | 0.8σ | 1.2σ | 0.4σ | PASS |
| BNL_FEMB_IO-1826-1L_00051 | 2026-10-15 17:19 | **3.2σ WARN** | 0.5σ | 0.5σ | 2.0σ | 1.0σ | 0.3σ | 1.2σ | 1.6σ | 0.6σ | 0.2σ | 1.5σ | WARN |
| BNL_FEMB_IO-1826-1L_00053 | 2026-07-28 15:36 | 1.0σ | 0.7σ | 1.1σ | 0.7σ | 0.6σ | 0.4σ | 1.6σ | 0.1σ | 0.0σ | 0.2σ | 0.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00054 | 2026-07-28 00:58 | 1.0σ | 0.5σ | 0.5σ | 1.5σ | 0.2σ | 0.4σ | 0.5σ | 0.7σ | 0.0σ | 0.8σ | 1.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00055 | 2026-07-28 00:58 | 0.1σ | 0.2σ | 0.7σ | 0.4σ | 1.5σ | 1.1σ | 2.1σ | 0.7σ | 1.3σ | 1.2σ | 0.1σ | PASS |
| BNL_FEMB_IO-1826-1L_00056 | 2026-07-28 20:24 | 0.4σ | 1.7σ | 0.1σ | 1.3σ | 0.2σ | 1.0σ | 0.0σ | 0.7σ | 1.5σ | 1.6σ | 1.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00057 | 2026-07-28 15:07 | 1.5σ | 0.0σ | 0.1σ | 0.4σ | 0.6σ | 0.7σ | 0.5σ | 0.1σ | 0.2σ | 0.4σ | 1.3σ | PASS |
| BNL_FEMB_IO-1826-1L_00058 | 2026-09-17 22:09 | 1.0σ | 0.7σ | 1.8σ | 0.2σ | 0.6σ | 1.7σ | 0.2σ | 0.1σ | 0.0σ | 0.2σ | 0.4σ | PASS |
| BNL_FEMB_IO-1826-1L_00059 | 2026-08-03 18:53 | 0.4σ | 1.8σ | 0.1σ | 0.7σ | 0.2σ | 0.3σ | 0.7σ | 1.7σ | 0.8σ | 0.8σ | 0.4σ | PASS |
| BNL_FEMB_IO-1826-1L_00061 | 2026-10-09 17:53 | 0.4σ | 0.5σ | 1.3σ | 0.7σ | 0.6σ | 1.1σ | 0.0σ | 0.9σ | 0.0σ | 1.0σ | 2.2σ | PASS |
| BNL_FEMB_IO-1826-1L_00062 | 2026-07-27 23:48 | 0.6σ | 0.5σ | 0.1σ | 0.4σ | 0.6σ | 0.4σ | 0.2σ | 0.5σ | 0.6σ | 0.6σ | 0.1σ | PASS |
| BNL_FEMB_IO-1826-1L_00063 | 2026-07-28 19:55 | 1.0σ | 1.1σ | 0.5σ | 0.4σ | 0.2σ | 0.4σ | 1.4σ | 1.2σ | 0.9σ | 0.6σ | 0.3σ | PASS |

## Appendix B: Output Files

- `output/criteria_4_3.csv` – mean, σ and 3σ/5σ/7σ limits per parameter
- `output/judgement_4_3.csv` – value, deviation and level per board per parameter
- `output/plot_4_3_*.png` – distribution plots
