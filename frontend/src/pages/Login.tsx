import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };



  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <Link to="/" className="flex justify-center">
          <span className="text-4xl font-bold">
            <span className="bg-gradient-to-r from-orange-500 to-red-600 bg-clip-text text-transparent">Mile</span>
            <span className="bg-gradient-to-r from-yellow-600 to-yellow-800 bg-clip-text text-transparent">Sync</span>
          </span>
        </Link>
        <h2 className="mt-6 text-center text-2xl font-bold text-gray-900">
          Sign in to your account
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-lg sm:rounded-lg sm:px-10">
          {/* Email/Password Form */}{/* Removed Google Login */}

          {/* Email/Password Form */}
          <form className="mt-6 space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-8 bg-blue-50 p-4 rounded-lg border border-blue-100">
            <h3 className="text-sm font-semibold text-blue-900 mb-2">Demo Accounts</h3>
            <div className="space-y-2 text-xs text-blue-800">
              <div
                className="flex justify-between items-center bg-white/50 p-2 rounded cursor-pointer hover:bg-white transition-colors"
                onClick={() => { setEmail('admin@milesync.demo'); setPassword('admin123'); }}
              >
                <div>
                  <div className="font-medium">Admin</div>
                  <div>admin@milesync.demo / admin123</div>
                </div>
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">Click to fill</span>
              </div>
              <div
                className="flex justify-between items-center bg-white/50 p-2 rounded cursor-pointer hover:bg-white transition-colors"
                onClick={() => { setEmail('user@milesync.demo'); setPassword('user123'); }}
              >
                <div>
                  <div className="font-medium">User</div>
                  <div>user@milesync.demo / user123</div>
                </div>
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">Click to fill</span>
              </div>
            </div>
          </div>

          <p className="mt-6 text-center text-sm text-gray-600">
            Don't have an account?{' '}
            <Link to="/register" className="font-medium text-primary-600 hover:text-primary-500">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
