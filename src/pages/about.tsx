import { Link } from "react-router-dom";

export default function About() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 sm:text-4xl mb-4">
            About Our Data Analysis Application
          </h1>
          <p className="text-lg text-gray-600 mb-12">
            Powerful insights from your data at your fingertips
          </p>
        </div>

        <div className="bg-white shadow-xl rounded-lg overflow-hidden">
          <div className="px-6 py-8 sm:p-10">
            <div className="prose prose-lg text-gray-600 mx-auto">
              <p>
                Our data analysis application is designed to help you transform raw data into 
                meaningful insights. With powerful visualization tools and intuitive dashboards, 
                you can quickly identify trends, patterns, and outliers in your data.
              </p>
              
              <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">Key Features</h2>
              <ul className="space-y-2">
                <li>• Interactive dashboards with real-time data visualization</li>
                <li>• Advanced analytics and reporting capabilities</li>
                <li>• Customizable charts and graphs</li>
                <li>• Data export in multiple formats</li>
                <li>• User-friendly interface for all skill levels</li>
              </ul>
              
              <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">Our Mission</h2>
              <p>
                We strive to democratize data analysis by making powerful analytical tools 
                accessible to everyone, regardless of their technical background. Our platform 
                empowers businesses and individuals to make data-driven decisions with confidence.
              </p>
              
              <div className="mt-10 p-6 bg-blue-50 rounded-lg">
                <h3 className="text-xl font-semibold text-blue-800 mb-2">Get Started</h3>
                <p className="text-blue-700">
                  Explore our dashboard to see how you can visualize and analyze your data. 
                  Navigate through the sidebar to access different sections of the application.
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-50 px-6 py-4 sm:px-10">
            <Link 
              to="/dashboard" 
              className="inline-flex items-center px-4 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Go to Dashboard
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}