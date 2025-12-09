const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  selectFile: () => ipcRenderer.invoke('select-file'),
  extractHeaders: (filePath) => ipcRenderer.invoke('extract-headers', filePath),
  processData: (filePath, columns) => ipcRenderer.invoke('process-data', filePath, columns),
  exportData: (data) => ipcRenderer.invoke('export-data', data)
});