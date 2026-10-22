# Independent reviews of the ISCAS 2027 draft (22 Oct 2026)

Three reviews of `paper/main.pdf` (the rewritten draft of 22 Oct), each produced by a separate AI reviewer with no knowledge of the editing history, acting as an ISCAS 2027 reviewer with expertise in memory circuits, RRAM, and processing-in-memory. They are AI reviews, not human ones, so treat them as a preview of what a careful reviewer is likely to raise rather than as a verdict. Still, three independent readers converged on the same handful of problems, and those are the ones to fix first.

| Reviewer | Novelty | Soundness | Clarity | Relevance | Recommendation |
|---|---|---|---|---|---|
| A | 3 | 2 | 3 | 4 | Weak reject |
| B | 3 | 2 | 3 | 4 | Weak reject |
| C | 3 | 3 | 3 | 5 | Weak accept |

All three agree the problem is real and well motivated, the writing is competent, the honesty about limitations is a strength, and the topic fits ISCAS. All three also agree the contribution is modest (time-domain readout and multi-row bitwise PiM are each known; the new part is the register and pad tunability plus the device-budget analysis) and that the evidence does not yet support the central claims.

## Raised by all three reviewers (fix these first)

1. **The 8-row NOR margin is quoted as both six and five taps.** Six in the abstract, introduction, Table II, Section IV-C, and the conclusion. Five in Table III at 27 C and in Fig. 4(a), and "four to five" in Section IV-D. If Table II is a direct transient and the others come from the crossing-time and tap-table model, say so where each number appears and explain the one-tap difference. Otherwise pick one number.

2. **The spread budget contradicts the single-row claim.** The Monte Carlo limit for one row is sigma_lnR = 0.46. The paper itself reports 0.5 to 1 for the Al-doped 130 nm devices, which is the module the macro is built in. So "the single-row read works at the characterized HRS" is not supported by the data in the paper, and the 1 MOhm eight-row limit of 0.5 sits at the bottom edge of that range, not "inside" it. Say which device population applies and rewrite the claim accordingly. Reviewer C also asks why 200 kOhm is used when the stated median is 90 to 220 kOhm with a conductive edge at 50 kOhm, and suggests adding a single-row and NOR result near 100 kOhm and at 50 kOhm.

3. **The temperature claim in the conclusion overreaches, and corners are promised but not shown.** "Re-tuning restores these margins across temperature" is false for the multi-row operations at 125 C (one tap for NOR, zero for majority, in Table III). Section IV-D is titled "corners and temperature" and the text quotes a 16 to 60 ns band over corners, but Table III has only the typical corner. Either add corner rows (the CSVs exist in `paper/results/corners/`) or remove corners from the title and text. Reviewer B adds that per-temperature re-tuning needs a sensor and a calibration loop, the very cost the introduction criticizes.

4. **The energy figure is an artifact of precharge clocking.** 90 percent of the 65 to 105 pJ is word-line flip-flop clock energy during a 400 ns precharge, and the paper says a clock gate would remove it. Reporting 0.13 to 0.2 pJ/bit as the headline (abstract, Table I, Table IV) is misleading. Also, "per bit" divides by 512 thermometer bits while only 64 decisions leave the macro, so it is about 1 to 1.6 pJ per result bit. Report read-path energy and the clock-gated estimate separately, state energy per logical result, and clarify whether "below 0.3 pJ" is per bit or per access. Two reviewers call the justification for the 40-cycle precharge ("the line loading doubles every crossing time") a non sequitur for about 100 fF; explain why 400 ns is needed. The 0.45 us access time is a throughput cost that deserves explicit discussion.

5. **The Monte Carlo is under-described and too narrow.** State the distribution sampled (lognormal HRS only? LRS too?), what "ideal threshold" means, whether the 1e-3 error rate is per cell or per 512-bit word, and how 160 SPICE runs can check a 1e-3 tail. Say that 0.46/sqrt(n) is a Gaussian-sum heuristic. Nothing varies except HRS: access-transistor Vt mismatch (critical, since the device is in weak inversion and current is exponential in Vt), buffer-threshold mismatch, delay-line and tap mismatch across the 64 columns sharing one line, supply noise, and TDC jitter are all absent. Reviewer B notes a Gaussian in ln R is inconsistent with a 50 kOhm floor.

