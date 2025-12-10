'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import DashboardLayout from '@/components/DashboardLayout';

export default function ProfilePage() {
    const router = useRouter();
    const { user, loading } = useAuth();
    const [isEditing, setIsEditing] = useState(false);

    useEffect(() => {
        if (!loading && !user) {
            router.push('/login');
        }
    }, [user, loading, router]);

    if (loading || !user) {
        return null;
    }

    return (
        <DashboardLayout>
            <div className="max-w-3xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Profile Settings</h1>
                    <p className="mt-2 text-gray-600">Manage your account information</p>
                </div>

                {/* Profile Card */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h2 className="text-lg font-semibold text-gray-900">Account Information</h2>
                    </div>

                    <div className="p-6 space-y-6">
                        {/* Avatar */}
                        <div className="flex items-center space-x-6">
                            <div className="w-20 h-20 rounded-full bg-indigo-100 flex items-center justify-center">
                                <span className="text-indigo-600 font-bold text-2xl">
                                    {user.username?.charAt(0).toUpperCase()}
                                </span>
                            </div>
                            <div>
                                <h3 className="text-lg font-medium text-gray-900">{user.username}</h3>
                                <p className="text-sm text-gray-500">Member since {new Date().toLocaleDateString()}</p>
                            </div>
                        </div>

                        {/* Email */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Email Address
                            </label>
                            <div className="flex items-center space-x-2">
                                <input
                                    type="email"
                                    value={user.email}
                                    disabled
                                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
                                />
                                <span className="inline-flex items-center px-3 py-2 rounded-lg bg-green-100 text-green-800 text-sm font-medium">
                                    <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                    </svg>
                                    Verified
                                </span>
                            </div>
                        </div>

                        {/* Username */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Username
                            </label>
                            <input
                                type="text"
                                value={user.username}
                                disabled={!isEditing}
                                className={`w-full px-4 py-2 border border-gray-300 rounded-lg ${isEditing ? 'bg-white' : 'bg-gray-50 text-gray-500'
                                    }`}
                            />
                        </div>

                        {/* Account Status */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Account Status
                            </label>
                            <div className="flex items-center space-x-2">
                                <span className="inline-flex items-center px-3 py-1 rounded-full bg-green-100 text-green-800 text-sm font-medium">
                                    Active
                                </span>
                                <span className="text-sm text-gray-500">
                                    Your account is in good standing
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end space-x-3">
                        {isEditing ? (
                            <>
                                <button
                                    onClick={() => setIsEditing(false)}
                                    className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={() => setIsEditing(false)}
                                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
                                >
                                    Save Changes
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={() => setIsEditing(true)}
                                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
                            >
                                Edit Profile
                            </button>
                        )}
                    </div>
                </div>

                {/* Security Section */}
                <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h2 className="text-lg font-semibold text-gray-900">Security</h2>
                    </div>

                    <div className="p-6">
                        <button className="w-full text-left px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="font-medium text-gray-900">Change Password</p>
                                    <p className="text-sm text-gray-500">Update your password regularly for security</p>
                                </div>
                                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                </svg>
                            </div>
                        </button>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
