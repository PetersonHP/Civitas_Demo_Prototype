import axios from 'axios'

// In production (served by backend), use same origin
// In development, use VITE_API_URL or default to localhost:8000
const API_URL = import.meta.env.PROD
  ? '' // Same origin in production
  : (import.meta.env.VITE_API_URL || 'http://localhost:8000')

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface Item {
  id: number
  name: string
  description: string | null
  created_at: string
  updated_at: string | null
}

export interface ItemCreate {
  name: string
  description: string | null
}

export interface ItemUpdate {
  name?: string
  description?: string | null
}

export const apiService = {
  // Get all items
  getItems: async (): Promise<Item[]> => {
    const response = await api.get<Item[]>('/api/items/')
    return response.data
  },

  // Get single item
  getItem: async (id: number): Promise<Item> => {
    const response = await api.get<Item>(`/api/items/${id}`)
    return response.data
  },

  // Create item
  createItem: async (item: ItemCreate): Promise<Item> => {
    const response = await api.post<Item>('/api/items/', item)
    return response.data
  },

  // Update item
  updateItem: async (id: number, item: ItemUpdate): Promise<Item> => {
    const response = await api.put<Item>(`/api/items/${id}`, item)
    return response.data
  },

  // Delete item
  deleteItem: async (id: number): Promise<void> => {
    await api.delete(`/api/items/${id}`)
  },
}
