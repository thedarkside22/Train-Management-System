const InputField = ({ id, label, type = 'text', placeholder, value, onChange, required = true }) => {
    return (
        <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor={id}>
                {label}
            </label>
            <input
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                id={id}
                type={type}
                placeholder={placeholder}
                value={value}
                onChange={onChange}
                required={required}
            />
        </div>
    );
};

export default InputField;
