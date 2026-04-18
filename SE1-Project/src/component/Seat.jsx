const Seat = ({ number, isBooked, isSelected, onSelect }) => {
    let bgClass = 'bg-green-100 border-green-400 text-green-800 hover:bg-green-200 cursor-pointer';

    if (isBooked) {
        bgClass = 'bg-gray-300 border-gray-400 text-gray-500 cursor-not-allowed';
    } else if (isSelected) {
        bgClass = 'bg-blue-500 border-blue-600 text-white cursor-pointer';
    }

    return (
        <button
            className={`w-10 h-10 rounded border-2 text-xs font-bold flex items-center justify-center transition-all duration-150 ${bgClass}`}
            disabled={isBooked}
            onClick={() => !isBooked && onSelect(number)}
            title={isBooked ? 'Already booked' : `Seat ${number}`}
        >
            {number}
        </button>
    );
};

export default Seat;
