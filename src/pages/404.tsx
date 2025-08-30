import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="text-center max-w-md">
        <h1 className="text-9xl font-bold text-indigo-600 mb-4">404</h1>
        <h2 className="text-3xl font-semibold text-gray-800 mb-6">Page Not Found</h2>
        <p className="text-gray-600 mb-8 text-lg">
          Sorry, the page you are looking for does not exist or has been moved.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link 
            to="/" 
            className="px-6 py-3 bg-indigo-600 text-white font-medium rounded-md hover:bg-indigo-700 transition-colors shadow-md"
          >
            Go back to Home
          </Link>
          <Link 
            to="/dashboard" 
            className="px-6 py-3 bg-white text-indigo-600 font-medium rounded-md hover:bg-gray-100 transition-colors shadow-md border border-indigo-200"
          >
            Go to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}