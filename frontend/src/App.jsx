import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast, { Toaster } from 'react-hot-toast';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import {
  Upload, FileText, BarChart2, LayoutDashboard,
  Download, Loader2, Database, History, ChevronRight
} from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
);

const API_BASE = 'http://localhost:8000/api';
const AUTH_HEADER = {
  headers: {
    'Authorization': 'Basic ' + btoa('admin:admin123')
  }
};

const CHART_THEME = {
  backgroundColor: ['#ffffff', '#a1a1aa', '#52525b', '#27272a', '#18181b'],
  borderColor: 'rgba(255, 255, 255, 0.1)',
};

function App() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchHistory();
    fetchLatestSummary();
  }, []);

  const fetchHistory = async () => {
    try {
      const resp = await axios.get(`${API_BASE}/history/`, AUTH_HEADER);
      setHistory(resp.data);
    } catch (err) {
      console.error("Error fetching history", err);
    }
  };

  const fetchLatestSummary = async () => {
    try {
      const resp = await axios.get(`${API_BASE}/summary/latest/`, AUTH_HEADER);
      if (resp.data) setData(resp.data);
    } catch (err) {
      console.error("Error fetching latest summary", err);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    const uploadToast = toast.loading('Processing equipment data...');

    try {
      const resp = await axios.post(`${API_BASE}/upload/`, formData, {
        headers: {
          ...AUTH_HEADER.headers
        }
      });
      setData(resp.data);
      fetchHistory();
      toast.success('Analysis complete!', { id: uploadToast });
      setFile(null); // Reset file input
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.message;
      toast.error(`Upload failed: ${errorMsg}`, { id: uploadToast });
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = async (id) => {
    const downloadToast = toast.loading('Generating PDF report...');
    try {
      const resp = await axios.get(`${API_BASE}/report/${id}/`, {
        ...AUTH_HEADER,
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([resp.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Equipment_Report_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      toast.success('Report downloaded', { id: downloadToast });
    } catch (err) {
      toast.error('Failed to generate report', { id: downloadToast });
    }
  };

  const chartData = data ? {
    labels: Object.keys(data.type_distribution),
    datasets: [{
      label: 'Units',
      data: Object.values(data.type_distribution),
      backgroundColor: CHART_THEME.backgroundColor,
      borderWidth: 0,
    }]
  } : null;

  return (
    <div className="min-h-screen pb-12">
      <Toaster position="top-right" toastOptions={{
        style: {
          background: '#18181b',
          color: '#fff',
          border: '1px solid rgba(255,255,255,0.1)'
        }
      }} />

      <div className="container mx-auto p-6 space-y-8">
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center glass-card gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-white rounded-lg">
              <LayoutDashboard className="text-black w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">Chemical Visualizer</h1>
              <p className="text-xs text-muted">Advanced Equipment Analytics</p>
            </div>
          </div>

          <div className="flex items-center space-x-3 w-full md:w-auto">
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
              className="hidden"
              id="file-upload"
              accept=".csv"
            />
            <label
              htmlFor="file-upload"
              className={`btn btn-secondary flex-1 md:flex-none flex items-center justify-center space-x-2 ${file ? 'border-white/40' : ''}`}
            >
              <FileText size={18} />
              <span className="truncate max-w-[150px]">{file ? file.name : 'Select CSV'}</span>
            </label>
            <button
              onClick={handleUpload}
              disabled={!file || loading}
              className="btn btn-primary flex-1 md:flex-none flex items-center justify-center space-x-2"
            >
              {loading ? <Loader2 className="animate-spin" size={18} /> : <Upload size={18} />}
              <span>{loading ? 'Processing...' : 'Upload & Process'}</span>
            </button>
          </div>
        </header>

        {!data && !loading && (
          <div className="flex flex-col items-center justify-center py-20 text-center space-y-4 opacity-50">
            <Database size={64} className="text-muted" />
            <div>
              <h2 className="text-2xl font-semibold">No Data Analyzed</h2>
              <p>Upload a CSV file to view real-time equipment parameters</p>
            </div>
          </div>
        )}

        {data && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 space-y-8">
            <section className="grid-cols-stats">
              <StatCard label="Total Units" value={data.total_count} icon={<Database />} />
              <StatCard label="Avg Flowrate" value={data.avg_flowrate.toFixed(1)} unit="m³/h" icon={<BarChart2 />} />
              <StatCard label="Avg Pressure" value={data.avg_pressure.toFixed(1)} unit="bar" icon={<BarChart2 />} />
              <StatCard label="Avg Temp" value={data.avg_temperature.toFixed(1)} unit="°C" icon={<BarChart2 />} />
            </section>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="glass-card">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <BarChart2 size={18} /> Distribution
                  </h3>
                </div>
                <div className="h-[300px] flex items-center justify-center">
                  {chartData && <Pie data={chartData} options={{ maintainAspectRatio: false }} />}
                </div>
              </div>
              <div className="glass-card">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <BarChart2 size={18} /> Comparison
                  </h3>
                </div>
                <div className="h-[300px]">
                  {chartData && <Bar data={chartData} options={{
                    maintainAspectRatio: false,
                    scales: {
                      y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                      x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                    },
                    plugins: { legend: { display: false } }
                  }} />}
                </div>
              </div>
            </div>

            <div className="glass-card">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <Database size={18} /> Component Inventory
                </h3>
                <button
                  onClick={() => downloadPDF(data.id)}
                  className="btn btn-secondary flex items-center space-x-2 text-sm"
                >
                  <Download size={16} />
                  <span>Download Report</span>
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="text-muted text-sm border-b border-white/5">
                      <th className="pb-4 font-medium">Equipment Name</th>
                      <th className="pb-4 font-medium">Type</th>
                      <th className="pb-4 font-medium">Flowrate</th>
                      <th className="pb-4 font-medium">Pressure</th>
                      <th className="pb-4 font-medium">Temperature</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {data.equipment_records?.map((rec, i) => (
                      <tr key={i} className="group hover:bg-white/5 transition-colors">
                        <td className="py-4 font-medium">{rec.name}</td>
                        <td className="py-4 text-muted">{rec.equipment_type}</td>
                        <td className="py-4 text-muted">{rec.flowrate} <span className="text-[10px]">m³/h</span></td>
                        <td className="py-4 text-muted">{rec.pressure} <span className="text-[10px]">bar</span></td>
                        <td className="py-4 text-muted">{rec.temperature} <span className="text-[10px]">°C</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        <footer className="glass-card">
          <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
            <History size={18} /> Analysis History
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {history.map((h) => (
              <div key={h.id} className="p-4 rounded-lg bg-zinc-900/50 border border-white/5 flex justify-between items-center group">
                <div className="space-y-1">
                  <p className="text-sm font-medium">{h.filename || 'equipment_data.csv'}</p>
                  <p className="text-[10px] text-muted">{new Date(h.uploaded_at).toLocaleString()}</p>
                </div>
                <button
                  onClick={() => downloadPDF(h.id)}
                  className="p-2 rounded-md hover:bg-white/10 text-muted hover:text-white transition-all"
                >
                  <Download size={16} />
                </button>
              </div>
            ))}
          </div>
        </footer>
      </div>
    </div>
  );
}

function StatCard({ label, value, unit, icon }) {
  return (
    <div className="stat-card">
      <div className="p-3 bg-zinc-800 rounded-lg text-white">
        {icon}
      </div>
      <div>
        <p className="text-muted text-xs uppercase tracking-wider">{label}</p>
        <p className="text-2xl font-bold flex items-baseline gap-1">
          {value}
          <span className="text-xs font-normal text-muted">{unit}</span>
        </p>
      </div>
    </div>
  );
}

export default App;
