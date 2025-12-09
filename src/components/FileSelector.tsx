import { FileSpreadsheet, Upload } from 'lucide-react';

interface FileSelectorProps {
  onFileSelect: (file: File) => void;
}

export function FileSelector({ onFileSelect }: FileSelectorProps) {
  const handleButtonClick = async () => {
    // Utiliser le dialogue natif Electron
    if (window.electron) {
      try {
        const filePath = await window.electron.selectFile();
        if (filePath) {
          // Créer un objet File-like avec le path pour compatibilité
          const fileObj = { path: filePath, name: filePath.split(/[\\/]/).pop() || '' } as any;
          onFileSelect(fileObj);
        }
      } catch (error) {
        console.error('Erreur lors de la sélection du fichier:', error);
      }
    } else {
      alert('Cette application doit être exécutée dans Electron');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="max-w-2xl w-full space-y-8 text-center">
        {/* Icon */}
        <div className="flex justify-center">
          <div className="relative">
            <div className="absolute inset-0 bg-emerald-500/10 blur-2xl rounded-full" />
            <FileSpreadsheet className="w-20 h-20 text-emerald-400 relative" />
          </div>
        </div>

        {/* Title */}
        <div className="space-y-3">
          <h1 className="text-3xl text-white">
            Choisissez le fichier Excel que vous voulez parser
          </h1>
          <p className="text-zinc-400">
            Sélectionnez un fichier .xlsx ou .xls pour commencer l'analyse
          </p>
        </div>

        {/* File Input */}
        <div className="space-y-4">
          <button
            onClick={handleButtonClick}
            className="group relative inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white rounded-lg overflow-hidden transition-all hover:shadow-lg hover:shadow-emerald-500/30 hover:scale-105"
          >
            <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform" />
            <Upload className="w-5 h-5 relative z-10" />
            <span className="relative z-10">Sélectionner un fichier Excel</span>
          </button>

          <p className="text-sm text-zinc-500">
            Format supporté: .xlsx, .xls
          </p>
        </div>

        {/* Decorative Elements */}
        <div className="pt-12 grid grid-cols-3 gap-6 text-left">
          {[
            { label: 'Rapide', desc: 'Analyse en quelques secondes' },
            { label: 'Précis', desc: 'Calculs statistiques avancés' },
            { label: 'Visuel', desc: 'Graphiques interactifs' }
          ].map((item, i) => (
            <div key={i} className="space-y-1 p-4 bg-zinc-900/50 rounded-lg border border-zinc-800">
              <div className="text-emerald-400">{item.label}</div>
              <div className="text-sm text-zinc-500">{item.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}