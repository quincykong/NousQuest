// exportUtils.js
import * as XLSX from 'xlsx';

export const exportToExcel = ({ rows, columnOrder, headerTranslations = {}, transformations = {}, filename = 'ExportedData.xlsx' }) => {
  // Preprocess the data, apply transformations if provided
  const processedRows = rows.map((row) => {
    const transformedRow = { ...row };
    Object.keys(transformations).forEach((key) => {
      if (row.hasOwnProperty(key)) {
        transformedRow[key] = transformations[key](row[key]); // Apply transformation function
      }
    });
    return transformedRow;
  });

  // Ensure the columns follow the desired order
  const orderedRows = processedRows.map((row) => {
    const orderedRow = {};
    columnOrder.forEach((column) => {
      orderedRow[column] = row[column];
    });
    return orderedRow;
  });

  // Create header row using the columnOrder and headerTranslations
  const headers = columnOrder.map((column) => headerTranslations[column] || column);  // Fallback to column name if no translation

  // Combine headers with the orderedRows data
  const dataWithHeaders = [headers, ...orderedRows.map(Object.values)];

  // Convert the rows to a worksheet and export as Excel file
  const ws = XLSX.utils.aoa_to_sheet(dataWithHeaders);  // Use aoa_to_sheet for arrays
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'DataExport');
  XLSX.writeFile(wb, filename);
};
