const TrainList = ({ schedules, onSelectSchedule, loading, error }) => {

    if (loading) {
        return (
            <div className="text-center py-12">
                <div className="text-4xl mb-3">🔄</div>
                <p className="text-gray-500 text-lg">Loading schedules...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-300 rounded-lg p-6 text-center">
                <p className="text-red-700 font-semibold">{error}</p>
                <p className="text-red-500 text-sm mt-1">Make sure the backend server is running.</p>
            </div>
        );
    }

    if (!schedules || schedules.length === 0) {
        return (
            <div className="text-center py-12">
                <div className="text-4xl mb-3">🚆</div>
                <p className="text-gray-500 text-lg">No schedules available at the moment.</p>
            </div>
        );
    }

    return (
        <>
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Available Schedules</h2>

            <div className="grid gap-4">
                {schedules.map((schedule) => (
                    <div
                        key={schedule.id}
                        className="bg-white rounded-lg shadow-sm border border-gray-200 p-5 flex items-center justify-between hover:shadow-md transition-shadow duration-200"
                    >
                        <div className="flex-1">
                            <h3 className="text-lg font-bold text-blue-800">
                                {schedule.train_name}
                                <span className="text-sm font-normal text-gray-500 ml-2">
                                    ({schedule.train_type})
                                </span>
                            </h3>
                            <p className="text-gray-600 mt-1">
                                {schedule.origin} → {schedule.destination}
                            </p>
                            <p className="text-sm text-gray-500 mt-1">
                                📅 {schedule.departure_date} &nbsp;|&nbsp;
                                🕐 {schedule.departure_time} → {schedule.arrival_time}
                            </p>
                        </div>

                        <div className="text-right ml-4">
                            <p className="text-2xl font-bold text-blue-700">
                                {schedule.ticket_price} <span className="text-sm font-normal">SAR</span>
                            </p>

                            <p className={`text-sm mt-1 font-semibold ${schedule.available_seats > 10 ? 'text-green-600' :
                                    schedule.available_seats > 0 ? 'text-yellow-600' :
                                        'text-red-600'
                                }`}>
                                {schedule.available_seats} / {schedule.total_seats} seats available
                            </p>

                            <button
                                onClick={() => onSelectSchedule(schedule)}
                                disabled={schedule.available_seats === 0}
                                className="mt-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-5 py-2 rounded text-sm font-semibold transition duration-200"
                            >
                                {schedule.available_seats === 0 ? 'Sold Out' : 'Book Now'}
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </>
    );
};

export default TrainList;
