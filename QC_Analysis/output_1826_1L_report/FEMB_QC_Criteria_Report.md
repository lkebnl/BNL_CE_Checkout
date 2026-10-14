# FEMB QC Criteria Report

## FEMB-IO 1826-1L Quality Control Analysis

**Analysis Date:** October 2026
**Board Version:** FEMB-IO 1826-1L
**Number of Boards Analyzed:** 44
**Total Parameters:** 44
**Analysis Method:** Statistical analysis using latest passing test per board

---

## Overview

This report documents the Quality Control (QC) criteria derived from 44 FEMB-IO 1826-1L boards that passed checkout testing at BNL.

### Tolerance Methods

Different tolerance methods are used based on parameter type:

| Parameter Type | Tolerance Method | Rationale |
|----------------|------------------|-----------|
| 128-Channel (ped, rms, etc.) | 5σ | Statistical outlier detection for large datasets (5632 points) |
| 8-Chip ASIC | 5σ | Statistical outlier detection (352 points) |
| LDO Voltages | 7σ | Wider tolerance for power rail monitoring (44 points) |
| Currents | 7σ | Wider tolerance for current measurements (44 points) |
| Power | 7σ | Wider tolerance for power measurements (44 points) |

### Parameter Categories

| Category | Description | Count |
|----------|-------------|-------|
| 128-Channel | Per-channel measurements (128 ch × 44 boards = 5632 points) | 7 |
| LDO Pedestal | LDO voltage readings during pedestal check | 11 |
| LDO Pulse | LDO voltage readings during pulse check | 11 |
| Current | Power rail current measurements | 6 |
| Power | Total power measurements | 2 |
| 8-Chip ASIC | Per-ASIC measurements (8 chips × 44 boards = 352 points) | 7 |

---

## 1. 128-Channel Parameters (5σ Tolerance)

These parameters are measured for all 128 channels on each FEMB board (5632 total data points).

### 1.1 Pedestal (ped)

**Description:** The baseline ADC value when no signal is present. Represents the DC offset of each channel's readout electronics.

| Statistic | Value |
|-----------|-------|
| Mean | 911.8066 |
| Std | 104.7993 |
| Median | 903.3195 |
| Min | 576.8393 |
| Max | 1305.4897 |
| N | 5632 |

