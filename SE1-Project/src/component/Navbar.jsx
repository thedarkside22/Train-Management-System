import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router';

const Navbar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav className="bg-blue-800 text-white px-6 py-4 flex items-center justify-between shadow-md">
            <div className="flex items-center gap-6">
                <h1
                    onClick={() => navigate('/')}
                    className="text-xl font-bold tracking-wide cursor-pointer hover:text-blue-200 transition-colors"
                >
                    🚆 Train Booking System
                </h1>

                <button
                    onClick={() => navigate('/')}
                    className="flex items-center gap-1 text-sm font-semibold bg-blue-700 hover:bg-blue-600 px-3 py-1.5 rounded transition duration-200"
                >
                    🏠 Home
                </button>
            </div>

            <div className="flex items-center gap-4">
                <span className="text-sm opacity-90">{user?.username || user?.name}</span>

                {user?.role === 'admin' && (
                    <button
                        onClick={() => navigate('/admin')}
                        className="bg-yellow-500 text-yellow-900 border border-yellow-600 px-3 py-1.5 rounded text-sm font-bold hover:bg-yellow-400 transition duration-200"
                    >
                        ⚙️ Admin Area
                    </button>
                )}
                <button
                    onClick={handleLogout}
                    className="bg-white text-blue-800 px-4 py-1.5 rounded text-sm font-semibold hover:bg-gray-100 transition duration-200"
                >
                    Logout
                </button>
            </div>
        </nav>
    );
};

export default Navbar;
