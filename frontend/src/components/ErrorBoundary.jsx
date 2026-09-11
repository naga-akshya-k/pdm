import React from 'react';
import { AlertOctagon, RefreshCw } from 'lucide-react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[400px] flex items-center justify-center p-6">
          <div className="bg-white rounded-2xl shadow-lg border border-red-200 p-8 max-w-lg w-full text-center space-y-4">
            <div className="w-12 h-12 bg-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto">
              <AlertOctagon className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Application View Notice</h2>
            <p className="text-xs text-gray-500">
              An unexpected render exception was caught. The system has prevented a blank screen.
            </p>
            <div className="p-3 bg-gray-50 rounded-lg text-left text-xs font-mono text-red-600 overflow-x-auto border border-gray-200">
              {this.state.error?.message || 'Component failed to render'}
            </div>
            <button
              onClick={this.handleReset}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg shadow-sm transition"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Reload Dashboard View
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
