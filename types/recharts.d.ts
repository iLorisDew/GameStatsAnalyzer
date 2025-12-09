declare module 'recharts/es6/component/Legend' {
    interface LegendProps {
      payload?: Array<{ value: string | number; color?: string; dataKey?: string; type?: string }>;
      verticalAlign?: 'top' | 'middle' | 'bottom';
      // Ajoute d'autres props si besoin
    }
    export const LegendProps: LegendProps;  // Placeholder pour export
  }