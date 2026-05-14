import { useState, useEffect } from 'react';
import Navbar from '../component/Navbar';
import DashboardOverview from '../component/DashboardOverview';
import ReportsPanel from '../component/ReportsPanel';
import BookingHistoryPanel from '../component/BookingHistoryPanel';
import AnalyticsPanel from '../component/AnalyticsPanel';
import {
    getTrains, createTrain, updateTrain, deleteTrain,
    getSchedules, createSchedule, updateSchedule, deleteSchedule,
    getReservations, cancelReservation
} from '../services/api';

const AdminDashboard = () => {
    const [activeTab, setActiveTab] = useState('overview');

    return (
        <div className="min-h-screen bg-gray-100">
            <Navbar />

            <main className="max-w-7xl mx-auto mt-8 px-4 pb-12">
                <div className="flex items-center justify-between mb-6">
                    <h1 className="text-3xl font-bold text-gray-800">⚙️ Admin Dashboard</h1>
                </div>

                <div className="flex flex-wrap gap-1 bg-white p-1 rounded-lg shadow-sm border border-gray-200 mb-6 w-max">
                    {[
                        { id: 'overview', label: '📊 Overview' },
                        { id: 'trains', label: 'Trains' },
                        { id: 'schedules', label: 'Schedules' },
                        { id: 'reservations', label: 'Reservations' },
                        { id: 'reports', label: '📑 Reports' },
                        { id: 'history', label: '🧾 Booking History' },
                        { id: 'analytics', label: '🤖 Analytics' },
                    ].map(t => (
                        <button
                            key={t.id}
                            onClick={() => setActiveTab(t.id)}
                            className={`px-5 py-2 rounded-md text-sm font-semibold transition-colors duration-200 ${activeTab === t.id ? 'bg-blue-600 text-white shadow' : 'text-gray-600 hover:bg-gray-100'}`}
                        >
                            {t.label}
                        </button>
                    ))}
                </div>

                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    {activeTab === 'overview' && <DashboardOverview />}
                    {activeTab === 'trains' && <TrainsManager />}
                    {activeTab === 'schedules' && <SchedulesManager />}
                    {activeTab === 'reservations' && <ReservationsReport />}
                    {activeTab === 'reports' && <ReportsPanel />}
                    {activeTab === 'history' && <BookingHistoryPanel />}
                    {activeTab === 'analytics' && <AnalyticsPanel />}
                </div>
            </main>
        </div>
    );
};


