# fixed-table
A simple HTML and JS table with a fixed header row and a fixed leftmost column. The approach is taken from [Fixed Tables JS](https://github.com/webcyou/fixed-table-js).

## Features
- Uses standard html table markup — no extra elements or classes needed. The only requirement is that the table is inside an element with class `fixed-table-container`.
- Uses vanilla JavaScript, so there's no dependencies.
- When users resize the browser window, column widths are updated using the default HTML table layout algorithm.

## Limitations
- Cell heights are incorrect when a row contains cells of varying heights. To avoid this, do not wrap cell content (e.g., by using `white-space: nowrap !important;`). Avoid long content in the fixed column so that it doesn't overwhelm narrow viewports.

## Usage
```
// Initialize table
var myFixedTable = fixTable(document.getElementById('my-fixed-table-container'));

// Programatically re-layout the table (e.g., after changing the number of columns, or changing content)
myFixedTable.relayout();
```
