const TRAINS = [
    {
        id: 1,
        name: 'Express 101',
        from: 'Riyadh',
        to: 'Jeddah',
        departure: '08:00 AM',
        arrival: '02:30 PM',
        price: 150,
        totalSeats: 40,
        bookedSeats: [3, 7, 12, 15, 22, 31, 35],
    },
    {
        id: 2,
        name: 'Express 202',
        from: 'Riyadh',
        to: 'Dammam',
        departure: '10:00 AM',
        arrival: '01:00 PM',
        price: 100,
        totalSeats: 40,
        bookedSeats: [1, 5, 8, 14, 19, 20, 27, 33, 38],
    },
    {
        id: 3,
        name: 'Express 303',
        from: 'Jeddah',
        to: 'Madinah',
        departure: '06:00 PM',
        arrival: '09:00 PM',
        price: 80,
        totalSeats: 32,
        bookedSeats: [2, 6, 10, 16, 24, 30],
    },
];

export default TRAINS;
