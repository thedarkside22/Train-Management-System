import { useState } from 'react';

const SeatSelection = ({ schedule, onConfirm, onBack, loading, error }) => {

    const [fullName, setFullName] = useState('');
    const [nationalId, setNationalId] = useState('');
    const [phone, setPhone] = useState('');
    const [email, setEmail] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        onConfirm({
            full_name: fullName,
            national_id: nationalId,
            phone,
            email: email || undefined,
        });
    };

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">

            <button
                onClick={onBack}
                className="text-blue-600 hover:text-blue-800 text-sm font-semibold mb-4 inline-flex items-center gap-1"
            >
                ← Back to schedules
            </button>

            <h2 className="text-xl font-bold text-gray-800">
                {schedule.train_name} — {schedule.origin} → {schedule.destination}
            </h2>
            <p className="text-sm text-gray-500 mt-1">
                📅 {schedule.departure_date} &nbsp;|&nbsp;
                🕐 {schedule.departure_time} → {schedule.arrival_time} &nbsp;|&nbsp;
                💰 {schedule.ticket_price} SAR
            </p>
            <p className={`text-sm mt-1 font-semibold ${schedule.available_seats > 10 ? 'text-green-600' :
                    schedule.available_seats > 0 ? 'text-yellow-600' :
                        'text-red-600'
                }`}>
                {schedule.available_seats} seats remaining
            </p>

            <hr className="my-5" />

            <h3 className="text-lg font-bold text-gray-700 mb-4">Passenger Information</h3>

            {error && (
                <div className="bg-red-50 border border-red-300 text-red-700 rounded-lg p-3 mb-4 text-sm">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1" htmlFor="passengerName">
                        Full Name *
                    </label>
                    <input
                        id="passengerName"
                        type="text"
                        required
                        minLength={2}
                        placeholder="Enter passenger full name"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>

                <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1" htmlFor="nationalId">
                        National ID (10 digits) *
                    </label>
                    <input
                        id="nationalId"
                        type="text"
                        required
                        pattern="\d{10}"
                        placeholder="e.g. 1234567890"
                        value={nationalId}
                        onChange={(e) => setNationalId(e.target.value)}
                        className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-400 mt-1">Must start with 1 (citizen) or 2 (resident)</p>
                </div>

                <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1" htmlFor="phone">
                        Phone Number *
                    </label>
                    <input
                        id="phone"
                        type="text"
                        required
                        placeholder="05XXXXXXXX"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>

                <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1" htmlFor="passengerEmail">
                        Email (optional)
                    </label>
                    <input
                        id="passengerEmail"
                        type="email"
                        placeholder="passenger@example.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>

                <div className="pt-2">
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-6 py-2.5 rounded font-bold text-sm transition duration-200"
                    >
                        {loading ? 'Booking...' : `Book Ticket — ${schedule.ticket_price} SAR`}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default SeatSelection;