6. **Tap pitch and fixed latency are never given.** The whole design turns on the relationship between the 10 ns offset step, the window width (eight taps times the pitch), and the latency from SL grounding to the first tap. Fig. 3(a) lets a reader infer about 13 ns latency and about 0.25 ns pitch, but the paper never says so. Give the pitch at each V_DEL, the latency, and the PVT sensitivity of the uncalibrated delay line. Reviewer C asks why the window is not simply widened (lower V_DEL or a longer line) to cover the 10 ns grid, which looks easier than the fractional-cycle offset proposed in IV-F. Reviewer B adds that "margin in taps" is a weak metric when 7 versus 1 comes from a 1 ns difference; report margin in ns against TDC resolution and jitter.

7. **Table II bias pairs are not self-consistent with resistor cells.** 0.09 V at 1.3 uA implies 69 kOhm, which is neither 9 k nor 200 k, and 0.12 V across 1 MOhm cannot carry 1.0 uA. Define V_RRAM and I_cell (which cell, which instant, peak or average). The read-disturb conclusion depends on them. Clarify the 8 uA RESET target versus the 5 uA ISPVA target, and soften the abstract's "below the read-disturb condition" since the evidence is SET-polarity data.

8. **Table IV compares against the wrong baselines.** It compares MAC engines on incomparable metrics (ns/cycle, TOPS/W, pJ/bit). The baseline all three want is a conventional voltage-mode or reference-tracked sense amplifier in the same process on the same device and RC model (area per column, energy per logical result, margin at 200 k / 9 k). Prior RRAM discharge-time or TDC readouts, and Pinatubo-style bitwise sensing, are absent. The [11] entry (0.3 to 0.8 TOPS/W) against that paper's title (768 to 2124) needs the normalization explained. Reviewer B: verify the nodes of [10] and [11].

9. **Implementation claims lack evidence.** AMS co-verification is stated but no result is shown; show a waveform or drop the claim. The Table I area split sums to 77 percent; say what the other 23 percent is.

10. **Undefined terms.** MEMRES, LRS2, PSP, BLD, TS_LS, "settle-drain bit", "signed offset" (range and sign). The ISPVA expansion is wrong: it should be "incremental step pulse with verify algorithm".

## Raised by two reviewers

- **Tunability is asserted, not demonstrated** (A, B). Every result uses C_MIM = 10 fF and one HRS. Sweep C_MIM and HRS and show that re-tuning recovers the margins where a fixed design does not. The host search procedure is never described, and it needs cells of known state, so "no reference cell" is overstated. The knobs are global (shared delay line, shared pads), so column-to-column variation is untouched. The `cap_sensitivity` CSVs may already cover the C_MIM part.
- **The weak-inversion operating point** (B, C). V_gate = 0.8 V compresses 22:1 to 3 to 3.6:1 and makes the read exponentially sensitive to Vt, temperature, and mismatch. The justification "so that a read never approaches a write condition" is weak because the cell sees only 0.06 to 0.12 V. Explain why a higher V_gate adds only 30 to 45 percent contrast, or show a V_gate sweep to 1.2 to 1.5 V.
- **Fig. 3(b) legend** covers the 1 MOhm plateau (A, C). Fig. 3 also lacks the 1 MOhm NOR point of Table II (C).
- **Fig. 2(b) layout** is unreadable at column width (A), and the clipped PDF still carries the old panel (a) text layer, so labels appear twice in text search (A, C). Crop the PDF itself rather than clipping in LaTeX.
- **Table I and Fig. 2(a) repeat the text** (B), and Table III could be one sentence (B); the space is better spent on a tuning flow and the error model.

## Raised by one reviewer, worth checking

