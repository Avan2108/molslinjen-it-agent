/**
 * Main application component
 */

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-primary-700 text-white p-4">
        <h1 className="text-xl font-semibold">Molslinjen IT Support</h1>
      </header>
      <main className="container mx-auto p-4">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Welcome to IT Support
          </h2>
          <p className="text-gray-600">
            This is the foundation setup. Components will be implemented in subsequent phases.
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;
