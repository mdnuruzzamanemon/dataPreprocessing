export interface AuthUser {
    id: string;
    email: string;
    username: string;
    is_active: boolean;
}

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface SignupData {
    email: string;
    username: string;
    password: string;
}
