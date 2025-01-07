import React from 'react';
import { Upload, Home } from 'lucide-react';
import Link from 'next/link';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link 
                href="/"
                className="flex items-center px-4 text-gray-700 hover:text-blue-600"
              >
                <Home className="h-5 w-5 mr-2" />
                <span className="font-medium">Home</span>
              </Link>
              <Link 
                href="/upload"
                className="flex items-center px-4 text-gray-700 hover:text-blue-600"
              >
                <Upload className="h-5 w-5 mr-2" />
                <span className="font-medium">Upload</span>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main>{children}</main>
    </div>
  );
};

export default Layout;