**Pass/Fail Criteria (5σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 387.8101 | 1435.8031 |

**Interpretation:** Pedestal values vary across channels due to manufacturing variations.

![Pedestal](plot_ped.png)

---

### 1.2 RMS Noise (rms)

**Description:** Root Mean Square of the baseline fluctuations. Measures the intrinsic electronic noise of each channel in ADC counts.

| Statistic | Value |
|-----------|-------|
| Mean | 11.1965 |
| Std | 0.4542 |
| Median | 11.1850 |
| Min | 9.2394 |
| Max | 13.0419 |
| N | 5632 |

**Pass/Fail Criteria (5σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 8.9255 | 13.4675 |

**Interpretation:** Lower noise is better. High RMS indicates noisy channels.

![RMS Noise](plot_rms.png)

---

### 1.3 Positive Peak (PPK_mean)

**Description:** Mean ADC value of the positive pulse response when injecting a calibration pulse.

| Statistic | Value |
|-----------|-------|
| Mean | 12747.6571 |
| Std | 94.2848 |
| Median | 12749.0000 |
| Min | 12375.0000 |
| Max | 13073.0000 |
| N | 5632 |

**Pass/Fail Criteria (5σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 12276.2331 | 13219.0811 |

**Interpretation:** Consistent PPK values indicate uniform gain.

![Positive Peak](plot_PPK_mean.png)

---

### 1.4 Negative Peak (NPK_mean)

**Description:** Mean ADC value of the negative pulse response.

| Statistic | Value |
|-----------|-------|
| Mean | 4411.5245 |
| Std | 85.6226 |
| Median | 4411.0000 |
| Min | 4143.0000 |
| Max | 4745.0000 |
| N | 5632 |

**Pass/Fail Criteria (5σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 3983.4115 | 4839.6375 |

**Interpretation:** NPK should be symmetric with PPK relative to baseline.

![Negative Peak](plot_NPK_mean.png)

---

### 1.5 Baseline (BL_mean)

**Description:** Mean baseline level during pulse response measurement.

| Statistic | Value |
|-----------|-------|
| Mean | 8579.7246 |
| Std | 70.1446 |
| Median | 8581.0000 |
| Min | 8330.0000 |
| Max | 8848.0000 |
| N | 5632 |

**Pass/Fail Criteria (5σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 8229.0016 | 8930.4476 |

**Interpretation:** Stable baseline indicates good DC performance.

![Baseline](plot_BL_mean.png)

---

### 1.6 Pedestal Max (pedmax)

**Description:** Maximum pedestal value observed during the measurement window.

| Statistic | Value |
|-----------|-------|
| Mean | 949.4876 |
| Std | 104.6585 |
| Median | 941.0000 |
| Min | 614.0000 |
| Max | 1339.0000 |
| N | 5632 |

**Pass/Fail Criteria (5σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 426.1951 | 1472.7801 |

**Interpretation:** Large pedmax-pedmin difference indicates instability.

![Pedestal Max](plot_pedmax.png)

---

### 1.7 Pedestal Min (pedmin)

**Description:** Minimum pedestal value observed during the measurement window.

| Statistic | Value |
|-----------|-------|
| Mean | 874.1628 |
| Std | 105.0868 |
| Median | 865.0000 |
| Min | 538.0000 |
| Max | 1269.0000 |
| N | 5632 |

**Pass/Fail Criteria (5σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 348.7288 | 1399.5968 |

**Interpretation:** Together with pedmax, defines pedestal variation range.

![Pedestal Min](plot_pedmin.png)

---

## 2. LDO Voltage Parameters - Pedestal (7σ Tolerance)

LDO regulator output voltages measured during pedestal check.

### 2.1 CDVDDA_ped (CDVDDA_ped)

**Description:** COLDATA analog supply voltage (VDDA).

| Statistic | Value |
|-----------|-------|
| Mean | 1185.1591 |
| Std | 1.9650 |
| Median | 1185.0000 |
| Min | 1180.0000 |
| Max | 1189.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 1171.4041 | 1198.9141 |

**Interpretation:** Should be stable within 7σ bounds.

![CDVDDA_ped](plot_CDVDDA_ped.png)

---

### 2.2 CDVDDIO_HALF_ped (CDVDDIO_HALF_ped)

**Description:** COLDATA I/O supply voltage (divided by 2).

| Statistic | Value |
|-----------|-------|
| Mean | 2231.4773 |
| Std | 5.8949 |
| Median | 2232.0000 |
| Min | 2221.0000 |
| Max | 2241.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 2190.2130 | 2272.7416 |

**Interpretation:** Should be stable within 7σ bounds.

![CDVDDIO_HALF_ped](plot_CDVDDIO_HALF_ped.png)

---

### 2.3 ADCRVDDD1P2_ped (ADCRVDDD1P2_ped)

**Description:** Right ColdADC digital 1.2V supply.

| Statistic | Value |
|-----------|-------|
| Mean | 1097.6364 |
| Std | 1.9551 |
| Median | 1097.5000 |
| Min | 1094.0000 |
| Max | 1101.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 1083.9507 | 1111.3221 |

**Interpretation:** Should be stable within 7σ bounds.

![ADCRVDDD1P2_ped](plot_ADCRVDDD1P2_ped.png)

---

### 2.4 ADCLVDDD1P2_ped (ADCLVDDD1P2_ped)

**Description:** Left ColdADC digital 1.2V supply.

| Statistic | Value |
|-----------|-------|
| Mean | 1097.5455 |
| Std | 1.8642 |
| Median | 1097.0000 |
| Min | 1094.0000 |
| Max | 1102.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 1084.4961 | 1110.5949 |

**Interpretation:** Should be stable within 7σ bounds.

![ADCLVDDD1P2_ped](plot_ADCLVDDD1P2_ped.png)

---

### 2.5 FERVDDP_ped (FERVDDP_ped)

**Description:** Right LArASIC positive supply voltage.

| Statistic | Value |
|-----------|-------|
| Mean | 1793.4091 |
| Std | 2.9720 |
| Median | 1793.5000 |
| Min | 1785.0000 |
| Max | 1799.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 1772.6051 | 1814.2131 |

**Interpretation:** Higher during pedestal, lower during pulse.

![FERVDDP_ped](plot_FERVDDP_ped.png)

---

### 2.6 FELVDDP_ped (FELVDDP_ped)

**Description:** Left LArASIC positive supply voltage.

| Statistic | Value |
|-----------|-------|
| Mean | 1792.7727 |
| Std | 3.2604 |
| Median | 1793.0000 |
| Min | 1783.0000 |
| Max | 1799.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 1769.9499 | 1815.5955 |

**Interpretation:** Higher during pedestal, lower during pulse.

![FELVDDP_ped](plot_FELVDDP_ped.png)

---

### 2.7 ADCRP25V_1_HALF_ped (ADCRP25V_1_HALF_ped)

**Description:** Right ColdADC 2.5V supply #1 (divided by 2).

| Statistic | Value |
|-----------|-------|
| Mean | 2252.5682 |
| Std | 5.6825 |
| Median | 2251.0000 |
| Min | 2243.0000 |
| Max | 2265.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 2212.7907 | 2292.3457 |

**Interpretation:** Should be stable within 7σ bounds.

![ADCRP25V_1_HALF_ped](plot_ADCRP25V_1_HALF_ped.png)

---

### 2.8 ADCLP25V_1_HALF_ped (ADCLP25V_1_HALF_ped)

**Description:** Left ColdADC 2.5V supply #1 (divided by 2).

| Statistic | Value |
|-----------|-------|
| Mean | 2250.5227 |
| Std | 5.0564 |
| Median | 2251.5000 |
| Min | 2240.0000 |
| Max | 2259.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 2215.1279 | 2285.9175 |

**Interpretation:** Should be stable within 7σ bounds.

![ADCLP25V_1_HALF_ped](plot_ADCLP25V_1_HALF_ped.png)

---

### 2.9 ADCRP25V_HALF_ped (ADCRP25V_HALF_ped)

**Description:** Right ColdADC 2.5V main supply (divided by 2).

| Statistic | Value |
|-----------|-------|
| Mean | 2251.8409 |
| Std | 5.6284 |
| Median | 2252.0000 |
| Min | 2237.0000 |
| Max | 2264.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 2212.4421 | 2291.2397 |

**Interpretation:** Should be stable within 7σ bounds.

![ADCRP25V_HALF_ped](plot_ADCRP25V_HALF_ped.png)

---

### 2.10 ADCLP25V_HALF_ped (ADCLP25V_HALF_ped)

**Description:** Left ColdADC 2.5V main supply (divided by 2).

| Statistic | Value |
|-----------|-------|
| Mean | 2252.2045 |
| Std | 5.2768 |
| Median | 2251.0000 |
| Min | 2240.0000 |
| Max | 2265.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 2215.2669 | 2289.1421 |

**Interpretation:** Should be stable within 7σ bounds.

![ADCLP25V_HALF_ped](plot_ADCLP25V_HALF_ped.png)

---

### 2.11 GND_ped (GND_ped)

**Description:** Ground reference measurement.

| Statistic | Value |
|-----------|-------|
| Mean | 29.4318 |
| Std | 2.6577 |
| Median | 29.0000 |
| Min | 23.0000 |
| Max | 33.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 10.8279 | 48.0357 |

**Interpretation:** Should be near zero, within 7σ bounds.

![GND_ped](plot_GND_ped.png)

---

## 3. LDO Voltage Parameters - Pulse (7σ Tolerance)

LDO measurements during pulse response check.

### 3.1 CDVDDA_pulse (CDVDDA_pulse)

**Description:** COLDATA analog supply voltage (VDDA).

| Statistic | Value |
|-----------|-------|
| Mean | 1185.1591 |
| Std | 1.8579 |
| Median | 1185.0000 |
| Min | 1180.0000 |
| Max | 1189.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 1172.1538 | 1198.1644 |

**Interpretation:** Should be stable within 7σ bounds.

![CDVDDA_pulse](plot_CDVDDA_pulse.png)

---

### 3.2 CDVDDIO_HALF_pulse (CDVDDIO_HALF_pulse)

**Description:** COLDATA I/O supply voltage (divided by 2).

| Statistic | Value |
|-----------|-------|
| Mean | 2232.0455 |
| Std | 5.4018 |
| Median | 2232.5000 |
| Min | 2220.0000 |
| Max | 2242.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 2194.2329 | 2269.8581 |

**Interpretation:** Should be stable within 7σ bounds.

![CDVDDIO_HALF_pulse](plot_CDVDDIO_HALF_pulse.png)

---

### 3.3 ADCRVDDD1P2_pulse (ADCRVDDD1P2_pulse)

**Description:** Right ColdADC digital 1.2V supply.

| Statistic | Value |
|-----------|-------|
| Mean | 1097.8409 |
| Std | 1.7181 |
| Median | 1098.0000 |
| Min | 1094.0000 |
| Max | 1101.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 1085.8142 | 1109.8676 |

**Interpretation:** Should be stable within 7σ bounds.

![ADCRVDDD1P2_pulse](plot_ADCRVDDD1P2_pulse.png)

---

### 3.4 ADCLVDDD1P2_pulse (ADCLVDDD1P2_pulse)

**Description:** Left ColdADC digital 1.2V supply.

| Statistic | Value |
|-----------|-------|
| Mean | 1097.7273 |
| Std | 1.7628 |
| Median | 1097.5000 |
| Min | 1094.0000 |
| Max | 1101.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 1085.3877 | 1110.0669 |

**Interpretation:** Should be stable within 7σ bounds.

![ADCLVDDD1P2_pulse](plot_ADCLVDDD1P2_pulse.png)

---

### 3.5 FERVDDP_pulse (FERVDDP_pulse)

**Description:** Right LArASIC positive supply voltage.

| Statistic | Value |
|-----------|-------|
| Mean | 1665.4773 |
| Std | 2.4167 |
| Median | 1665.0000 |
| Min | 1657.0000 |
| Max | 1670.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 1648.5604 | 1682.3942 |

**Interpretation:** Higher during pedestal, lower during pulse.

![FERVDDP_pulse](plot_FERVDDP_pulse.png)

---

### 3.6 FELVDDP_pulse (FELVDDP_pulse)

**Description:** Left LArASIC positive supply voltage.

| Statistic | Value |
|-----------|-------|
| Mean | 1665.1136 |
| Std | 2.7734 |
| Median | 1665.0000 |
| Min | 1656.0000 |
| Max | 1670.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 1645.6998 | 1684.5274 |

**Interpretation:** Higher during pedestal, lower during pulse.

![FELVDDP_pulse](plot_FELVDDP_pulse.png)

---

### 3.7 ADCRP25V_1_HALF_pulse (ADCRP25V_1_HALF_pulse)

**Description:** Right ColdADC 2.5V supply #1 (divided by 2).

| Statistic | Value |
|-----------|-------|
| Mean | 2252.9545 |
| Std | 5.6083 |
| Median | 2252.0000 |
| Min | 2242.0000 |
| Max | 2265.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 2213.6964 | 2292.2126 |

**Interpretation:** Should be stable within 7σ bounds.

![ADCRP25V_1_HALF_pulse](plot_ADCRP25V_1_HALF_pulse.png)

---

### 3.8 ADCLP25V_1_HALF_pulse (ADCLP25V_1_HALF_pulse)

**Description:** Left ColdADC 2.5V supply #1 (divided by 2).

| Statistic | Value |
|-----------|-------|
| Mean | 2250.6136 |
| Std | 4.8581 |
| Median | 2251.0000 |
| Min | 2241.0000 |
| Max | 2260.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 2216.6069 | 2284.6203 |

**Interpretation:** Should be stable within 7σ bounds.

![ADCLP25V_1_HALF_pulse](plot_ADCLP25V_1_HALF_pulse.png)

---

### 3.9 ADCRP25V_HALF_pulse (ADCRP25V_HALF_pulse)

**Description:** Right ColdADC 2.5V main supply (divided by 2).

| Statistic | Value |
|-----------|-------|
| Mean | 2252.1136 |
| Std | 5.2838 |
| Median | 2252.0000 |
| Min | 2237.0000 |
| Max | 2263.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 2215.1270 | 2289.1002 |

**Interpretation:** Should be stable within 7σ bounds.

![ADCRP25V_HALF_pulse](plot_ADCRP25V_HALF_pulse.png)

---

### 3.10 ADCLP25V_HALF_pulse (ADCLP25V_HALF_pulse)

**Description:** Left ColdADC 2.5V main supply (divided by 2).

| Statistic | Value |
|-----------|-------|
| Mean | 2251.9091 |
| Std | 4.9764 |
| Median | 2251.0000 |
| Min | 2239.0000 |
| Max | 2265.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 2217.0743 | 2286.7439 |

**Interpretation:** Should be stable within 7σ bounds.

![ADCLP25V_HALF_pulse](plot_ADCLP25V_HALF_pulse.png)

---

### 3.11 GND_pulse (GND_pulse)

**Description:** Ground reference measurement.

| Statistic | Value |
|-----------|-------|
| Mean | 33.2500 |
| Std | 2.8772 |
| Median | 33.0000 |
| Min | 27.0000 |
| Max | 38.0000 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 13.1096 | 53.3904 |

**Interpretation:** Should be near zero, within 7σ bounds.

![GND_pulse](plot_GND_pulse.png)

---

## 4. Current Measurements (7σ Tolerance)

Board-level current consumption for each power rail.

### 4.1 I LArASIC (Ped) (I_LArASIC_ped)

**Description:** LArASIC front-end ASIC current consumption.

| Statistic | Value |
|-----------|-------|
| Mean | 0.4226 |
| Std | 0.0030 |
| Median | 0.4225 |
| Min | 0.4180 |
| Max | 0.4300 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 0.4016 | 0.4436 |

**Interpretation:** Should be within 7σ bounds.

![I LArASIC (Ped)](plot_I_LArASIC_ped.png)

---

### 4.2 I ColdDATA (Ped) (I_ColdDATA_ped)

**Description:** COLDATA serializer ASIC current consumption.

| Statistic | Value |
|-----------|-------|
| Mean | 0.2319 |
| Std | 0.0071 |
| Median | 0.2320 |
| Min | 0.2230 |
| Max | 0.2720 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 0.1822 | 0.2816 |

**Interpretation:** Should be within 7σ bounds.

![I ColdDATA (Ped)](plot_I_ColdDATA_ped.png)

---

### 4.3 I ColdADC (Ped) (I_ColdADC_ped)

**Description:** ColdADC digitizer current consumption.

| Statistic | Value |
|-----------|-------|
| Mean | 1.5979 |
| Std | 0.0345 |
| Median | 1.5870 |
| Min | 1.5260 |
| Max | 1.7400 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 1.3564 | 1.8394 |

**Interpretation:** Should be within 7σ bounds.

![I ColdADC (Ped)](plot_I_ColdADC_ped.png)

---

### 4.4 I LArASIC (Pulse) (I_LArASIC_pulse)

**Description:** LArASIC front-end ASIC current consumption.

| Statistic | Value |
|-----------|-------|
| Mean | 0.6739 |
| Std | 0.0051 |
| Median | 0.6740 |
| Min | 0.6650 |
| Max | 0.6840 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 0.6382 | 0.7096 |

**Interpretation:** Should be within 7σ bounds.

![I LArASIC (Pulse)](plot_I_LArASIC_pulse.png)

---

### 4.5 I ColdDATA (Pulse) (I_ColdDATA_pulse)

**Description:** COLDATA serializer ASIC current consumption.

| Statistic | Value |
|-----------|-------|
| Mean | 0.2339 |
| Std | 0.0069 |
| Median | 0.2320 |
| Min | 0.2230 |
| Max | 0.2720 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 0.1856 | 0.2822 |

**Interpretation:** Should be within 7σ bounds.

![I ColdDATA (Pulse)](plot_I_ColdDATA_pulse.png)

---

### 4.6 I ColdADC (Pulse) (I_ColdADC_pulse)

**Description:** ColdADC digitizer current consumption.

| Statistic | Value |
|-----------|-------|
| Mean | 1.6006 |
| Std | 0.0301 |
| Median | 1.6020 |
| Min | 1.5260 |
| Max | 1.7090 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 1.3899 | 1.8113 |

**Interpretation:** Should be within 7σ bounds.

![I ColdADC (Pulse)](plot_I_ColdADC_pulse.png)

---

## 5. Power Measurements (7σ Tolerance)

Total board power consumption.

### 5.1 Total Power (Ped) (Total_Power_ped)

**Description:** Total board power consumption.

| Statistic | Value |
|-----------|-------|
| Mean | 7.4095 |
| Std | 0.1233 |
| Median | 7.3820 |
| Min | 7.1350 |
| Max | 7.8620 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 6.5464 | 8.2726 |

**Interpretation:** Should be within 7σ bounds.

![Total Power (Ped)](plot_Total_Power_ped.png)

---

### 5.2 Total Power (Pulse) (Total_Power_pulse)

**Description:** Total board power consumption.

| Statistic | Value |
|-----------|-------|
| Mean | 8.1342 |
| Std | 0.1066 |
| Median | 8.1565 |
| Min | 7.8980 |
| Max | 8.4630 |
| N | 44 |

**Pass/Fail Criteria (7σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 7.3880 | 8.8804 |

**Interpretation:** Should be within 7σ bounds.

![Total Power (Pulse)](plot_Total_Power_pulse.png)

---

## 6. ASIC-Level Parameters (5σ Tolerance)

Per-ASIC measurements (8 chips per board, 352 total data points).

### 6.1 FE Temperature (FE T)

**Description:** LArASIC temperature sensor reading.

| Statistic | Value |
|-----------|-------|
| Mean | 902.3207 |
| Std | 6.3980 |
| Median | 902.5500 |
| Min | 882.3000 |
| Max | 918.1000 |
| N | 352 |

**Pass/Fail Criteria (5σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 870.3307 | 934.3107 |

**Interpretation:** Should be consistent at room temperature.

![FE Temperature](plot_FE_T.png)

---

### 6.2 FE Bandgap (FE BGP)

**Description:** LArASIC bandgap reference voltage.

| Statistic | Value |
|-----------|-------|
| Mean | 1207.5426 |
| Std | 3.4129 |
| Median | 1207.5500 |
| Min | 1198.7000 |
| Max | 1216.5000 |
| N | 352 |

**Pass/Fail Criteria (5σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 1190.4781 | 1224.6071 |

**Interpretation:** Critical for stable operation.

![FE Bandgap](plot_FE_BGP.png)

---

### 6.3 ADC VCMI (ADC_VCMI)

**Description:** ColdADC common-mode input voltage.

| Statistic | Value |
|-----------|-------|
| Mean | 937.2756 |
| Std | 3.1470 |
| Median | 937.0000 |
| Min | 929.0000 |
| Max | 945.6000 |
| N | 352 |

**Pass/Fail Criteria (5σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 921.5406 | 953.0106 |

**Interpretation:** Should be consistent across chips.

![ADC VCMI](plot_ADC_VCMI.png)

---

### 6.4 ADC VCMO (ADC_VCMO)

**Description:** ColdADC common-mode output voltage.

| Statistic | Value |
|-----------|-------|
| Mean | 1224.4903 |
| Std | 3.3991 |
| Median | 1224.1000 |
| Min | 1213.7000 |
| Max | 1233.4000 |
| N | 352 |

**Pass/Fail Criteria (5σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 1207.4948 | 1241.4858 |

**Interpretation:** Should be consistent across chips.

![ADC VCMO](plot_ADC_VCMO.png)

---

### 6.5 ADC VREFP (ADC_VREFP)

**Description:** ColdADC positive reference voltage.

| Statistic | Value |
|-----------|-------|
| Mean | 1942.3085 |
| Std | 4.6486 |
| Median | 1942.1500 |
| Min | 1922.8000 |
| Max | 1954.4000 |
| N | 352 |

**Pass/Fail Criteria (5σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 1919.0655 | 1965.5515 |

**Interpretation:** Sets upper ADC range limit.

![ADC VREFP](plot_ADC_VREFP.png)

---

### 6.6 ADC VREFN (ADC_VREFN)

**Description:** ColdADC negative reference voltage.

| Statistic | Value |
|-----------|-------|
| Mean | 501.5187 |
| Std | 2.9686 |
| Median | 501.5500 |
| Min | 494.5000 |
| Max | 507.8000 |
| N | 352 |

**Pass/Fail Criteria (5σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 486.6757 | 516.3617 |

**Interpretation:** Sets lower ADC range limit.

![ADC VREFN](plot_ADC_VREFN.png)

---

### 6.7 VSSA (VSSA)

**Description:** Analog ground reference voltage.

| Statistic | Value |
|-----------|-------|
| Mean | 67.4304 |
| Std | 3.0570 |
| Median | 67.2000 |
| Min | 58.8000 |
| Max | 74.1000 |
| N | 352 |

**Pass/Fail Criteria (5σ):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| 52.1454 | 82.7154 |

**Interpretation:** Should be near zero.

![VSSA](plot_VSSA.png)

---

## Appendix A: Complete Pass/Fail Criteria Summary

| Parameter | Type | Method | Lower Limit | Upper Limit |
|-----------|------|--------|-------------|-------------|
| ped | 128ch | 5σ | 387.8101 | 1435.8031 |
| rms | 128ch | 5σ | 8.9255 | 13.4675 |
| PPK_mean | 128ch | 5σ | 12276.2331 | 13219.0811 |
| NPK_mean | 128ch | 5σ | 3983.4115 | 4839.6375 |
| BL_mean | 128ch | 5σ | 8229.0016 | 8930.4476 |
| pedmax | 128ch | 5σ | 426.1951 | 1472.7801 |
| pedmin | 128ch | 5σ | 348.7288 | 1399.5968 |
| CDVDDA_ped | ldo_ped | 7σ | 1171.4041 | 1198.9141 |
| CDVDDIO_HALF_ped | ldo_ped | 7σ | 2190.2130 | 2272.7416 |
| ADCRVDDD1P2_ped | ldo_ped | 7σ | 1083.9507 | 1111.3221 |
| ADCLVDDD1P2_ped | ldo_ped | 7σ | 1084.4961 | 1110.5949 |
| FERVDDP_ped | ldo_ped | 7σ | 1772.6051 | 1814.2131 |
| FELVDDP_ped | ldo_ped | 7σ | 1769.9499 | 1815.5955 |
| ADCRP25V_1_HALF_ped | ldo_ped | 7σ | 2212.7907 | 2292.3457 |
| ADCLP25V_1_HALF_ped | ldo_ped | 7σ | 2215.1279 | 2285.9175 |
| ADCRP25V_HALF_ped | ldo_ped | 7σ | 2212.4421 | 2291.2397 |
| ADCLP25V_HALF_ped | ldo_ped | 7σ | 2215.2669 | 2289.1421 |
| GND_ped | ldo_ped | 7σ | 10.8279 | 48.0357 |
| CDVDDA_pulse | ldo_pulse | 7σ | 1172.1538 | 1198.1644 |
| CDVDDIO_HALF_pulse | ldo_pulse | 7σ | 2194.2329 | 2269.8581 |
| ADCRVDDD1P2_pulse | ldo_pulse | 7σ | 1085.8142 | 1109.8676 |
| ADCLVDDD1P2_pulse | ldo_pulse | 7σ | 1085.3877 | 1110.0669 |
| FERVDDP_pulse | ldo_pulse | 7σ | 1648.5604 | 1682.3942 |
| FELVDDP_pulse | ldo_pulse | 7σ | 1645.6998 | 1684.5274 |
| ADCRP25V_1_HALF_pulse | ldo_pulse | 7σ | 2213.6964 | 2292.2126 |
| ADCLP25V_1_HALF_pulse | ldo_pulse | 7σ | 2216.6069 | 2284.6203 |
| ADCRP25V_HALF_pulse | ldo_pulse | 7σ | 2215.1270 | 2289.1002 |
| ADCLP25V_HALF_pulse | ldo_pulse | 7σ | 2217.0743 | 2286.7439 |
| GND_pulse | ldo_pulse | 7σ | 13.1096 | 53.3904 |
| I_LArASIC_ped | current | 7σ | 0.4016 | 0.4436 |
| I_ColdDATA_ped | current | 7σ | 0.1822 | 0.2816 |
| I_ColdADC_ped | current | 7σ | 1.3564 | 1.8394 |
| I_LArASIC_pulse | current | 7σ | 0.6382 | 0.7096 |
| I_ColdDATA_pulse | current | 7σ | 0.1856 | 0.2822 |
| I_ColdADC_pulse | current | 7σ | 1.3899 | 1.8113 |
| Total_Power_ped | power | 7σ | 6.5464 | 8.2726 |
| Total_Power_pulse | power | 7σ | 7.3880 | 8.8804 |
| FE T | 8chip | 5σ | 870.3307 | 934.3107 |
| FE BGP | 8chip | 5σ | 1190.4781 | 1224.6071 |
| ADC_VCMI | 8chip | 5σ | 921.5406 | 953.0106 |
| ADC_VCMO | 8chip | 5σ | 1207.4948 | 1241.4858 |
| ADC_VREFP | 8chip | 5σ | 1919.0655 | 1965.5515 |
| ADC_VREFN | 8chip | 5σ | 486.6757 | 516.3617 |
| VSSA | 8chip | 5σ | 52.1454 | 82.7154 |

---

## Appendix B: Tolerance Configuration

| Parameter Type | Tolerance | Description |
|----------------|-----------|-------------|
| 128-Channel | 5σ | Mean ± 5×Std, for large datasets (5632 points) |
| 8-Chip ASIC | 5σ | Mean ± 5×Std, for ASIC-level measurements (352 points) |
| LDO Voltages | 7σ | Mean ± 7×Std, wider tolerance for power rail (44 points) |
| Currents | 7σ | Mean ± 7×Std, wider tolerance for current measurements |
| Power | 7σ | Mean ± 7×Std, wider tolerance for power measurements |

---

## Appendix C: Board List

44 boards were used in this analysis (latest passing test only).
See `good_boards_list.txt` for the complete list.

---

## Appendix D: Excluded Boards

- **Board 00046:** Manually excluded (known bad board)
- Boards with only failed tests were automatically excluded

---

*Report generated from QC checkout data analysis*
*BNL Cold Electronics Testing Facility*
