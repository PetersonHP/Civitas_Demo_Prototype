import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface Label {
  label_id: string
  label_name: string
  label_description: string | null
  color_hex: string
  meta_data: Record<string, any>
  time_created: string
  time_updated: string | null
  created_by: string | null
}

export const labelService = {
  /**
   * Get list of all labels with optional search
   */
  getLabels: async (params?: {
    skip?: number
    limit?: number
    search?: string
  }): Promise<Label[]> => {
    const response = await api.get<Label[]>('/api/labels/', { params })
    return response.data
  },

  /**
   * Get a specific label by ID
   */
  getLabel: async (labelId: string): Promise<Label> => {
    const response = await api.get<Label>(`/api/labels/${labelId}`)
    return response.data
  },
}
