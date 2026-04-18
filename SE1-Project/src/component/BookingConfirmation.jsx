const BookingConfirmation = ({ booking, onBookAnother }) => {
    return (
        <div className="bg-green-50 border border-green-300 rounded-lg p-6 mb-8">
            <div className="text-center">
                <div className="text-4xl mb-2">✅</div>
                <h2 className="text-xl font-bold text-green-800 mb-1">Booking Confirmed!</h2>
                <p className="text-green-600 text-sm">{booking.message}</p>
            </div>

            <div className="mt-5 bg-white rounded-lg border border-green-200 p-4 space-y-2">
                <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Booking Reference</span>
                    <span className="font-bold text-blue-800 text-base">{booking.booking_reference}</span>
                </div>
                <hr />
                <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Passenger</span>
                    <span className="font-semibold text-gray-800">{booking.passenger_name}</span>
                </div>
                <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Train</span>
                    <span className="font-semibold text-gray-800">{booking.train_name}</span>
                </div>
                <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Route</span>
                    <span className="font-semibold text-gray-800">{booking.origin} → {booking.destination}</span>
                </div>
                <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Departure</span>
                    <span className="font-semibold text-gray-800">{booking.departure_date} at {booking.departure_time}</span>
                </div>
                <hr />
                <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Price Paid</span>
                    <span className="font-bold text-green-700 text-base">{booking.price_paid} SAR</span>
                </div>
                <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Remaining Seats</span>
                    <span className="font-semibold text-gray-800">{booking.remaining_seats}</span>
                </div>
            </div>

            <div className="text-center mt-5">
                <button
                    onClick={onBookAnother}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded font-semibold transition duration-200"
                >
                    Book Another Ticket
                </button>
            </div>
        </div>
    );
};

export default BookingConfirmation;
