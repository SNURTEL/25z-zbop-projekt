// Auth types based on OpenAPI specification

export type UserRole = 'admin' | 'manager' | 'user' | 'vendor';

export interface UserRegister {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in?: number;
}

export interface UserResponse {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  role: UserRole;
  office_id?: number | null;
  is_active: boolean;
  created_at: string;
}
