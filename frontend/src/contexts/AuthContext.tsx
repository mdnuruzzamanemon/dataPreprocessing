'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { AuthUser, LoginCredentials, SignupData } from '@/types/auth';

interface AuthContextType {
    user: AuthUser | null;
    loading: boolean;
    login: (credentials: LoginCredentials) => Promise<void>;
    signup: (data: SignupData) => Promise<void>;
    logout: () => Promise<void>;
    checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<AuthUser | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    const getAuthHeaders = (): HeadersInit => {
        const token = localStorage.getItem('access_token');
        if (!token) return {};
        return { 'Authorization': `Bearer ${token}` };
    };

    const checkAuth = async () => {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                setUser(null);
                setLoading(false);
                return;
            }

            const response = await fetch('http://localhost:8000/api/auth/me', {
                headers: getAuthHeaders(),
            });

            if (response.ok) {
                const userData = await response.json();
                setUser(userData);
            } else {
                setUser(null);
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        checkAuth();
    }, []);

    const login = async (credentials: LoginCredentials) => {
        const response = await fetch('http://localhost:8000/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();

        // Store tokens in localStorage for development
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);

        await checkAuth();
        router.push('/dashboard');
    };

    const signup = async (data: SignupData) => {
        const response = await fetch('http://localhost:8000/api/auth/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Signup failed');
        }

        // Redirect to OTP verification page
        router.push(`/verify-otp?email=${encodeURIComponent(data.email)}`);
    };

    const logout = async () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
        router.push('/login');
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, signup, logout, checkAuth }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
