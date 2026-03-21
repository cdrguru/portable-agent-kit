# PBIP Files Quick Guide

Use this as a quick reference when editing PBIP artifacts.

## Typical Structure

- `*.pbip` (root descriptor)
- `<Report>.Report/`
  - `definition.pbir`
  - `report.json`
  - `.platform`
  - `StaticResources/`
- `<Report>.SemanticModel/`
  - `definition.pbism`
  - `definition/`
    - `model.tmdl`
    - `relationships.tmdl`
    - `tables/*.tmdl`
    - `expressions.tmdl`
  - `.platform`

## Common Edits

- **Pages/visuals**: `report.json` sections and visualContainers
- **Measures/columns**: `tables/*.tmdl`
- **Relationships**: `relationships.tmdl`
- **Parameters**: `expressions.tmdl`
- **Dataset linkage**: `definition.pbir`

## Safe Practices

- Keep date table consistent with slicers.
- Avoid renaming tables/columns unless required.
- Add measures with clear names and format strings.
- Verify relationships for visuals that join multiple tables.

## Visual Container Structure

In `report.json`, each visual is a container with position and config:

```json
{
  "x": 0,
  "y": 0,
  "width": 300,
  "height": 200,
  "z": 1000,
  "config": "...encoded visual config..."
}
```

- **x, y**: Position from top-left (pixels)
- **width, height**: Size in pixels
- **z**: Z-index for layering (higher = on top)

## Button Actions

Configure button visuals for navigation:

- Page navigation: `{"type":"Navigation","destination":"PageName"}`
- Web URL: `{"type":"OpenUrl","url":"https://..."}`
- Bookmark: `{"type":"SetBookmark","bookmarkName":"BookmarkId"}`

## Data Bar Conditional Formatting

In visual config under `objects.values`:

- `dataBar.positiveColor`: Hex color for positive values
- `dataBar.negativeColor`: Hex color for negative values
- `dataBar.minValue`: Minimum bound (0 or auto)
- `dataBar.maxValue`: Maximum bound (auto or specific)
