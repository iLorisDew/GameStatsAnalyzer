const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 1000,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // En développement
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools(); // Ouvre les DevTools automatiquement
  } else {
    // En production
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// ============================================
// IPC Handlers - Communication avec le frontend
// ============================================

// Sélection de fichier
ipcMain.handle('select-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Excel Files', extensions: ['xlsx', 'xls'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });

  if (result.canceled) {
    return null;
  }

  return result.filePaths[0];
});

// Extraction des headers
ipcMain.handle('extract-headers', async (event, filePath) => {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, '../scripts/extract_headers.py');
    const python = spawn('python', [pythonScript, filePath]);

    let dataString = '';
    let errorString = '';

    python.stdout.on('data', (data) => {
      dataString += data.toString();
    });

    python.stderr.on('data', (data) => {
      errorString += data.toString();
    });

    python.on('close', (code) => {
      if (code === 0) {
        try {
          resolve(JSON.parse(dataString));
        } catch (e) {
          reject(new Error('Failed to parse Python output: ' + e.message));
        }
      } else {
        reject(new Error('Python script failed: ' + errorString));
      }
    });
  });
});

// Processing des données
ipcMain.handle('process-data', async (event, filePath, columns) => {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, '../scripts/process_data.py');
    const python = spawn('python', [
      pythonScript,
      filePath,
      JSON.stringify(columns)
    ]);

    let dataString = '';
    let errorString = '';

    python.stdout.on('data', (data) => {
      dataString += data.toString();
    });

    python.stderr.on('data', (data) => {
      errorString += data.toString();
    });

    python.on('close', (code) => {
      if (code === 0) {
        try {
          resolve(JSON.parse(dataString));
        } catch (e) {
          reject(new Error('Failed to parse Python output: ' + e.message));
        }
      } else {
        reject(new Error('Python script failed: ' + errorString));
      }
    });
  });
});

// Export des données
ipcMain.handle('export-data', async (event, data) => {
  // Demander où sauvegarder
  const result = await dialog.showSaveDialog(mainWindow, {
    filters: [{ name: 'Excel Files', extensions: ['xlsx'] }],
    defaultPath: 'export.xlsx'
  });

  if (result.canceled) {
    return false;
  }

  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, '../scripts/export_data.py');
    const python = spawn('python', [
      pythonScript,
      JSON.stringify(data),
      result.filePath
    ]);

    let errorString = '';

    python.stderr.on('data', (data) => {
      errorString += data.toString();
    });

    python.on('close', (code) => {
      if (code === 0) {
        resolve(true);
      } else {
        reject(new Error('Export failed: ' + errorString));
      }
    });
  });
});