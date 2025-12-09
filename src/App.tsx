import { useState, useEffect } from 'react';
import { Splashscreen } from './components/Splashscreen';
import { FileSelector } from './components/FileSelector';
import { ColumnSelector } from './components/ColumnSelector';
import { Results } from './components/Results';

export type AppStep = 'splash' | 'fileSelect' | 'columnSelect' | 'results';

export interface ColumnData {
  name: string;
  moyenne: number;
  min: number;
  max: number;
  onePctLow: number;
  timeSeriesData: { time: number; value: number }[];
}

export interface ResultsMetadata {
  duration: string; // Format: "hh:mm:ss"
  columns: ColumnData[];
}

function App() {
  const [step, setStep] = useState<AppStep>('splash');
  // @ts-ignore
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [availableColumns, setAvailableColumns] = useState<string[]>([]);
  // @ts-ignore
  const [selectedColumns, setSelectedColumns] = useState<string[]>([]);
  const [resultsData, setResultsData] = useState<ResultsMetadata | null>(null);

  useEffect(() => {
    // Auto-transition from splash after loading
    if (step === 'splash') {
      const timer = setTimeout(() => {
        setStep('fileSelect');
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [step]);

  const handleFileSelect = async (file: any) => {
    setSelectedFile(file);
    
    // Extraction des headers via Python/Electron
    // En production, décommentez ceci:
    // const headers = await window.electron.extractHeaders(file.path);
    
    // Mock pour développement:
    const mockHeaders = ['Temperature', 'Pressure', 'Velocity', 'Power', 'Efficiency'];
    setAvailableColumns(mockHeaders);
    setStep('columnSelect');
  };

  const handleColumnsConfirm = async (columns: string[]) => {
    setSelectedColumns(columns);
    
    // Processing des données via Python/Electron
    // En production, décommentez ceci:
    // const results = await window.electron.processData(selectedFile.path, columns);
    // setResultsData(results);
    
    // Mock pour développement:
    const mockColumns: ColumnData[] = columns.map(col => ({
      name: col,
      moyenne: Math.random() * 100,
      min: Math.random() * 50,
      max: Math.random() * 150,
      onePctLow: Math.random() * 40,
      timeSeriesData: Array.from({ length: 50 }, (_, i) => ({
        time: i,
        value: Math.random() * 100 + 50
      }))
    }));
    
    const mockResults: ResultsMetadata = {
      duration: "00:34:24", // Durée mock
      columns: mockColumns
    };
    
    setResultsData(mockResults);
    setStep('results');
  };

  const handleBack = () => {
    setStep('fileSelect');
    setSelectedFile(null);
    setAvailableColumns([]);
    setSelectedColumns([]);
    setResultsData(null);
  };

  const handleExport = async () => {
    // Export via Python/Electron
    // En production, décommentez ceci:
    // await window.electron.exportData(resultsData, './export.xlsx');
    // alert('Export réussi!');
    
    // Mock pour développement:
    console.log('Exporting data...', resultsData);
    alert('Export en cours... (Connectez votre fonction Python ici)');
  };

  return (
    <div className="min-h-screen bg-zinc-950">
      {step === 'splash' && <Splashscreen />}
      {step === 'fileSelect' && <FileSelector onFileSelect={handleFileSelect} />}
      {step === 'columnSelect' && (
        <ColumnSelector
          columns={availableColumns}
          onConfirm={handleColumnsConfirm}
          onBack={() => setStep('fileSelect')}
        />
      )}
      {step === 'results' && resultsData && (
        <Results
          data={resultsData.columns}
          duration={resultsData.duration}
          onBack={handleBack}
          onExport={handleExport}
        />
      )}
    </div>
  );
}

export default App;