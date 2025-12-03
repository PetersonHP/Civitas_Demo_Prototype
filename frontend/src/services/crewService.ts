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

  /**
   * Get the k nearest crews to a given location
   * @param latitude - Latitude of the location
   * @param longitude - Longitude of the location
   * @param k - Number of nearest crews to return
   * @param filters - Optional filters for crew type and status
   * @returns Array of k nearest crews sorted by distance
   * 
   * NOTE: This is inefficient for a large number of teams.
   * This should eventually be updated to use spatial queries on the 
   * backend.
   */
  getKNearestCrews: async (
    latitude: number,
    longitude: number,
    k: number,
    filters?: {
      crew_type?: SupportCrewType
      status?: SupportCrewStatus
    }
  ): Promise<SupportCrew[]> => {
    // Fetch all crews with optional filters
    const crews = await crewService.getCrews(filters)

    // Filter out crews without location coordinates
    const crewsWithLocation = crews.filter((crew) => crew.location_coordinates !== null)

    // Calculate distance for each crew and sort
    const crewsWithDistance = crewsWithLocation
      .map((crew) => {
        const distance = calculateDistance(
          latitude,
          longitude,
          crew.location_coordinates!.lat,
          crew.location_coordinates!.lng
        )
        return { crew, distance }
      })
      .sort((a, b) => a.distance - b.distance)
      .slice(0, k)
      .map((item) => item.crew)

    return crewsWithDistance
  },
}

/**
 * Calculate the Haversine distance between two coordinates in kilometers
 */
function calculateDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371 // Earth's radius in kilometers
  const dLat = toRadians(lat2 - lat1)
  const dLon = toRadians(lon2 - lon1)

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(lat1)) *
      Math.cos(toRadians(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2)

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

/**
 * Convert degrees to radians
 */
function toRadians(degrees: number): number {
  return degrees * (Math.PI / 180)
}