- Splitting wide sums into eight-row groups works for NOR but not for majority: a majority of a union cannot be computed from per-group majorities (A).
- The popcount statement (distinct code only for two rows) conflicts with Table II, where the majority row resolves several counts at eight rows; and 1/k^2 in IV-C versus 1/n^2 in IV-D (A). The Section II sentence has since been removed; the IV-D one remains.
- Single read, NOR, and majority use different V_drain and V_DEL, which are supply pads; explain how a mixed instruction stream switches them, or show one setting that serves all (B).
- Off-state leakage of the 56 uninstantiated rows is not added, which matters at 125 C and at the 0.12 uA 1 MOhm read (B).
- The compact model is validated only at 1.4 and 12 kOhm, never at any HRS used (B).
- Fig. 1(b) shows DRAIN_SL low during settle, contradicting the settle-drain requirement in IV-C (C).
- Pinatubo already adjusts the sense reference for OR/AND/XOR, so the novelty statement should position against it explicitly (B).
- "Tape-out-ready": state whether it was submitted (B).

## Minor issues (collected)

- Fig. 1(b): the "LRS -> 00000000" label collides with the threshold line and renders garbled.
- Table II: the single-row row mixes formats in the codes column; "off." and "k = 0...8" headers are cryptic; the dagger footnote placement is odd; "direct transients" is unclear.
- Table III caption: say which entry is fixed and which is re-tuned.
- Table IV: "summed" header is cryptic; "[10] none on chip" is an odd row for a memory comparison; "slice SPICE" should read "8x8 slice, post-layout SPICE".
- Section IV-B: "with 0.9 V on BL" while the single-row point uses V_drain = 0.8 V.
- Fig. 2(b) reads 227 um while caption and Table I say 226.5 um.
- The disturb figures (1e5 pulses, drift at 0.3 V) need a citation.
- Section IV-A first sentence is about 60 words; split it.
- The abstract is long and dense; one reviewer suggests about 150 words.
- References [13] and [14] are 2026 and early access; confirm by camera-ready.
- Notation: V_DEL in capitals versus V_drain and V_gate.
- Only the first author's email is listed.

## Suggested order of work

1. Reconcile the NOR margin everywhere (one afternoon with the existing CSVs).
2. Rewrite the spread claim against the 130 nm device data, and add the Monte Carlo details (distribution, threshold, error-rate definition).
3. Add corner rows to Table III from `paper/results/corners/`, or drop corners from the title and text, and qualify the temperature sentence in the conclusion.
4. Split the energy into precharge clocking and read path, state energy per 64-bit result, and justify or shorten the precharge.
5. State tap pitch per V_DEL and the fixed latency, and define V_RRAM and I_cell in Table II.
6. Replace Table IV with a baseline that is comparable, or at least add the structural columns the reviewers ask for.
7. Define the remaining acronyms, fix the figure overlaps, and crop the Fig. 2(b) PDF.

## Status after the revision of 22 Oct (evening)

Eyal's commits of 22 Oct (up to "Energy: buffer static share") plus the merge of their separate PDF draft into the source address most of the list above. Table numbering below refers to the revised paper, where the operating-point table is Table I and the comparison table is Table II; the temperature table and the macro summary table were folded into the text.

Done, with where it now lives:

