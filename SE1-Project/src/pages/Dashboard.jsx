import { useState, useEffect } from 'react';
import Navbar from '../component/Navbar';
import TrainList from '../component/TrainList';
import SeatSelection from '../component/SeatSelection';
import BookingConfirmation from '../component/BookingConfirmation';
import { getSchedules, createPassenger, getPassengerByNationalId, bookTicket } from '../services/api';

const Dashboard = () => {
    const [schedules, setSchedules] = useState([]);
    const [loadingSchedules, setLoadingSchedules] = useState(true);
    const [schedulesError, setSchedulesError] = useState(null);

    const [selectedSchedule, setSelectedSchedule] = useState(null);
    const [bookingConfirmed, setBookingConfirmed] = useState(null);
    const [bookingLoading, setBookingLoading] = useState(false);
    const [bookingError, setBookingError] = useState(null);

    useEffect(() => {
        fetchSchedules();
    }, []);

    const fetchSchedules = async () => {
        setLoadingSchedules(true);
        setSchedulesError(null);
        try {
            const data = await getSchedules({ available_only: true, per_page: 50 });
            setSchedules(data.items || []);
        } catch (err) {
            setSchedulesError(err.message || 'Failed to load schedules');
        } finally {
            setLoadingSchedules(false);
        }
    };

    const handleSelectSchedule = (schedule) => {
        setSelectedSchedule(schedule);
        setBookingConfirmed(null);
        setBookingError(null);
    };

    const handleBookTicket = async (passengerData) => {
        setBookingLoading(true);
        setBookingError(null);

        try {
            let passenger;
            try {
                passenger = await getPassengerByNationalId(passengerData.national_id);
            } catch {
                passenger = await createPassenger(passengerData);
            }

            const confirmation = await bookTicket(passenger.id, selectedSchedule.id);
            setBookingConfirmed(confirmation);

            fetchSchedules();
        } catch (err) {
            setBookingError(err.message || 'Booking failed. Please try again.');
        } finally {
            setBookingLoading(false);
        }
    };

    const handleBackToSchedules = () => {
        setSelectedSchedule(null);
        setBookingConfirmed(null);
        setBookingError(null);
    };

    return (
        <div className="min-h-screen bg-gray-100">
            <Navbar />

            <main className="max-w-5xl mx-auto mt-8 px-4 pb-12">

                {bookingConfirmed && (
                    <BookingConfirmation
                        booking={bookingConfirmed}
                        onBookAnother={handleBackToSchedules}
                    />
                )}

                {!selectedSchedule && !bookingConfirmed && (
                    <TrainList
                        schedules={schedules}
                        onSelectSchedule={handleSelectSchedule}
                        loading={loadingSchedules}
                        error={schedulesError}
                    />
                )}

                {selectedSchedule && !bookingConfirmed && (
                    <SeatSelection
                        schedule={selectedSchedule}
                        onConfirm={handleBookTicket}
                        onBack={handleBackToSchedules}
                        loading={bookingLoading}
                        error={bookingError}
                    />
                )}

            </main>
        </div>
    );
};

export default Dashboard;
