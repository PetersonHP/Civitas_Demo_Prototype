import axios from 'axios'
import { SupportCrew } from './ticketService'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ============================================================================
// Enums matching backend
// ============================================================================

export enum SupportCrewType {
  POTHOLE_CREW = 'pothole crew',
  DRAIN_CREW = 'drain crew',
  TREE_CREW = 'tree crew',
  SIGN_CREW = 'sign crew',
  SNOW_CREW = 'snow crew',
  SANITATION_CREW = 'sanitation crew',
}

export enum SupportCrewStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
}

// ============================================================================
// Crew API Service
// ============================================================================

export const crewService = {
  /**
   * Get all crews
   */
  getCrews: async (params?: {
    skip?: number
    limit?: number
    status?: SupportCrewStatus
    crew_type?: SupportCrewType
  }): Promise<SupportCrew[]> => {
    const response = await api.get<SupportCrew[]>('/api/crews/', { params })
    return response.data
  },

  /**
   * Get a specific crew by ID
   */
  getCrew: async (teamId: string): Promise<SupportCrew> => {
    const response = await api.get<SupportCrew>(`/api/crews/${teamId}`)
    return response.data
  },
}
