# Excel Analytics Pro - Frontend

Une interface React moderne avec thème sombre pour votre application d'analyse Excel basée sur Python/Pandas.

## 📁 Structure du projet

```
/
├── App.tsx                      # Composant principal avec gestion des états
├── components/
│   ├── Splashscreen.tsx        # Écran de chargement (3 secondes)
│   ├── FileSelector.tsx        # Sélecteur de fichier Excel (dialogue natif)
│   ├── ColumnSelector.tsx      # Dialogue de sélection des colonnes
│   └── Results.tsx             # Affichage tableau + graphiques + durée
├── electron.d.ts               # Types TypeScript pour Electron API
└── README.md
```

## 🚀 Installation

```bash
# Les dépendances sont automatiquement gérées
# Packages utilisés:
# - react
# - lucide-react (icônes)
# - recharts (graphiques)
```

## 🔌 Intégration avec Electron

### 1. Installation d'Electron dans votre projet

```bash
npm install electron electron-builder
npm install --save-dev concurrently wait-on cross-env
```

### 2. Créer le fichier principal Electron (`electron/main.js`)

```javascript
const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 1000,    // Largeur minimale
    minHeight: 700,    // Hauteur minimale
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // En développement
  mainWindow.loadURL('http://localhost:5173');
  
  // En production
  // mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (pythonProcess) pythonProcess.kill();
  if (process.platform !== 'darwin') app.quit();
});

// IPC Handlers pour communiquer avec Python
ipcMain.handle('select-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [{ name: 'Excel Files', extensions: ['xlsx', 'xls'] }]
  });
  return result.filePaths[0];
});

ipcMain.handle('extract-headers', async (event, filePath) => {
  return new Promise((resolve, reject) => {
    // Appeler votre script Python
    const python = spawn('python', ['scripts/extract_headers.py', filePath]);
    let dataString = '';

    python.stdout.on('data', (data) => {
      dataString += data.toString();
    });

    python.on('close', (code) => {
      if (code === 0) {
        resolve(JSON.parse(dataString));
      } else {
        reject(new Error('Python script failed'));
      }
    });
  });
});

ipcMain.handle('process-data', async (event, filePath, columns) => {
  return new Promise((resolve, reject) => {
    const python = spawn('python', [
      'scripts/process_data.py',
      filePath,
      JSON.stringify(columns)
    ]);
    let dataString = '';

    python.stdout.on('data', (data) => {
      dataString += data.toString();
    });

    python.on('close', (code) => {
      if (code === 0) {
        resolve(JSON.parse(dataString));
      } else {
        reject(new Error('Python script failed'));
      }
    });
  });
});

ipcMain.handle('export-data', async (event, data, outputPath) => {
  return new Promise((resolve, reject) => {
    const python = spawn('python', [
      'scripts/export_data.py',
      JSON.stringify(data),
      outputPath
    ]);

    python.on('close', (code) => {
      if (code === 0) {
        resolve(true);
      } else {
        reject(new Error('Export failed'));
      }
    });
  });
});
```

### 3. Créer le preload script (`electron/preload.js`)

```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  selectFile: () => ipcRenderer.invoke('select-file'),
  extractHeaders: (filePath) => ipcRenderer.invoke('extract-headers', filePath),
  processData: (filePath, columns) => ipcRenderer.invoke('process-data', filePath, columns),
  exportData: (data, outputPath) => ipcRenderer.invoke('export-data', data, outputPath)
});
```

### 4. Modifier votre `package.json`

```json
{
  "name": "excel-analytics-pro",
  "version": "1.0.0",
  "main": "electron/main.js",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "electron": "electron .",
    "electron-dev": "concurrently \"npm run dev\" \"wait-on http://localhost:5173 && electron .\"",
    "electron-build": "npm run build && electron-builder"
  },
  "build": {
    "appId": "com.yourcompany.excelanalytics",
    "files": ["dist/**/*", "electron/**/*"],
    "directories": {
      "buildResources": "assets"
    }
  }
}
```

## 🐍 Intégration Backend Python

### Points d'intégration dans le code React

#### 1. **App.tsx - Ligne 38** : Extraction des headers

Remplacez:
```typescript
const mockHeaders = ['Temperature', 'Pressure', 'Velocity', 'Power', 'Efficiency'];
setAvailableColumns(mockHeaders);
```

