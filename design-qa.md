# TBFX 销售页：前20大客户信息汇总

- Source: `codex-clipboard-1f0abaea-e109-45ee-b731-fc48be8fc8b7.png`, 750 × 594 pixels, user-supplied Q3 Excel reference.
- Rendered evidence: `../tbfx-top20-q3-preview.jpg` (1280 × 900 desktop viewport), `../tbfx-top20-mobile-preview.jpg` (390 × 844 narrow viewport), and `../tbfx-top20-design-comparison.png`. Evidence is local only.
- Compared native-density captures side by side for 2026 Q3, nationwide, using the screenshot as the column/content reference rather than a browser-size design.

## Findings

- The full view places the panel directly after the existing customer ranking. The focused table preserves the requested customer/type columns and metric/YoY pairs, with explicit rank and amount units. Spot-checked the first row against the reference; formal customer names follow the existing merge master.
- The existing dashboard sans-serif, muted header, and rounded panel integrate with adjacent sections. Financial columns are right-aligned with tabular numerals. Alternating row fill and signed positive/negative colors make the dense table readable without relying on color alone. The reference contains no image assets.
- Narrow-screen pass 1 (P2): only rank and name were initially visible. Constrained the first four column widths; pass 2 at the same 390 px viewport shows rank, name, type, and sales together. Long names wrap and remaining columns scroll inside the table. Keyboard right arrow moved the table 160 px without expanding the panel.
- Browser verified 20 rows by default and after selecting Q3, plus 2025.10 with an unavailable 2024 baseline shown as dashes. No browser console errors in the verified preview. Existing chart sections remain unchanged.

final result: passed
