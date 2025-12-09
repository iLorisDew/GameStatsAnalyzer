import type { ColumnData } from './App';

export interface ProcessDataResult {
  duration: string; // Format: "hh:mm:ss"
  columns: ColumnData[];
}

export interface IElectronAPI {
  selectFile: () => Promise<string>;
  extractHeaders: (filePath: string) => Promise<string[]>;
  processData: (filePath: string, columns: string[]) => Promise<ProcessDataResult>;
  exportData: (data: ColumnData[], outputPath: string) => Promise<boolean>;
}

declare global {
  interface Window {
    electron: IElectronAPI;
  }
}

export {};