export interface User {
  id: string
  username: string
  email: string
  first_name: string
  last_name: string
  avatar_url?: string
  phone_number?: string
  timezone?: string
  locale?: string
  is_active: boolean
  is_verified: boolean
  is_superuser: boolean
  last_login_at?: string
  failed_login_attempts?: number
  locked_until?: string | null
  created_at: string
  updated_at: string
  roles: Role[]
  permissions: string[]
}

export interface Role {
  id: string
  name: string
  description: string
  is_system?: boolean
  is_default?: boolean
  weight?: number
  created_at?: string
  updated_at?: string
}

export interface UserListResponse {
  data: User[]
  meta: {
    page: number
    per_page: number
    total: number
    total_pages: number
    has_next: boolean
    has_previous: boolean
  }
  links: {
    self: string
    first?: string
    prev?: string
    next?: string
    last?: string
  }
}

export interface UserCreateRequest {
  username: string
  email: string
  password: string
  first_name: string
  last_name: string
  phone_number?: string
  timezone?: string
  locale?: string
  is_active?: boolean
  role_ids?: string[]
}

export interface UserUpdateRequest {
  first_name?: string
  last_name?: string
  phone_number?: string
  timezone?: string
  locale?: string
  is_active?: boolean
}

export interface UserFilters {
  page?: number
  per_page?: number
  search?: string
  is_active?: boolean
  is_verified?: boolean
  role_id?: string
  sort?: string
  order?: 'asc' | 'desc'
}