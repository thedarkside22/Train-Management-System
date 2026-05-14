import { useEffect, useState } from 'react';
import { Bar, Line } from 'react-chartjs-2';
import {
    Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement,
    BarElement, Title, Tooltip, Legend, Filler,
} from 'chart.js';
import { getDashboardStats, getRevenueTrend, getOccupancy } from '../services/api';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler);

const REFRESH_MS = 30000;

const StatCard = ({ label, value, hint, color = 'blue' }) => {
    const tones = {
        blue: 'bg-blue-50 border-blue-200 text-blue-900',
        green: 'bg-green-50 border-green-200 text-green-900',
        amber: 'bg-amber-50 border-amber-200 text-amber-900',
        purple: 'bg-purple-50 border-purple-200 text-purple-900',
    };
    return (
        <div className={`rounded-lg border p-4 ${tones[color]}`}>
            <div className="text-xs uppercase tracking-wide opacity-70">{label}</div>
            <div className="text-2xl font-bold mt-1">{value}</div>
            {hint && <div className="text-xs mt-1 opacity-70">{hint}</div>}
        </div>
    );
};

const DashboardOverview = () => {
    const [stats, setStats] = useState(null);
    const [trend, setTrend] = useState([]);
    const [occupancy, setOccupancy] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [updatedAt, setUpdatedAt] = useState(null);

    const refresh = async () => {
        try {
            const [s, t, o] = await Promise.all([
                getDashboardStats(),
                getRevenueTrend(14),
                getOccupancy(8),
            ]);
            setStats(s);
            setTrend(t);
            setOccupancy(o);
            setUpdatedAt(new Date());
            setError(null);
        } catch (e) {
            setError(e.message || 'Failed to load dashboard');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        refresh();
        const id = setInterval(refresh, REFRESH_MS);
        return () => clearInterval(id);
    }, []);

    if (loading) return <p className="text-gray-500">Loading dashboard…</p>;
    if (error) return <p className="text-red-600">⚠️ {error}</p>;
    if (!stats) return null;

    const moneyFmt = (v) => `${(v || 0).toFixed(2)} SAR`;

    const lineData = {
        labels: trend.map(p => p.label.slice(5)),
        datasets: [
            {
                label: 'Daily Revenue (SAR)',
                data: trend.map(p => p.revenue),
                borderColor: 'rgb(37, 99, 235)',
                backgroundColor: 'rgba(37, 99, 235, 0.15)',
                fill: true,
                tension: 0.3,
            },
        ],
    };

    const barData = {
        labels: occupancy.map(p => `${p.route} • ${p.departure_date}`),
        datasets: [
            {
                label: 'Occupancy %',
                data: occupancy.map(p => Math.round(p.occupancy_rate * 100)),
                backgroundColor: 'rgba(16, 185, 129, 0.7)',
            },
        ],
    };

    return (
        <div>
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h2 className="text-xl font-bold text-gray-800">Live Operations Overview</h2>
                    <p className="text-xs text-gray-500">
                        Auto-refreshing every {REFRESH_MS / 1000}s {updatedAt && `· last updated ${updatedAt.toLocaleTimeString()}`}
                    </p>
                </div>
                <button onClick={refresh} className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 py-1.5 px-3 rounded font-medium border border-gray-300">🔄 Refresh now</button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                <StatCard label="Total Trains" value={stats.total_trains} hint={`${stats.active_trains} active`} color="blue" />
                <StatCard label="Bookings Today" value={stats.bookings_today} color="green" />
                <StatCard label="Revenue Today" value={moneyFmt(stats.revenue_today)} color="green" />
                <StatCard label="Revenue (7d)" value={moneyFmt(stats.revenue_this_week)} color="amber" />
                <StatCard label="Total Passengers" value={stats.total_passengers} color="purple" />
                <StatCard label="Confirmed" value={stats.confirmed_reservations} color="green" />
                <StatCard label="Cancelled" value={stats.cancelled_reservations} color="amber" />
                <StatCard label="Avg Occupancy" value={`${Math.round(stats.average_occupancy * 100)}%`} color="blue" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Revenue (last 14 days)</h3>
                    <Line data={lineData} options={{ responsive: true, plugins: { legend: { display: false } } }} />
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Top Upcoming Schedules by Occupancy</h3>
                    {occupancy.length === 0
                        ? <p className="text-xs text-gray-500">No upcoming schedules</p>
                        : <Bar data={barData} options={{ indexAxis: 'y', responsive: true, plugins: { legend: { display: false } }, scales: { x: { max: 100 } } }} />}
                </div>
            </div>
        </div>
    );
};

export default DashboardOverview;
