import { useEffect, useState } from 'react';
import { getAnalyticsEDA, getAnalyticsFeatures } from '../services/api';

const AnalyticsPanel = () => {
    const [eda, setEda] = useState(null);
    const [features, setFeatures] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        (async () => {
            try {
                const [e, f] = await Promise.all([getAnalyticsEDA(), getAnalyticsFeatures(20)]);
                setEda(e);
                setFeatures(f);
            } catch (err) {
                setError(err.message || 'Failed to load analytics');
            } finally {
                setLoading(false);
            }
        })();
    }, []);

    if (loading) return <p className="text-gray-500">Loading analytics…</p>;
    if (error) return <p className="text-red-600">⚠️ {error}</p>;

    return (
        <div>
            <h2 className="text-xl font-bold text-gray-800 mb-4">🤖 Booking Analytics & Feature Engineering</h2>
            <p className="text-xs text-gray-500 mb-4">
                Sprint 3 (US-015): historical booking data is collected, summarised, and feature-engineered for downstream ML models.
            </p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                <div className="border border-gray-200 rounded p-3">
                    <div className="text-xs text-gray-500">Rows</div>
                    <div className="text-xl font-bold">{eda?.rows ?? 0}</div>
                </div>
                <div className="border border-gray-200 rounded p-3">
                    <div className="text-xs text-gray-500">Unique Passengers</div>
                    <div className="text-xl font-bold">{eda?.unique_passengers ?? 0}</div>
                </div>
                <div className="border border-gray-200 rounded p-3">
                    <div className="text-xs text-gray-500">Unique Routes</div>
                    <div className="text-xl font-bold">{eda?.unique_routes ?? 0}</div>
                </div>
                <div className="border border-gray-200 rounded p-3">
                    <div className="text-xs text-gray-500">Total Revenue</div>
                    <div className="text-xl font-bold">{(eda?.total_revenue ?? 0).toFixed(2)} SAR</div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div className="border border-gray-200 rounded">
                    <div className="bg-gray-50 px-3 py-2 text-sm font-semibold border-b">Top Routes</div>
                    <table className="w-full text-sm">
                        <thead><tr className="bg-gray-50 text-gray-600">
                            <th className="text-left p-2">Origin</th>
                            <th className="text-left p-2">Destination</th>
                            <th className="text-right p-2">Bookings</th>
                        </tr></thead>
                        <tbody>
                            {(eda?.top_routes || []).map((r, i) => (
                                <tr key={i} className="border-t border-gray-100">
                                    <td className="p-2">{r.origin}</td>
                                    <td className="p-2">{r.destination}</td>
                                    <td className="p-2 text-right">{r.bookings}</td>
                                </tr>
                            ))}
                            {(!eda?.top_routes || eda.top_routes.length === 0) && (
                                <tr><td colSpan="3" className="p-3 text-center text-gray-400 text-xs">No data</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>

                <div className="border border-gray-200 rounded">
                    <div className="bg-gray-50 px-3 py-2 text-sm font-semibold border-b">Engineered Features (preview)</div>
                    <div className="p-3 text-xs text-gray-600">
                        <div className="mb-2">
                            <b>Columns:</b> {features?.columns?.join(', ') || 'none'}
                        </div>
                        <div>
                            <b>Sample rows:</b> {features?.preview?.length || 0} of {features?.rows || 0}
                        </div>
                    </div>
                    <div className="overflow-x-auto max-h-64">
                        <table className="w-full text-xs">
                            <thead className="bg-gray-50 text-gray-600">
                                <tr>
                                    <th className="p-1.5 text-left">ref</th>
                                    <th className="p-1.5 text-right">dow</th>
                                    <th className="p-1.5 text-right">weekend</th>
                                    <th className="p-1.5 text-right">holiday</th>
                                    <th className="p-1.5 text-right">hour</th>
                                    <th className="p-1.5 text-right">lead_days</th>
                                    <th className="p-1.5 text-right">occupancy</th>
                                </tr>
                            </thead>
                            <tbody>
                                {(features?.preview || []).map((row, i) => (
                                    <tr key={i} className="border-t border-gray-100">
                                        <td className="p-1.5">{row.booking_reference}</td>
                                        <td className="p-1.5 text-right">{row.dep_dayofweek}</td>
                                        <td className="p-1.5 text-right">{row.dep_is_weekend}</td>
                                        <td className="p-1.5 text-right">{row.dep_is_holiday}</td>
                                        <td className="p-1.5 text-right">{row.hour}</td>
                                        <td className="p-1.5 text-right">{row.lead_time_days}</td>
                                        <td className="p-1.5 text-right">{(row.occupancy_at_booking ?? 0).toFixed(2)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AnalyticsPanel;
