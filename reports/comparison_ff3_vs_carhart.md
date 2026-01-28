# FF3 vs. Carhart (Momentum) Comparison  
**25 Size–Book-to-Market Portfolios**

## Overview
This report compares time-series regressions of portfolio returns under the
Fama–French three-factor (FF3) model and the Carhart four-factor model (FF3 + Momentum).
The goal is to assess how the inclusion of the momentum factor affects estimated
abnormal returns (alphas) and overall model fit.

The analysis uses monthly returns for the 25 Size–B/M portfolios and Newey–West
(HAC) standard errors with 3 lags.

---

## Models

### Fama–French 3-Factor Model
$$ R_{i,t} - R_{f,t} = \alpha_i + \beta_{i,M}(Mkt\!-\!RF)_t + \beta_{i,S}SMB_t + \beta_{i,H}HML_t + \varepsilon_{i,t}  $$

### Carhart 4-Factor Model
$$ R_{i,t} - R_{f,t} = \alpha_i + \beta_{i,M}(Mkt\!-\!RF)_t + \beta_{i,S}SMB_t + \beta_{i,H}HML_t + \beta_{i,Mo}Mom_t + \varepsilon_{i,t} $$

---

## Comparison Strategy
- FF3 and Carhart regressions are estimated separately for each portfolio.
- Results are merged into a single comparison table:
  - FF3 alpha vs. Carhart alpha
  - Change in alpha:  
    $$
    \Delta \alpha = \alpha_{\text{Carhart}} - \alpha_{\text{FF3}}
    $$
  - Change in goodness of fit:
    $$
    \Delta R^2 = R^2_{\text{Carhart}} - R^2_{\text{FF3}}
    $$

The comparison table is stored as:
[ff3_vs_carhart_comparison.csv](ff3_vs_carhart_comparison.csv)

---

## Results

### Alpha Behavior
Across the 25 portfolios, estimated alphas generally **shrink toward zero**
after adding the momentum factor.

This shrinkage is not random:
- Portfolios that exhibit strong momentum loadings under the Carhart model
  tend to show the largest reductions in alpha.
- This pattern is consistent with **omitted-variable bias** in the FF3 model,
  where momentum-related returns are incorrectly absorbed into the intercept.

### Momentum Factor Significance
In the Carhart regressions, the momentum factor loadings are frequently
statistically significant, indicating that momentum captures systematic
variation in returns not explained by the FF3 factors.

This supports the interpretation that the reduction in FF3 alphas reflects
improved model specification rather than overfitting noise.

### R² Changes
The inclusion of an additional factor mechanically increases in-sample \(R^2\),
so the observed increases in \(R^2\) are not interpreted as formal statistical
evidence.

\( \Delta R^2 \) indicates that momentum contributes meaningfully to explaining 
return variation across portfolios.

---

## Figures

### Alpha: FF3 vs Carhart
![Alpha scatter](../figures/alpha_ff3_vs_carhart.png)

### \(\Delta R^2\) by portfolio
![Delta R2](../figures/delta_r2_by_portfolio.png)

## Interpretation
The results are consistent with the core Carhart (1997) finding:
- Momentum represents an additional priced dimension of risk or return
  variation.
- Once momentum is accounted for, the apparent abnormal returns observed under
  the FF3 model are substantially reduced.
- The evidence for momentum arises from both statistically significant factor
  loadings and systematic attenuation of FF3 alphas.

---

## Conclusion
Adding the momentum factor improves the fit of the asset pricing model
for the 25 Size–B/M portfolios. While changes in \(R^2\) are mechanical, the
behavior of alphas and the significance of momentum loadings provide strong
evidence that momentum captures an important component of expected returns not
addressed by the Fama–French three-factor model.

---

## Files Generated
- `reports/ff3_25_5x5_results.csv`
- `reports/carhart_25_5x5_results.csv`
- `reports/ff3_vs_carhart_comparison.csv`