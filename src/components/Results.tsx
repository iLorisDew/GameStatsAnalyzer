import { useState } from 'react';
import { ArrowLeft, Download, Table as TableIcon, LineChart, Clock } from 'lucide-react';
import { LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { ColumnData } from '../App';

interface ResultsProps {
  data: ColumnData[];
  duration: string; // Format: "hh:mm:ss"
  onBack: () => void;
  onExport: () => void;
}

type ViewMode = 'table' | 'chart';

export function Results({ data, duration, onBack, onExport }: ResultsProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('table');

  // Prepare chart data by merging all time series
  const chartData = data[0]?.timeSeriesData.map((point, index) => {
    const dataPoint: any = { time: point.time };
    data.forEach(col => {
      dataPoint[col.name] = col.timeSeriesData[index]?.value || 0;
    });
    return dataPoint;
  }) || [];

  const colors = ['#10b981', '#06b6d4', '#8b5cf6', '#f59e0b', '#ef4444'];

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h1 className="text-3xl text-white">Résultats de l'analyse</h1>
            <p className="text-zinc-400">
              {data.length} colonne{data.length !== 1 ? 's' : ''} analysée{data.length !== 1 ? 's' : ''}
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={onBack}
              className="flex items-center gap-2 px-4 py-2 bg-zinc-800 text-zinc-300 rounded-lg hover:bg-zinc-700 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Retour
            </button>
            <button
              onClick={onExport}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white rounded-lg hover:shadow-lg hover:shadow-emerald-500/30 transition-all"
            >
              <Download className="w-4 h-4" />
              Exporter
            </button>
          </div>
        </div>

        {/* View Mode Toggle */}
        <div className="flex gap-2 bg-zinc-900 p-1 rounded-lg w-fit border border-zinc-800">
          <button
            onClick={() => setViewMode('table')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition-all ${
              viewMode === 'table'
                ? 'bg-emerald-500 text-white'
                : 'text-zinc-400 hover:text-zinc-300'
            }`}
          >
            <TableIcon className="w-4 h-4" />
            Tableau
          </button>
          <button
            onClick={() => setViewMode('chart')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition-all ${
              viewMode === 'chart'
                ? 'bg-emerald-500 text-white'
                : 'text-zinc-400 hover:text-zinc-300'
            }`}
          >
            <LineChart className="w-4 h-4" />
            Graphique
          </button>
        </div>

        {/* Duration Display */}
        <div className="flex justify-center">
          <div className="inline-flex items-center gap-3 px-6 py-4 bg-gradient-to-r from-zinc-900 to-zinc-800 border border-zinc-700 rounded-xl shadow-lg">
            <Clock className="w-6 h-6 text-emerald-400" />
            <div className="flex flex-col">
              <span className="text-xs text-zinc-400">Durée totale</span>
              <span className="text-2xl text-white tabular-nums tracking-wider">
                {duration}
              </span>
            </div>
          </div>
        </div>

        {/* Content */}
        {viewMode === 'table' ? (
          <div className="bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-zinc-800/50">
                  <tr>
                    <th className="px-6 py-4 text-left text-zinc-300">Colonne</th>
                    <th className="px-6 py-4 text-right text-zinc-300">Moyenne</th>
                    <th className="px-6 py-4 text-right text-zinc-300">Min</th>
                    <th className="px-6 py-4 text-right text-zinc-300">Max</th>
                    <th className="px-6 py-4 text-right text-zinc-300">1% Low</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800">
                  {data.map((col, index) => (
                    <tr key={index} className="hover:bg-zinc-800/30 transition-colors">
                      <td className="px-6 py-4 text-white">{col.name}</td>
                      <td className="px-6 py-4 text-right text-emerald-400">
                        {col.moyenne.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 text-right text-blue-400">
                        {col.min.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 text-right text-orange-400">
                        {col.max.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 text-right text-purple-400">
                        {col.onePctLow.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-6">
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsLineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis
                    dataKey="time"
                    stroke="#71717a"
                    label={{ value: 'Temps', position: 'insideBottom', offset: -5, fill: '#a1a1aa' }}
                  />
                  <YAxis
                    stroke="#71717a"
                    label={{ value: 'Valeur', angle: -90, position: 'insideLeft', fill: '#a1a1aa' }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#18181b',
                      border: '1px solid #27272a',
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                  />
                  <Legend />
                  {data.map((col, index) => (
                    <Line
                      key={col.name}
                      type="monotone"
                      dataKey={col.name}
                      stroke={colors[index % colors.length]}
                      strokeWidth={2}
                      dot={false}
                    />
                  ))}
                </RechartsLineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Stats Summary */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
            <div className="text-sm text-zinc-400">Colonnes analysées</div>
            <div className="text-2xl text-white mt-1">{data.length}</div>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
            <div className="text-sm text-zinc-400">Points de données</div>
            <div className="text-2xl text-white mt-1">{data[0]?.timeSeriesData.length || 0}</div>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
            <div className="text-sm text-zinc-400">Moyenne globale</div>
            <div className="text-2xl text-emerald-400 mt-1">
              {(data.reduce((acc, col) => acc + col.moyenne, 0) / data.length).toFixed(2)}
            </div>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
            <div className="text-sm text-zinc-400">Max global</div>
            <div className="text-2xl text-orange-400 mt-1">
              {Math.max(...data.map(col => col.max)).toFixed(2)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}