import Seat from './Seat';

const SeatMap = ({ train, selectedSeats, onToggleSeat }) => {
    const cols = 4;
    const rows = Math.ceil(train.totalSeats / cols);

    return (
        <div className="mt-4">

            <div className="flex items-center gap-4 mb-4 text-xs">
                <div className="flex items-center gap-1">
                    <span className="inline-block w-4 h-4 rounded bg-green-100 border-2 border-green-400"></span>
                    Available
                </div>
                <div className="flex items-center gap-1">
                    <span className="inline-block w-4 h-4 rounded bg-blue-500 border-2 border-blue-600"></span>
                    Selected
                </div>
                <div className="flex items-center gap-1">
                    <span className="inline-block w-4 h-4 rounded bg-gray-300 border-2 border-gray-400"></span>
                    Booked
                </div>
            </div>

            <div className="inline-block bg-gray-50 border border-gray-200 rounded-lg p-4">
                {Array.from({ length: rows }, (_, rowIdx) => (
                    <div key={rowIdx} className="flex items-center gap-2 mb-2">

                        {[0, 1].map((colIdx) => {
                            const seatNum = rowIdx * cols + colIdx + 1;
                            if (seatNum > train.totalSeats) return <div key={colIdx} className="w-10 h-10" />;
                            return (
                                <Seat
                                    key={seatNum}
                                    number={seatNum}
                                    isBooked={train.bookedSeats.includes(seatNum)}
                                    isSelected={selectedSeats.includes(seatNum)}
                                    onSelect={onToggleSeat}
                                />
                            );
                        })}

                        <div className="w-6" />

                        {[2, 3].map((colIdx) => {
                            const seatNum = rowIdx * cols + colIdx + 1;
                            if (seatNum > train.totalSeats) return <div key={colIdx} className="w-10 h-10" />;
                            return (
                                <Seat
                                    key={seatNum}
                                    number={seatNum}
                                    isBooked={train.bookedSeats.includes(seatNum)}
                                    isSelected={selectedSeats.includes(seatNum)}
                                    onSelect={onToggleSeat}
                                />
                            );
                        })}

                    </div>
                ))}
            </div>
        </div>
    );
};

export default SeatMap;
