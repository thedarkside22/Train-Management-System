import { Navigate, Outlet } from 'react-router';
import { useAuth } from '../context/AuthContext';

const AdminRoute = () => {
    const { user } = useAuth();

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    if (user.role !== 'admin') {
        return <Navigate to="/" replace />;
    }

    return <Outlet />;
};

export default AdminRoute;
