'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { useState } from 'react';
import {
    HomeIcon,
    DocumentIcon,
    UserIcon,
    ArrowRightOnRectangleIcon,
    Bars3Icon,
    XMarkIcon
} from '@heroicons/react/24/outline';

interface SidebarProps {
    children: React.ReactNode;
}

export default function DashboardLayout({ children }: SidebarProps) {
    const pathname = usePathname();
    const router = useRouter();
    const { user, logout } = useAuth();
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const navigation = [
        { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
        { name: 'My Files', href: '/dashboard/files', icon: DocumentIcon },
        { name: 'Profile', href: '/dashboard/profile', icon: UserIcon },
    ];

    const handleLogout = async () => {
        await logout();
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Mobile menu button */}
            <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
                <h1 className="text-lg font-bold text-indigo-600">Data Preprocessor</h1>
                <button
                    onClick={() => setSidebarOpen(!sidebarOpen)}
                    className="p-2 rounded-md text-gray-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    aria-label="Toggle menu"
                >
                    {sidebarOpen ? (
                        <XMarkIcon className="h-6 w-6" />
                    ) : (
                        <Bars3Icon className="h-6 w-6" />
                    )}
                </button>
            </div>

            {/* Sidebar */}
            <div className={`fixed inset-y-0 left-0 w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 ease-in-out z-40 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'
                } lg:translate-x-0`}>
                {/* Logo/Brand */}
                <div className="flex items-center justify-center h-16 border-b border-gray-200">
                    <h1 className="text-xl font-bold text-indigo-600">Data Preprocessor</h1>
                </div>

                {/* User Info */}
                <div className="p-4 border-b border-gray-200">
                    <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
                            <span className="text-indigo-600 font-semibold text-sm">
                                {user?.username?.charAt(0).toUpperCase()}
                            </span>
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">
                                {user?.username}
                            </p>
                            <p className="text-xs text-gray-500 truncate">
                                {user?.email}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-4 space-y-1">
                    {navigation.map((item) => {
                        const isActive = pathname === item.href;
                        return (
                            <button
                                key={item.name}
                                onClick={() => {
                                    router.push(item.href);
                                    setSidebarOpen(false);
                                }}
                                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${isActive
                                        ? 'bg-indigo-50 text-indigo-600'
                                        : 'text-gray-700 hover:bg-gray-50'
                                    }`}
                            >
                                <item.icon className="w-5 h-5 flex-shrink-0" />
                                <span className="font-medium">{item.name}</span>
                            </button>
                        );
                    })}
                </nav>

                {/* Logout Button */}
                <div className="p-4 border-t border-gray-200">
                    <button
                        onClick={handleLogout}
                        className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-red-600 hover:bg-red-50 transition-colors"
                    >
                        <ArrowRightOnRectangleIcon className="w-5 h-5 flex-shrink-0" />
                        <span className="font-medium">Logout</span>
                    </button>
                </div>
            </div>

            {/* Overlay for mobile */}
            {sidebarOpen && (
                <div
                    className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
                    onClick={() => setSidebarOpen(false)}
                />
            )}

            {/* Main Content */}
            <div className="lg:pl-64">
                <main className="p-4 sm:p-6 lg:p-8 pt-20 lg:pt-8">
                    {children}
                </main>
            </div>
        </div>
    );
}
