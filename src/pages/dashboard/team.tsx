export default function Team() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Team Members</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-2">John Doe</h2>
          <p className="text-gray-600 mb-2">Data Scientist</p>
          <p className="text-sm">Specializes in machine learning and statistical analysis.</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-2">Jane Smith</h2>
          <p className="text-gray-600 mb-2">Frontend Developer</p>
          <p className="text-sm">Creates beautiful and responsive user interfaces.</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-2">Robert Johnson</h2>
          <p className="text-gray-600 mb-2">Backend Engineer</p>
          <p className="text-sm">Builds scalable and secure server-side applications.</p>
        </div>
      </div>
    </div>
  );
}