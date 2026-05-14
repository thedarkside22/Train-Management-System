import { useState } from 'react';
import { getReport, downloadReport } from '../services/api';

const ReportsPanel = () => {
    const [period, setPeriod] = useState('weekly');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const generate = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await getReport(period, startDate || undefined, endDate || undefined);
            setReport(data);
        } catch (e) {
            setError(e.message || 'Failed to generate report');
        } finally {
            setLoading(false);
        }
    };

    const exportFile = async (format) => {
        try {
            await downloadReport(format, period, startDate || undefined, endDate || undefined);
        } catch (e) {
            setError(e.message || 'Export failed');
        }
    };

    return (
        <div>
            <h2 className="text-xl font-bold text-gray-800 mb-4">📑 Booking Reports</h2>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">
                <div>
                    <label className="block text-xs text-gray-500 mb-1">Period</label>
                    <select
                        value={period}
                        onChange={e => setPeriod(e.target.value)}
                        className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
                    >
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                    </select>
                </div>
                <div>
                    <label className="block text-xs text-gray-500 mb-1">Start date (optional)</label>
                    <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)}
                        className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                </div>
                <div>
                    <label className="block text-xs text-gray-500 mb-1">End date (optional)</label>
                    <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)}
                        className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                </div>
                <div className="flex items-end gap-2">
                    <button onClick={generate} className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-semibold">
                        Generate
                    </button>
                </div>
            </div>

            {error && <div className="mb-3 p-3 bg-red-50 text-red-800 border border-red-200 rounded text-sm">⚠️ {error}</div>}
            {loading && <p className="text-gray-500">Generating…</p>}

            {report && (
                <div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                        <div className="border border-gray-200 rounded p-3">
                            <div className="text-xs text-gray-500">Bookings</div>
                            <div className="text-xl font-bold">{report.total_bookings}</div>
                        </div>
                        <div className="border border-gray-200 rounded p-3">
                            <div className="text-xs text-gray-500">Cancellations</div>
                            <div className="text-xl font-bold">{report.total_cancellations}</div>
                        </div>
                        <div className="border border-gray-200 rounded p-3">
                            <div className="text-xs text-gray-500">Total Revenue</div>
                            <div className="text-xl font-bold">{report.total_revenue.toFixed(2)} SAR</div>
                        </div>
                        <div className="border border-gray-200 rounded p-3">
                            <div className="text-xs text-gray-500">Avg Daily</div>
                            <div className="text-xl font-bold">{report.average_daily_revenue.toFixed(2)} SAR</div>
                        </div>
                    </div>

                    <div className="flex gap-2 mb-4">
                        <button onClick={() => exportFile('pdf')} className="bg-red-600 text-white px-4 py-2 rounded text-sm font-semibold">⬇ Export PDF</button>
                        <button onClick={() => exportFile('csv')} className="bg-emerald-600 text-white px-4 py-2 rounded text-sm font-semibold">⬇ Export CSV</button>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        <div className="border border-gray-200 rounded">
                            <div className="bg-gray-50 px-3 py-2 text-sm font-semibold text-gray-700 border-b">Daily Breakdown</div>
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="bg-gray-50 text-gray-600">
                                        <th className="text-left p-2">Date</th>
                                        <th className="text-right p-2">Bookings</th>
                                        <th className="text-right p-2">Revenue</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {report.by_day.map(d => (
                                        <tr key={d.date} className="border-t border-gray-100">
                                            <td className="p-2">{d.date}</td>
                                            <td className="p-2 text-right">{d.bookings}</td>
                                            <td className="p-2 text-right">{d.revenue.toFixed(2)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <div className="border border-gray-200 rounded">
                            <div className="bg-gray-50 px-3 py-2 text-sm font-semibold text-gray-700 border-b">Top Routes</div>
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="bg-gray-50 text-gray-600">
                                        <th className="text-left p-2">Route</th>
                                        <th className="text-right p-2">Bookings</th>
                                        <th className="text-right p-2">Revenue</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {report.top_routes.length === 0 && (
                                        <tr><td colSpan="3" className="p-3 text-center text-gray-400 text-xs">No data</td></tr>
                                    )}
                                    {report.top_routes.map((r, i) => (
                                        <tr key={i} className="border-t border-gray-100">
                                            <td className="p-2">{r.origin} → {r.destination}</td>
                                            <td className="p-2 text-right">{r.bookings}</td>
                                            <td className="p-2 text-right">{r.revenue.toFixed(2)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ReportsPanel;
