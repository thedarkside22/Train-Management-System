const API_BASE_URL = 'http://127.0.0.1:8000/api';

function authHeaders() {
    const stored = localStorage.getItem('user');
    if (!stored) return {};
    try {
        const { token } = JSON.parse(stored);
        if (token) return { Authorization: `Bearer ${token}` };
    } catch {
    }
    return {};
}

async function apiFetch(endpoint, options = {}) {
    const headers = {
        ...authHeaders(),
        ...options.headers,
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const message = errorData?.detail || errorData?.message || `Request failed (${response.status})`;
        throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
    }

    return response.json();
}

export async function getProfile() {
    return apiFetch('/auth/me');
}

export async function getSchedules(filters = {}) {
    const params = new URLSearchParams();
    if (filters.origin) params.append('origin', filters.origin);
    if (filters.destination) params.append('destination', filters.destination);
    if (filters.departure_date) params.append('departure_date', filters.departure_date);
    if (filters.train_id) params.append('train_id', filters.train_id);
    if (filters.available_only) params.append('available_only', 'true');
    if (filters.page) params.append('page', filters.page);
    if (filters.per_page) params.append('per_page', filters.per_page);

    const query = params.toString();
    return apiFetch(`/schedules/${query ? `?${query}` : ''}`);
}

export async function getSchedule(id) {
    return apiFetch(`/schedules/${id}`);
}

export async function createSchedule(data) {
    return apiFetch('/schedules/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
}

export async function updateSchedule(id, data) {
    return apiFetch(`/schedules/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
}

export async function deleteSchedule(id) {
    return apiFetch(`/schedules/${id}`, { method: 'DELETE' });
}

export async function getTrains(filters = {}) {
    const params = new URLSearchParams();
    if (filters.search) params.append('search', filters.search);
    if (filters.status) params.append('status', filters.status);
    if (filters.page) params.append('page', filters.page);
    if (filters.per_page) params.append('per_page', filters.per_page);

    const query = params.toString();
    return apiFetch(`/trains/${query ? `?${query}` : ''}`);
}

export async function getTrain(id) {
    return apiFetch(`/trains/${id}`);
}

export async function createTrain(data) {
    return apiFetch('/trains/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
}

export async function updateTrain(id, data) {
    return apiFetch(`/trains/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
}

export async function deleteTrain(id) {
    return apiFetch(`/trains/${id}`, { method: 'DELETE' });
}

export async function createPassenger(data) {
    return apiFetch('/passengers/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
}

export async function getPassengers(filters = {}) {
    const params = new URLSearchParams();
    if (filters.search) params.append('search', filters.search);
    if (filters.page) params.append('page', filters.page);
    if (filters.per_page) params.append('per_page', filters.per_page);

    const query = params.toString();
    return apiFetch(`/passengers/${query ? `?${query}` : ''}`);
}

export async function getPassenger(id) {
    return apiFetch(`/passengers/${id}`);
}

export async function getPassengerByNationalId(nationalId) {
    return apiFetch(`/passengers/national-id/${nationalId}`);
}

export async function bookTicket(passengerId, scheduleId) {
    return apiFetch('/reservations/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            passenger_id: passengerId,
            schedule_id: scheduleId,
        }),
    });
}

export async function getReservations(filters = {}) {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.passenger_id) params.append('passenger_id', filters.passenger_id);
    if (filters.schedule_id) params.append('schedule_id', filters.schedule_id);
    if (filters.page) params.append('page', filters.page);
    if (filters.per_page) params.append('per_page', filters.per_page);

    const query = params.toString();
    return apiFetch(`/reservations/${query ? `?${query}` : ''}`);
}

export async function getReservation(id) {
    return apiFetch(`/reservations/${id}`);
}

export async function getReservationByRef(reference) {
    return apiFetch(`/reservations/ref/${reference}`);
}

// Sprint 3 - cancellation
export async function cancelReservation(id) {
    return apiFetch(`/reservations/${id}`, { method: 'DELETE' });
}

// Sprint 3 - dashboard stats / charts
export async function getDashboardStats() {
    return apiFetch('/dashboard/stats');
}

export async function getRevenueTrend(days = 14) {
    return apiFetch(`/dashboard/revenue-trend?days=${days}`);
}

export async function getOccupancy(limit = 10) {
    return apiFetch(`/dashboard/occupancy?limit=${limit}`);
}

// Sprint 3 - reports
export async function getReport(period = 'daily', startDate, endDate) {
    const params = new URLSearchParams({ period });
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    return apiFetch(`/reports/?${params.toString()}`);
}

const API_BASE_URL_PUBLIC = 'http://127.0.0.1:8000/api';

export function getReportExportUrl(format, period, startDate, endDate) {
    const params = new URLSearchParams({ period });
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    return `${API_BASE_URL_PUBLIC}/reports/export/${format}?${params.toString()}`;
}

export async function downloadReport(format, period, startDate, endDate) {
    const params = new URLSearchParams({ period });
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const url = `${API_BASE_URL_PUBLIC}/reports/export/${format}?${params.toString()}`;
    const resp = await fetch(url, { headers: { ...authHeaders() } });
    if (!resp.ok) throw new Error(`Download failed (${resp.status})`);
    const blob = await resp.blob();
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `report_${period}.${format === 'pdf' ? 'pdf' : 'csv'}`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(link.href);
}

// Sprint 3 - booking history (US-017)
export async function getPassengerBookings(passengerId) {
    return apiFetch(`/passengers/${passengerId}/bookings`);
}

// Sprint 3 - analytics (US-015)
export async function getAnalyticsEDA() {
    return apiFetch('/analytics/eda');
}

export async function getAnalyticsFeatures(limit = 50) {
    return apiFetch(`/analytics/features?limit=${limit}`);
}

