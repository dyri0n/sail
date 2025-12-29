export interface LoginRequest {
    email: string;
    password: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: string; // "bearer"
}

export interface UserStatsResponse {
    total_users: number;
    active_users: number;
    admin_users: number;
    last_access: string | null; // ISO Date string
}

export interface UserListItem {
    id: string; // UUID
    name: string;
    email: string;
    username: string;
    role: string; // "ADMIN" | "GERENCIA"
    is_active: boolean;
    last_login_at: string | null; // ISO Date string
    department: string | null;
}

export interface UserListResponse {
    users: UserListItem[];
}

export interface UserUpdateRequest {
    name: string;
    email: string;
    role: string;
    department: string;
    is_active: boolean;
}

export interface PasswordResetRequest {
    new_password: string;
}

export interface UserCreateRequest {
    name: string;
    email: string;
    username: string;
    role: string; // "ADMIN" | "GERENCIA"
    department?: string | null;
}

export interface FileUploadResponse {
    message: string;
    filename: string;
    upload_timestamp: string;
    status: string;
}
