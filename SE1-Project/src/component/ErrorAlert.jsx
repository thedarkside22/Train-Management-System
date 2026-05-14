const ErrorAlert = ({ message }) => {
    if (!message) return null;

    return (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
            {message}
        </div>
    );
};

export default ErrorAlert;
