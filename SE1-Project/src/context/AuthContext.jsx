import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

const USE_MOCK = false;
const API_BASE_URL = 'http://127.0.0.1:8000/api';

const MOCK_USERS = [
    { email: 'nawaf@test.com', password: '123456', name: 'Nawaf' },
    { email: 'admin@test.com', password: 'admin123', name: 'Admin' },
];

export function AuthProvider({ children }) {

    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [mockUsers, setMockUsers] = useState(MOCK_USERS);

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            try {
                setUser(JSON.parse(storedUser));
            } catch {
                localStorage.removeItem('user');
            }
        }
        setLoading(false);
    }, []);

    const login = async (username, password) => {

        if (USE_MOCK) {
            await new Promise((r) => setTimeout(r, 500));

            const found = mockUsers.find(
                (u) => u.email === username && u.password === password
            );

            if (!found) throw new Error('Invalid username or password');

            const userData = { email: found.email, name: found.name, token: 'mock-token' };
            localStorage.setItem('user', JSON.stringify(userData));
            setUser(userData);
            return userData;
        }

        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.detail || 'Invalid username or password');
        }

        const data = await response.json();
        const userData = {
            token: data.access_token,
            user_id: data.user_id,
            username: data.username,
            role: data.role,
        };
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
        return userData;
    };

    const register = async (username, name, email, password, role = 'staff') => {

        if (USE_MOCK) {
            await new Promise((r) => setTimeout(r, 500));

            if (mockUsers.find((u) => u.email === email)) {
                throw new Error('An account with this email already exists');
            }

            setMockUsers((prev) => [...prev, { email, password, name }]);

            const userData = { email, name, username, token: 'mock-token' };
            localStorage.setItem('user', JSON.stringify(userData));
            setUser(userData);
            return userData;
        }

        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username,
                email,
                password,
                full_name: name,
                role: role,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.detail || errorData?.message || 'Registration failed');
        }

        const data = await response.json();
        return data;
    };

    const logout = () => {
        localStorage.removeItem('user');
        setUser(null);
    };

    const value = {
        user,
        isAuthenticated: !!user,
        loading,
        login,
        register,
        logout,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}

export default AuthContext;