const TrainsManager = () => {
    const [trains, setTrains] = useState([]);
    const [loading, setLoading] = useState(true);

    const [editId, setEditId] = useState(null);
    const [name, setName] = useState('');
    const [type, setType] = useState('High Speed');
    const [seats, setSeats] = useState(200);
    const [status, setStatus] = useState('active');

    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        loadTrains();
    }, []);

    const loadTrains = async () => {
        setLoading(true);
        try {
            const data = await getTrains({ per_page: 100 });
            setTrains(data.items || []);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleEdit = (train) => {
        setEditId(train.id);
        setName(train.name);
        setType(train.train_type);
        setSeats(train.total_seats);
        setStatus(train.status);
        setError('');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleCancelEdit = () => {
        setEditId(null);
        setName('');
        setType('High Speed');
        setSeats(200);
        setStatus('active');
        setError('');
    };

    const handleDelete = async (id, trainName) => {
        if (window.confirm(`Are you sure you want to delete train '${trainName}'? This will also delete its schedules.`)) {
            try {
                await deleteTrain(id);
                loadTrains();
            } catch (err) {
                alert(err.message || 'Failed to delete train');
            }
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setError('');
        try {
            const payload = {
                name,
                train_type: type,
                total_seats: parseInt(seats, 10),
                status
            };

            if (editId) {
                await updateTrain(editId, payload);
            } else {
                await createTrain(payload);
            }

            handleCancelEdit();
            loadTrains();
        } catch (err) {
            setError(err.message || `Failed to ${editId ? 'update' : 'add'} train`);
        } finally {
            setSaving(false);
        }
    };

    return (
        <div>
            <h2 className="text-xl font-bold text-gray-800 mb-4">Manage Trains</h2>

            <form onSubmit={handleSubmit} className="bg-gray-50 border border-gray-200 rounded p-4 mb-8">
                <div className="flex flex-wrap items-end gap-4">
                    <div className="flex-1 min-w-[200px]">
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Train Name</label>
                        <input required type="text" value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Express 101" className="w-full border rounded px-3 py-2 text-sm" />
                    </div>
                    <div className="w-48">
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Type</label>
                        <input required type="text" value={type} onChange={e => setType(e.target.value)} className="w-full border rounded px-3 py-2 text-sm" />
                    </div>
                    <div className="w-32">
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Total Seats</label>
                        <input required type="number" min="1" max="2000" value={seats} onChange={e => setSeats(e.target.value)} className="w-full border rounded px-3 py-2 text-sm" />
                    </div>
                    {editId && (
                        <div className="w-32">
                            <label className="block text-sm font-semibold text-gray-700 mb-1">Status</label>
                            <select value={status} onChange={e => setStatus(e.target.value)} className="w-full border rounded px-3 py-2 text-sm bg-white">
                                <option value="active">Active</option>
                                <option value="inactive">Inactive</option>
                                <option value="maintenance">Maintenance</option>
                            </select>
                        </div>
                    )}
                    <div className="flex gap-2">
                        <button type="submit" disabled={saving} className={`${editId ? 'bg-orange-500 hover:bg-orange-600' : 'bg-green-600 hover:bg-green-700'} text-white font-bold py-2 px-6 rounded text-sm disabled:opacity-50`}>
                            {saving ? 'Saving...' : (editId ? 'Update Train' : '+ Add Train')}
                        </button>
                        {editId && (
                            <button type="button" onClick={handleCancelEdit} className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded text-sm">
                                Cancel
                            </button>
                        )}
                    </div>
                </div>
                {error && <p className="text-red-600 text-sm mt-3">{error}</p>}
            </form>

            {loading ? <p className="text-gray-500">Loading trains...</p> : (
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-gray-100 border-b border-gray-200 text-sm">
                                <th className="p-3 font-semibold text-gray-700">ID</th>
                                <th className="p-3 font-semibold text-gray-700">Name</th>
                                <th className="p-3 font-semibold text-gray-700">Type</th>
                                <th className="p-3 font-semibold text-gray-700">Seats</th>
                                <th className="p-3 font-semibold text-gray-700">Status</th>
                                <th className="p-3 font-semibold text-gray-700 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {trains.map(t => (
                                <tr key={t.id} className="border-b border-gray-100 hover:bg-gray-50 text-sm">
                                    <td className="p-3 text-gray-500">#{t.id}</td>
                                    <td className="p-3 font-medium text-gray-900">{t.name}</td>
                                    <td className="p-3 text-gray-600">{t.train_type}</td>
                                    <td className="p-3 text-gray-600">{t.total_seats}</td>
                                    <td className="p-3">
                                        <span className={`px-2 py-1 text-xs rounded-full font-medium ${t.status === 'active' ? 'bg-green-100 text-green-800' :
                                                t.status === 'maintenance' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                                            }`}>
                                            {t.status}
                                        </span>
                                    </td>
                                    <td className="p-3 text-right">
                                        <button onClick={() => handleEdit(t)} className="text-blue-600 hover:text-blue-900 font-medium mr-3">Edit</button>
                                        <button onClick={() => handleDelete(t.id, t.name)} className="text-red-600 hover:text-red-900 font-medium">Delete</button>
                                    </td>
                                </tr>
                            ))}
                            {trains.length === 0 && (
                                <tr>
                                    <td colSpan="6" className="p-4 text-center text-gray-500">No trains found. Add one above.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};


const SchedulesManager = () => {
    const [schedules, setSchedules] = useState([]);
    const [trains, setTrains] = useState([]);
    const [loading, setLoading] = useState(true);

    const [editId, setEditId] = useState(null);
    const [trainId, setTrainId] = useState('');
    const [origin, setOrigin] = useState('');
    const [destination, setDestination] = useState('');
    const [date, setDate] = useState('');
    const [depTime, setDepTime] = useState('');
    const [arrTime, setArrTime] = useState('');
    const [price, setPrice] = useState(100);

    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const [schedData, trainData] = await Promise.all([
                getSchedules({ per_page: 100 }),
                getTrains({ per_page: 100, status: 'active' })
            ]);
            setSchedules(schedData.items || []);
            setTrains(trainData.items || []);

            if (!editId && trainData.items?.length > 0) {
                setTrainId(trainData.items[0].id);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleEdit = (sched) => {
        setEditId(sched.id);
        setTrainId(sched.train_id);
        setOrigin(sched.origin);
        setDestination(sched.destination);
        setDate(sched.departure_date);
        setDepTime(sched.departure_time);
        setArrTime(sched.arrival_time);
        setPrice(sched.ticket_price);
        setError('');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleCancelEdit = () => {
        setEditId(null);
        setOrigin('');
        setDestination('');
        if (trains.length > 0) setTrainId(trains[0].id);
        setError('');
    };

    const handleDelete = async (id, info) => {
        if (window.confirm(`Are you sure you want to delete this schedule?\n${info}\nAny reservations for this schedule will also be cancelled.`)) {
            try {
                await deleteSchedule(id);
                loadData();
            } catch (err) {
                alert(err.message || 'Failed to delete schedule');
            }
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setError('');

        const formattedDepTime = depTime.length === 5 ? `${depTime}:00` : depTime;
        const formattedArrTime = arrTime.length === 5 ? `${arrTime}:00` : arrTime;

        try {
            const payload = {
                train_id: parseInt(trainId, 10),
                origin,
                destination,
                departure_date: date,
                departure_time: formattedDepTime,
                arrival_time: formattedArrTime,
                ticket_price: parseFloat(price)
            };

            if (editId) {
                await updateSchedule(editId, payload);
            } else {
                await createSchedule(payload);
            }

            handleCancelEdit();
            loadData();
        } catch (err) {
            setError(err.message || `Failed to ${editId ? 'update' : 'add'} schedule`);
        } finally {
            setSaving(false);
        }
    };

    return (
        <div>
            <h2 className="text-xl font-bold text-gray-800 mb-4">Manage Schedules</h2>

            <form onSubmit={handleSubmit} className="bg-gray-50 border border-gray-200 rounded p-4 mb-8">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="col-span-2">
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Train</label>
                        <select required value={trainId} onChange={e => setTrainId(e.target.value)} disabled={!!editId} className="w-full border rounded px-3 py-2 text-sm bg-white disabled:bg-gray-100">
                            {trains.map(t => <option key={t.id} value={t.id}>{t.name} ({t.total_seats} seats)</option>)}
                            {trains.length === 0 && <option value="">No trains available</option>}
                        </select>
                        {editId && <p className="text-xs text-gray-500 mt-1">Cannot change train for an existing schedule.</p>}
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Origin City</label>
                        <input required type="text" value={origin} onChange={e => setOrigin(e.target.value)} placeholder="e.g. Riyadh" className="w-full border rounded px-3 py-2 text-sm" />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Destination City</label>
                        <input required type="text" value={destination} onChange={e => setDestination(e.target.value)} placeholder="e.g. Jeddah" className="w-full border rounded px-3 py-2 text-sm" />
                    </div>

                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Departure Date</label>
                        <input required type="date" value={date} onChange={e => setDate(e.target.value)} className="w-full border rounded px-3 py-2 text-sm" />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Departure Time</label>
                        <input required type="time" value={depTime} onChange={e => setDepTime(e.target.value)} className="w-full border rounded px-3 py-2 text-sm" />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Arrival Time</label>
                        <input required type="time" value={arrTime} onChange={e => setArrTime(e.target.value)} className="w-full border rounded px-3 py-2 text-sm" />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Price (SAR)</label>
                        <input required type="number" min="1" step="0.01" value={price} onChange={e => setPrice(e.target.value)} className="w-full border rounded px-3 py-2 text-sm" />
                    </div>
                </div>

                <div className="flex gap-2 justify-end">
                    {editId && (
                        <button type="button" onClick={handleCancelEdit} className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-6 rounded text-sm">
                            Cancel
                        </button>
                    )}
                    <button type="submit" disabled={saving || trains.length === 0} className={`${editId ? 'bg-orange-500 hover:bg-orange-600' : 'bg-green-600 hover:bg-green-700'} text-white font-bold py-2 px-8 rounded text-sm disabled:opacity-50`}>
                        {saving ? 'Saving...' : (editId ? 'Update Schedule' : '+ Add Schedule')}
                    </button>
                </div>
                {error && <p className="text-red-600 text-sm mt-3">{error}</p>}
            </form>

            {loading ? <p className="text-gray-500">Loading schedules...</p> : (
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-gray-100 border-b border-gray-200 text-sm">
                                <th className="p-3 font-semibold text-gray-700">Train</th>
                                <th className="p-3 font-semibold text-gray-700">Route</th>
                                <th className="p-3 font-semibold text-gray-700">Departure</th>
                                <th className="p-3 font-semibold text-gray-700">Arrival</th>
                                <th className="p-3 font-semibold text-gray-700">Price</th>
                                <th className="p-3 font-semibold text-gray-700">Seats</th>
                                <th className="p-3 font-semibold text-gray-700 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {schedules.map(s => (
                                <tr key={s.id} className="border-b border-gray-100 hover:bg-gray-50 text-sm">
                                    <td className="p-3 font-medium text-gray-900">{s.train_name}</td>
                                    <td className="p-3 text-gray-600">{s.origin} → {s.destination}</td>
                                    <td className="p-3 text-gray-600">
                                        <div className="font-medium">{s.departure_date}</div>
                                        <div className="text-xs text-gray-500">{s.departure_time}</div>
                                    </td>
                                    <td className="p-3 text-gray-600">{s.arrival_time}</td>
                                    <td className="p-3 font-medium text-green-700">{s.ticket_price} SAR</td>
                                    <td className="p-3 text-gray-600">{s.available_seats} / {s.total_seats}</td>
                                    <td className="p-3 text-right">
                                        <button onClick={() => handleEdit(s)} className="text-blue-600 hover:text-blue-900 font-medium mr-3">Edit</button>
                                        <button onClick={() => handleDelete(s.id, `${s.train_name}: ${s.origin} to ${s.destination}`)} className="text-red-600 hover:text-red-900 font-medium">Delete</button>
                                    </td>
                                </tr>
                            ))}
                            {schedules.length === 0 && (
                                <tr>
                                    <td colSpan="7" className="p-4 text-center text-gray-500">No schedules found. Add one above.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};


const ReservationsReport = () => {
    const [reservations, setReservations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [statusFilter, setStatusFilter] = useState('');
    const [cancelInfo, setCancelInfo] = useState(null);
    const [busyId, setBusyId] = useState(null);

    useEffect(() => {
        loadReservations();
    }, [statusFilter]);

    const loadReservations = async () => {
        setLoading(true);
        try {
            const filters = { per_page: 100 };
            if (statusFilter) filters.status = statusFilter;
            const data = await getReservations(filters);
            setReservations(data.items || []);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = async (r) => {
        if (!confirm(`Cancel ${r.booking_reference}? Refund is computed automatically.`)) return;
        setBusyId(r.id);
        setCancelInfo(null);
        try {
            const res = await cancelReservation(r.id);
            setCancelInfo(res);
            await loadReservations();
        } catch (e) {
            alert(`Cancellation failed: ${e.message}`);
        } finally {
            setBusyId(null);
        }
    };

    return (
        <div>
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-800">Reservations</h2>
                <div className="flex items-center gap-2">
                    <select
                        value={statusFilter}
                        onChange={e => setStatusFilter(e.target.value)}
                        className="text-sm border border-gray-300 rounded px-2 py-1.5"
                    >
                        <option value="">All</option>
                        <option value="confirmed">Confirmed</option>
                        <option value="cancelled">Cancelled</option>
                    </select>
                    <button
                        onClick={loadReservations}
                        className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 py-1.5 px-3 rounded font-medium border border-gray-300"
                    >
                        🔄 Refresh
                    </button>
                </div>
            </div>

            {cancelInfo && (
                <div className="mb-4 p-3 rounded border border-green-200 bg-green-50 text-green-900 text-sm">
                    ✅ {cancelInfo.message} Booking <b>{cancelInfo.booking_reference}</b> refunded
                    {' '}<b>{cancelInfo.refund_amount.toFixed(2)} SAR</b>
                    {' '}({(cancelInfo.refund_percentage * 100).toFixed(0)}%).
                </div>
            )}

            {loading ? <p className="text-gray-500">Loading reservations...</p> : (
                <div className="overflow-x-auto shadow-sm border border-gray-200 rounded-lg">
                    <table className="w-full text-left border-collapse bg-white">
                        <thead>
                            <tr className="bg-blue-50 border-b border-gray-200 text-sm">
                                <th className="p-3 font-semibold text-blue-900">Reference</th>
                                <th className="p-3 font-semibold text-blue-900">Passenger</th>
                                <th className="p-3 font-semibold text-blue-900">Train</th>
                                <th className="p-3 font-semibold text-blue-900">Route</th>
                                <th className="p-3 font-semibold text-blue-900">Departs</th>
                                <th className="p-3 font-semibold text-blue-900">Status</th>
                                <th className="p-3 font-semibold text-blue-900">Price</th>
                                <th className="p-3 font-semibold text-blue-900">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {reservations.map(r => (
                                <tr key={r.id} className="border-b border-gray-100 hover:bg-gray-50 text-sm">
                                    <td className="p-3 font-bold text-gray-700">{r.booking_reference}</td>
                                    <td className="p-3">
                                        <div className="font-medium text-gray-900">{r.passenger_name}</div>
                                        <div className="text-xs text-gray-500">ID: {r.passenger_national_id}</div>
                                    </td>
                                    <td className="p-3 text-gray-600">{r.train_name}</td>
                                    <td className="p-3 text-gray-600">{r.schedule_origin} → {r.schedule_destination}</td>
                                    <td className="p-3 text-gray-600">
                                        <div className="font-medium">{r.departure_date}</div>
                                        <div className="text-xs text-gray-500">{r.departure_time}</div>
                                    </td>
                                    <td className="p-3">
                                        <span className={`px-2 py-1 text-xs rounded-full font-medium ${r.status === 'confirmed' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                            }`}>
                                            {r.status.toUpperCase()}
                                        </span>
                                    </td>
                                    <td className="p-3 font-medium text-green-700">{r.price_paid} SAR</td>
                                    <td className="p-3">
                                        {r.status === 'confirmed' ? (
                                            <button
                                                onClick={() => handleCancel(r)}
                                                disabled={busyId === r.id}
                                                className="text-xs bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded px-2 py-1 font-semibold disabled:opacity-50"
                                            >
                                                {busyId === r.id ? 'Cancelling…' : 'Cancel'}
                                            </button>
                                        ) : (
                                            <span className="text-xs text-gray-400">—</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                            {reservations.length === 0 && (
                                <tr>
                                    <td colSpan="8" className="p-6 text-center text-gray-500">No reservations found in the system.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default AdminDashboard;
