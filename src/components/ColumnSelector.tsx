import { useState } from 'react';
import { Check, ChevronRight, ArrowLeft } from 'lucide-react';

interface ColumnSelectorProps {
  columns: string[];
  onConfirm: (selectedColumns: string[]) => void;
  onBack: () => void;
}

export function ColumnSelector({ columns, onConfirm, onBack }: ColumnSelectorProps) {
  const [selected, setSelected] = useState<string[]>([]);

  const toggleColumn = (column: string) => {
    setSelected(prev =>
      prev.includes(column)
        ? prev.filter(c => c !== column)
        : [...prev, column]
    );
  };

  const handleConfirm = () => {
    if (selected.length > 0) {
      onConfirm(selected);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="max-w-2xl w-full space-y-8">
        {/* Header */}
        <div className="text-center space-y-3">
          <h1 className="text-3xl text-white">
            Sélectionnez les colonnes à analyser
          </h1>
          <p className="text-zinc-400">
            {selected.length} colonne{selected.length !== 1 ? 's' : ''} sélectionnée{selected.length !== 1 ? 's' : ''}
          </p>
        </div>

        {/* Column List */}
        <div className="bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden">
          <div className="max-h-96 overflow-y-auto">
            {columns.map((column, index) => {
              const isSelected = selected.includes(column);
              return (
                <button
                  key={index}
                  onClick={() => toggleColumn(column)}
                  className="w-full flex items-center gap-4 px-6 py-4 hover:bg-zinc-800/50 transition-colors border-b border-zinc-800 last:border-b-0"
                >
                  {/* Checkbox */}
                  <div
                    className={`w-6 h-6 rounded-md border-2 flex items-center justify-center transition-all ${
                      isSelected
                        ? 'bg-emerald-500 border-emerald-500'
                        : 'border-zinc-600'
                    }`}
                  >
                    {isSelected && <Check className="w-4 h-4 text-white" />}
                  </div>

                  {/* Column Name */}
                  <span className={`flex-1 text-left ${
                    isSelected ? 'text-white' : 'text-zinc-300'
                  }`}>
                    {column}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <button
            onClick={onBack}
            className="flex items-center gap-2 px-6 py-3 bg-zinc-800 text-zinc-300 rounded-lg hover:bg-zinc-700 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Retour
          </button>

          <button
            onClick={handleConfirm}
            disabled={selected.length === 0}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white rounded-lg hover:shadow-lg hover:shadow-emerald-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none"
          >
            Confirmer la sélection
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
