import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
    cancelReservation,
    getDashboardStats,
    getRevenueTrend,
    getReport,
    getPassengerBookings,
    getAnalyticsEDA,
} from '../services/api';

beforeEach(() => {
    localStorage.setItem('user', JSON.stringify({ token: 'fake-token' }));
    vi.restoreAllMocks();
});

function mockOk(body) {
    return vi.spyOn(globalThis, 'fetch').mockResolvedValue({
        ok: true,
        json: async () => body,
    });
}

describe('Sprint 3 API client', () => {
    it('cancelReservation calls DELETE /reservations/:id', async () => {
        const f = mockOk({ message: 'ok', booking_reference: 'TRN-1', refund_amount: 10, refund_percentage: 1, cancelled_at: 'x', remaining_seats: 5 });
        await cancelReservation(42);
        expect(f).toHaveBeenCalled();
        const [url, opts] = f.mock.calls[0];
        expect(url).toContain('/reservations/42');
        expect(opts.method).toBe('DELETE');
    });

    it('getDashboardStats hits /dashboard/stats', async () => {
        const f = mockOk({ total_trains: 3 });
        const data = await getDashboardStats();
        expect(data.total_trains).toBe(3);
        expect(f.mock.calls[0][0]).toContain('/dashboard/stats');
    });

    it('getRevenueTrend supports the days param', async () => {
        const f = mockOk([]);
        await getRevenueTrend(7);
        expect(f.mock.calls[0][0]).toContain('days=7');
    });

    it('getReport sends period and date filters', async () => {
        const f = mockOk({ period: 'weekly', total_bookings: 0 });
        await getReport('weekly', '2026-03-01', '2026-03-07');
        const url = f.mock.calls[0][0];
        expect(url).toContain('period=weekly');
        expect(url).toContain('start_date=2026-03-01');
        expect(url).toContain('end_date=2026-03-07');
    });

    it('getPassengerBookings hits /passengers/:id/bookings', async () => {
        const f = mockOk({ summary: {}, bookings: [] });
        await getPassengerBookings(7);
        expect(f.mock.calls[0][0]).toContain('/passengers/7/bookings');
    });

    it('getAnalyticsEDA calls /analytics/eda', async () => {
        const f = mockOk({ rows: 0 });
        await getAnalyticsEDA();
        expect(f.mock.calls[0][0]).toContain('/analytics/eda');
    });
});