Par:
```typescript
const headers = await window.electron.extractHeaders(file.path);
setAvailableColumns(headers);
```

#### 2. **App.tsx - Ligne 47** : Processing des données

Remplacez:
```typescript
const mockResults: ResultsMetadata = {
  duration: "00:34:24",
  columns: mockColumns
};
```

Par:
```typescript
const results = await window.electron.processData(selectedFile.path, columns);
setResultsData(results); // results contient { duration: "hh:mm:ss", columns: [...] }
```

#### 3. **App.tsx - Ligne 74** : Export des données

Remplacez:
```typescript
console.log('Exporting data...', resultsData);
alert('Export en cours...');
```

Par:
```typescript
await window.electron.exportData(resultsData, './output.xlsx');
alert('Export réussi!');
```

### Scripts Python requis

Créez ces scripts dans un dossier `scripts/`:

#### `scripts/extract_headers.py`
```python
import sys
import pandas as pd
import json

def extract_headers(file_path):
    df = pd.read_excel(file_path)
    headers = df.columns.tolist()
    print(json.dumps(headers))

if __name__ == '__main__':
    extract_headers(sys.argv[1])
```

#### `scripts/process_data.py`
```python
import sys
import pandas as pd
import json
from datetime import timedelta

def process_data(file_path, columns):
    df = pd.read_excel(file_path)
    results = []
    
    # Calculer la durée totale (exemple basé sur une colonne temps)
    # Adaptez selon votre logique métier
    if 'Time' in df.columns:
        total_seconds = df['Time'].max()  # ou autre logique
        duration = str(timedelta(seconds=int(total_seconds)))
    else:
        duration = "00:00:00"
    
    for col in columns:
        if col in df.columns:
            col_data = df[col]
            
            # Calculs
            moyenne = float(col_data.mean())
            minimum = float(col_data.min())
            maximum = float(col_data.max())
            one_pct_low = float(col_data.quantile(0.01))
            
            # Time series data
            time_series = [
                {"time": i, "value": float(val)}
                for i, val in enumerate(col_data.values)
            ]
            
            results.append({
                "name": col,
                "moyenne": moyenne,
                "min": minimum,
                "max": maximum,
                "onePctLow": one_pct_low,
                "timeSeriesData": time_series
            })
    
    # Retourner les données avec la durée
    output = {
        "duration": duration,
        "columns": results
    }
    
    print(json.dumps(output))

if __name__ == '__main__':
    file_path = sys.argv[1]
    columns = json.loads(sys.argv[2])
    process_data(file_path, columns)
```

#### `scripts/export_data.py`
```python
import sys
import json
import pandas as pd

def export_data(data, output_path):
    # Votre logique d'export existante
    # Exemple:
    results = json.loads(data)
    
    export_df = pd.DataFrame([
        {
            "Colonne": r["name"],
            "Moyenne": r["moyenne"],
            "Min": r["min"],
            "Max": r["max"],
            "1% Low": r["onePctLow"]
        }
        for r in results
    ])
    
    export_df.to_excel(output_path, index=False)

if __name__ == '__main__':
    data = sys.argv[1]
    output_path = sys.argv[2]
    export_data(data, output_path)
```

## 📝 Notes importantes

### Affichage de la durée

La durée s'affiche dans un composant élégant au-dessus du tableau des résultats:
- Format attendu: `"hh:mm:ss"` (ex: "00:34:24")
- Affichage avec icône horloge et style gradient
- Police monospace pour un alignement parfait des chiffres

Votre script Python doit calculer cette durée et la retourner dans le format JSON:
```json
{
  "duration": "00:34:24",
  "columns": [...]
}
```

### TypeScript Definitions

Ajoutez dans un fichier `electron.d.ts`:
```typescript
export interface IElectronAPI {
  selectFile: () => Promise<string>;
  extractHeaders: (filePath: string) => Promise<string[]>;
  processData: (filePath: string, columns: string[]) => Promise<{
    duration: string;  // Format: "hh:mm:ss"
    columns: ColumnData[];
  }>;
  exportData: (data: ColumnData[], outputPath: string) => Promise<boolean>;
}

declare global {
  interface Window {
    electron: IElectronAPI;
  }
}
```

