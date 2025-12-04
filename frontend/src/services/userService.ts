import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface CivitasUser {
  user_id: string
  firstname: string
  lastname: string
  email: string | null
  phone_number: string | null
  status: string
  time_created: string
  time_updated: string | null
  time_last_login: string | null
  google_id: string | null
  google_email: string | null
  google_avatar_url: string | null
  meta_data: Record<string, any>
}

export const userService = {
  /**
   * Get list of all users with optional search
   */
  getUsers: async (params?: {
    skip?: number
    limit?: number
    search?: string
  }): Promise<CivitasUser[]> => {
    const response = await api.get<CivitasUser[]>('/api/users/', { params })
    return response.data
  },

  /**
   * Get a specific user by ID
   */
  getUser: async (userId: string): Promise<CivitasUser> => {
    const response = await api.get<CivitasUser>(`/api/users/${userId}`)
    return response.data
  },
}
