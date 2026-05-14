import { useState } from 'react';
import { getPassengerByNationalId, getPassengerBookings, cancelReservation } from '../services/api';

const BookingHistoryPanel = () => {
    const [nationalId, setNationalId] = useState('');
    const [history, setHistory] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [busyId, setBusyId] = useState(null);

    const search = async (e) => {
        if (e) e.preventDefault();
        setLoading(true);
        setError(null);
        setHistory(null);
        try {
            const passenger = await getPassengerByNationalId(nationalId);
            const data = await getPassengerBookings(passenger.id);
            setHistory(data);
        } catch (e) {
            setError(e.message || 'Lookup failed');
        } finally {
            setLoading(false);
        }
    };

    const onCancel = async (id, ref) => {
        if (!confirm(`Cancel booking ${ref}?`)) return;
        setBusyId(id);
        try {
            await cancelReservation(id);
            const data = await getPassengerBookings(history.passenger.id);
            setHistory(data);
        } catch (e) {
            alert(`Cancellation failed: ${e.message}`);
        } finally {
            setBusyId(null);
        }
    };

    return (
        <div>
            <h2 className="text-xl font-bold text-gray-800 mb-4">🧾 Passenger Booking History</h2>

            <form onSubmit={search} className="flex gap-2 mb-4">
                <input
                    type="text"
                    placeholder="National ID (e.g. 1xxxxxxxxx)"
                    value={nationalId}
                    onChange={e => setNationalId(e.target.value)}
                    className="border border-gray-300 rounded px-3 py-2 text-sm flex-1 max-w-md"
                />
                <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-semibold">Lookup</button>
            </form>

            {loading && <p className="text-gray-500">Loading…</p>}
            {error && <div className="p-3 bg-red-50 text-red-800 border border-red-200 rounded text-sm">⚠️ {error}</div>}

            {history && (
                <div>
                    <div className="bg-gray-50 border border-gray-200 rounded p-3 mb-4 grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                        <div><span className="text-gray-500">Name:</span> <b>{history.passenger.full_name}</b></div>
                        <div><span className="text-gray-500">Total:</span> <b>{history.summary.total_bookings}</b></div>
                        <div><span className="text-gray-500">Confirmed:</span> <b>{history.summary.confirmed}</b></div>
                        <div><span className="text-gray-500">Spent:</span> <b>{history.summary.total_spent.toFixed(2)} SAR</b></div>
                    </div>

                    <div className="overflow-x-auto border border-gray-200 rounded">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="bg-blue-50 text-blue-900">
                                    <th className="p-2 text-left">Reference</th>
                                    <th className="p-2 text-left">Train</th>
                                    <th className="p-2 text-left">Route</th>
                                    <th className="p-2 text-left">Departure</th>
                                    <th className="p-2 text-left">Status</th>
                                    <th className="p-2 text-right">Price</th>
                                    <th className="p-2 text-right">Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {history.bookings.map(b => (
                                    <tr key={b.id} className="border-t border-gray-100">
                                        <td className="p-2 font-bold">{b.booking_reference}</td>
                                        <td className="p-2">{b.train_name}</td>
                                        <td className="p-2">{b.origin} → {b.destination}</td>
                                        <td className="p-2">{b.departure_date} {b.departure_time}</td>
                                        <td className="p-2">
                                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${b.status === 'confirmed' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                {b.status.toUpperCase()}
                                            </span>
                                        </td>
                                        <td className="p-2 text-right">{b.price_paid.toFixed(2)} SAR</td>
                                        <td className="p-2 text-right">
                                            {b.status === 'confirmed' ? (
                                                <button
                                                    onClick={() => onCancel(b.id, b.booking_reference)}
                                                    disabled={busyId === b.id}
                                                    className="text-xs bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded px-2 py-1 disabled:opacity-50"
                                                >
                                                    {busyId === b.id ? '…' : 'Cancel'}
                                                </button>
                                            ) : <span className="text-gray-400 text-xs">—</span>}
                                        </td>
                                    </tr>
                                ))}
                                {history.bookings.length === 0 && (
                                    <tr><td colSpan="7" className="p-4 text-center text-gray-400 text-sm">No bookings yet.</td></tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

export default BookingHistoryPanel;