### Gestion des fichiers

Pour le sélecteur de fichier, vous avez deux options:

**Option 1 - Dialogue natif Electron** (recommandé):
```typescript
const filePath = await window.electron.selectFile();
// Utiliser filePath au lieu de l'objet File
```

**Option 2 - Input HTML** (mode web uniquement):
Gardez le code actuel avec `<input type="file">`

### Distribution de Python avec votre app

Pour distribuer votre application:

1. **PyInstaller** - Convertir vos scripts Python en exécutables:
```bash
pip install pyinstaller
pyinstaller --onefile scripts/process_data.py
```

2. **Inclure Python** - Embarquer Python avec votre app:
   - Utilisez `python-shell` npm package
   - Ou distribuez un environnement Python portable

3. **Alternative** - Backend séparé:
   - Créez une API Flask/FastAPI
   - Communiquez via HTTP au lieu d'IPC

### Packaging final

```bash
# Build de l'application complète
npm run build
npm run electron-build

# Cela créera des installateurs pour votre plateforme
# Les fichiers seront dans le dossier dist/
```

## 🎨 Personnalisation du thème

Les couleurs principales sont dans `tailwind.config.js` et `/styles/globals.css`:
- Accent principal: Emerald (`#10b981`)
- Accent secondaire: Cyan (`#06b6d4`)
- Background: Zinc-950 (`#09090b`)

## 🔧 Développement

```bash
# Mode développement (React uniquement)
npm run dev

# Mode développement avec Electron
npm run electron-dev
```

## ⚡ Performance

- Le splashscreen dure exactement 3 secondes
- Les animations utilisent CSS transforms pour de meilleures performances
- Les graphiques sont optimisés avec `recharts` (basé sur D3)

## 🐛 Debugging

Pour débugger l'intégration Python:
1. Ajoutez `console.log()` dans vos IPC handlers
2. Utilisez Chrome DevTools dans Electron (`Ctrl+Shift+I`)
3. Vérifiez les sorties Python avec `stderr`

## 📦 Dépendances Python

Assurez-vous d'avoir installé:
```bash
pip install pandas openpyxl xlrd
```

## 🖥️ Taille de fenêtre et Responsive

### Configuration recommandée pour Desktop

L'interface est **responsive par défaut**, ce qui permet à l'utilisateur de redimensionner la fenêtre. Configuration recommandée dans Electron:

```javascript
// electron/main.js
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,        // Taille par défaut
    height: 800,
    minWidth: 1000,     // Empêche la fenêtre d'être trop petite
    minHeight: 700,
    // resizable: true,  // Par défaut: permet le redimensionnement
  });
}
```

### Options selon vos besoins

**1. Fenêtre redimensionnable (RECOMMANDÉ)**
```javascript
{
  width: 1200,
  height: 800,
  minWidth: 1000,     // Taille minimale pour éviter de casser l'UI
  minHeight: 700,
  resizable: true     // Par défaut
}
```
✅ Flexible pour différentes tailles d'écran  
✅ L'utilisateur peut agrandir pour voir plus de données  
✅ Fonctionne sur petits et grands écrans  

**2. Fenêtre fixe**
```javascript
{
  width: 1200,
  height: 800,
  resizable: false    // Désactive le redimensionnement
}
```
✅ Interface constante, aucune surprise visuelle  
❌ Moins flexible  

**3. Plein écran disponible**
```javascript
{
  width: 1200,
  height: 800,
  minWidth: 1000,
  minHeight: 700,
  fullscreenable: true,  // Permet le plein écran (F11)
}
```

### Layout responsive actuel

L'interface s'adapte automatiquement:
- **Stats Summary**: `grid-cols-2 md:grid-cols-4` (2 colonnes sur petits écrans, 4 sur grands)
- **Tableau**: Scroll horizontal automatique si trop large
- **Graphiques**: S'adaptent à la largeur disponible
- **Padding/Margins**: Optimisés pour toutes les tailles

---

**Bon développement! 🚀**

Pour toute question sur l'intégration, référez-vous à:
- [Documentation Electron](https://www.electronjs.org/docs)
- [Documentation Vite](https://vitejs.dev/)
- [Documentation Pandas](https://pandas.pydata.org/)