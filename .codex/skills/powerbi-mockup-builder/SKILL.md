---
name: powerbi-mockup-builder
description: Build or update a Power BI PBIP report from a UI mockup (HTML/Figma/PNG) with UX improvements. Use when asked to implement or refine a Power BI app to match a mockup, map visuals to a semantic model, add measures, or edit PBIP report/semantic model files.
---

# PowerBI Mockup Builder

## Overview

Turn a mockup into a real PBIP report by mapping visuals to the semantic model, adding required measures, and updating PBIP artifacts safely.

## Workflow Decision Tree

1. **Mockup type?**
   - **HTML**: Extract page titles, KPIs, charts, tables, filters, interactions.
   - **Image/Figma**: Identify sections and visuals; if labels are unclear, ask one question.
2. **PBIP present?**
   - **Yes**: Update existing `.Report` and `.SemanticModel` artifacts.
   - **No**: Create a report spec first, then build PBIP.
3. **Model gaps?**
   - **Missing fields/measures**: Add DAX measures or document a workaround.
   - **Missing tables**: Exclude visuals or propose a spec change.

## Quick Start

1. Locate artifacts and mockups:
   - Find `.pbip`, `.Report`, `.SemanticModel`, and mockup files.
2. Read the semantic model:
   - Tables/columns, measures, relationships, date table.
3. Convert mockup → page spec:
   - Page list, KPIs, charts, tables, slicers, interactions.
4. Add required measures:
   - Prefer reusable measures; set format strings.
5. Implement PBIP changes:
   - Update `.SemanticModel` TMDL (measures, tables if needed).
   - Update `.Report` report.json for pages/visuals.
6. Validate:
   - No broken fields, visuals match grain, filters use date table.

## Implementation Steps (PBIP)

1. **Inventory**
   - Identify PBIP root and related folders.
   - Note report theme and display names.

2. **Model mapping**
   - Build a field map: mockup labels → tables/columns/measures.
   - Flag any mismatch immediately.

3. **Measures**
   - Add measures in the fact table or a dedicated measures table.
   - Provide DAX + format + description.
   - Avoid implicit aggregation in visuals.

4. **Pages & visuals**
   - Create/rename sections to match mockup tabs.
   - Add visuals with explicit fields and filters.
   - Set interactions intentionally (cross-filter/highlight/none).

5. **Filters & slicers**
   - Use the model's date table.
   - Keep consistent slicers across pages if the mockup implies it.

6. **UX improvements (safe)**
   - Improve legibility, alignment, and hierarchy.
   - Keep layout consistent with mockup.
   - Avoid scope creep beyond the mockup unless asked.

7. **Validation**
   - Check for missing fields/measures.
   - Verify relationships support visuals.
   - Confirm totals won't double-count.

## Visual Configuration Patterns

### Time-Formatted Measures (MM:SS)

For duration metrics, use this DAX pattern:

```dax
AHT Formatted =
VAR TotalSeconds = [Avg Handle Time (sec)]
VAR Minutes = INT(TotalSeconds / 60)
VAR Seconds = MOD(TotalSeconds, 60)
RETURN FORMAT(Minutes, "0") & ":" & FORMAT(Seconds, "00")
```

### Table Data Bars

Apply conditional formatting for inline data visualization:

- Select measure column → Conditional formatting → Data bars
- Configure min (0 or auto), max (auto), bar color
- Accessibility: Power BI generates "data bar XX%" screen reader text

### Treemap Hierarchy

For multi-level treemaps:

- Group: Parent category field (e.g., CSQ Name)
- Details: Child metrics (Total, Handled, Abandoned)
- Use distinct colors per category

### Navigation Buttons

Button actions:

- **Page navigation**: Links to another report page
- **Web URL**: Opens external link
- **Bookmark**: Applies filter state or shows/hides visuals

Place navigation buttons consistently (left sidebar or top).

### Wallboard Layout Pattern

For real-time operational dashboards:

- **Row 1**: Large KPI cards (4-6) for critical live metrics
- **Row 2**: Status tables (Agent Status, Queue Status)
- **Row 3**: Summary KPIs for daily totals
- **No slicers**: Operators need full unfiltered view
- **Large fonts**: Readable from distance

### Dark Theme Color Palette

| Purpose          | Color      | Hex     |
|------------------|------------|---------|
| Background       | Navy       | #1B2838 |
| Primary Accent   | Teal       | #00A99D |
| Secondary Accent | Yellow     | #F4D03F |
| Warning          | Orange     | #E67E22 |
| Text Primary     | White      | #FFFFFF |
| Text Secondary   | Light Gray | #CCCCCC |

## Output Requirements

- Provide a concise change summary.
- List files changed.
- Provide a short manual test checklist (refresh, slicers, key visuals).
- Ask only one clarifying question if blocked.

## References

- PBIP structure guide: `references/pbip-files.md`
