# Publication announcement — draft for editing

I’ve prepared a reproducible verification study of an assumption in an open-source ASIC power-integrity analyzer.

In a deliberately simple two-node RC network, switching both loads simultaneously produced 47.628 mV peak voltage droop. Allowing their event centers to vary produced a worst case of 55.157 mV — a 15.81% increase under the stated model.

The counterexample was checked using a mathematical response model, the pinned native Rust executable and ngspice. The archive includes input fixtures, raw outputs, test results and a proposed upstream documentation correction.

This is a **technical reproducibility contribution**, not a new general EDA algorithm and not a measured silicon defect. I think it illustrates why worst-case assertions need explicit assumptions and adversarial test cases.

**Repository:** [insert your public GitHub URL after release]
**Archival DOI:** [insert after Zenodo issues it]

Topics: #EDA #ComputerEngineering #Semiconductors #OpenSource #PowerIntegrity