- Item 1, NOR margin: Section IV-C states that the computed codes are one tap conservative, so six taps is the direct transient and five is the crossing-time model behind Fig. 4 and the temperature results. The abstract, introduction, and conclusion quote six.
- Item 2, spread claim: Section IV-E names both device populations (250 nm arrays, spread 0.5 with the edge clipped at 40 kOhm; Al-doped 130 nm, 0.5 to 1, median 90 to 220 kOhm, edge at 50 kOhm), places the single-row limit of 0.45 "at the edge of the characterized state", and gives the deep-reset limits (0.5 NOR, 0.6 majority). The abstract and introduction no longer claim the read "works at the characterized HRS".
- Item 3, corners and temperature: Section IV-D now has the five PSP corners with the cells scaled by their measured temperature coefficients, the 16 ns (ff, 125 C) to 60 ns (ss, -40 C) band, the single-row read decided in 14 of 15 corner-temperature pairs after re-searching the offset, and the 8-row NOR recovered only at -40 C. The conclusion says so.
- Item 4, energy: per 64-bit result (1.0 to 1.7 pJ), with the split into word-line clock (53 to 69 %), buffer static current (21 to 23 % at 0.8 V), and array plus delay line (0.5 to 1.1 pJ), the clock-gated estimate (21 to 50 pJ per access), and the reason for the 40-cycle precharge (the loaded bit line reaches 0.49 V after ten cycles at 0.8 V). The access time is stated with the throughput.
- Item 5, Monte Carlo: lognormal cells (LRS sigma 0.1, HRS swept) behind the 0.08 MOhm access resistance, ideal midpoint threshold, 1e5 draws, error per column decision, 160 SPICE runs reproducing the crossing-time spread, the 1/sqrt(n) form named as a Gaussian sum, and the 1e-6 scaling (0.65x). Transistor mismatch is still not in the Monte Carlo; see below.
- Item 6, tap pitch and latency: first tap 3.4 ns after the READ edge; pitch 0.35, 0.24, 0.18 ns at V_DEL = 0.8, 0.9, 1.0 V; window 2.5 to 1.3 ns; the window cannot be widened beyond about 5 ns because the line stops clocking the flip-flops below 0.7 V, which answers why the fractional-cycle offset is the fix.
- Item 7, Table I bias pairs: the footnote defines V_RRAM and I_cell as the largest values over the row's runs, in different cells and at different instants, and IV-B says the HRS cell sees 0.09 V while the LRS cell draws 1.3 uA.
- Item 8, comparison: Table II gained the 22 nm 8 Mb ReRAM time-domain macro (Hung et al., JSSC 2023) and the FeFET thermometer-code macro (Mattar et al.), with the [11] normalization explained in the footnote, and the metric is per 64-bit result. Section IV-F positions the work against the FeFET macro. A same-process voltage-mode sense amplifier baseline is still absent.
- Item 9, implementation evidence: Section III states that in the AMS simulation the sequenced reads return the codes of the stimulus-driven runs. The area split table was removed, so the 77 % question is moot.
- Item 10, terms: MEMRES expanded, LRS2 removed, ISPVA expanded correctly, settle-drain reworded as a controller bit, signed offset defined with its sign. PSP is named as the foundry transistor model. BLD and TS_LS appear only in the figures.
- Two-reviewer items: the per-operation supply pads are explained in IV-C (bench supplies on the test chip, grouped by operation or regulated on chip); the global-knob limitation and a first-order buffer-offset estimate (2.5 % per 10 mV, comparable to the majority step) are in IV-F (the v3 markup dropped the per-column-threshold mitigation, since such thresholds cannot absorb offsets larger than the 1.2 ns window); Fig. 1(b) now shows the source line grounded as the rows open; Fig. 2(b) is a cropped PDF with no hidden text layer; Fig. 3 carries the 1 MOhm NOR point and its legend sits above the panels; the popcount sentence was removed and the eight-row grouping is now stated for NOR only; the majority tie rule for even n is stated.

Still open:

- A mismatch Monte Carlo over the access transistor, buffer, and delay line (all three reviewers). The paper now says this is the next step and gives the estimate; it does not do it.
- A conventional sense-amplifier baseline on the same device and RC model (all three reviewers).
- A C_MIM or HRS sweep that shows re-tuning recovering a margin a fixed design loses (reviewers A and B). The `cap_sensitivity` CSVs may cover the C_MIM part.
- A single-row and NOR result near the 100 kOhm median and at the 50 kOhm edge (reviewer C).
- Off-state leakage of the uninstantiated rows (reviewer B).
- Mattar et al. is cited as arXiv:2504.03925 with a note that it is accepted to IEEE TCAS-I; replace with the journal reference by camera-ready, and confirm the two 2026 early-access references.
- Figs. 3 and 4 are now at 86 % of the column width to fit four pages; check label legibility in print.
