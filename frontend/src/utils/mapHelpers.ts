import { TicketPriority } from '../services/ticketService'
import type { LocationCoordinates } from '../services/ticketService'
import { SupportCrewType } from '../services/crewService'

/**
 * Get marker color based on ticket priority
 * Uses Chakra UI color palette for consistency with the dashboard
 */
export const getPriorityMarkerColor = (priority: TicketPriority): string => {
  const colors: Record<TicketPriority, string> = {
    [TicketPriority.LOW]: '#48BB78',     // Chakra green.400
    [TicketPriority.MEDIUM]: '#4299E1',  // Chakra blue.400
    [TicketPriority.HIGH]: '#F56565',    // Chakra red.400
  }
  return colors[priority]
}

/**
 * Type guard to validate location coordinates
 * Checks for valid lat/lng ranges and non-null values
 */
export const isValidCoordinates = (
  coords: LocationCoordinates | null | undefined
): coords is LocationCoordinates => {
  if (!coords) return false
  const { lat, lng } = coords
  return (
    typeof lat === 'number' &&
    typeof lng === 'number' &&
    lat >= -90 && lat <= 90 &&
    lng >= -180 && lng <= 180 &&
    !isNaN(lat) &&
    !isNaN(lng)
  )
}

/**
 * Calculate bounding box for an array of coordinates
 * Returns [[west, south], [east, north]] format for Mapbox fitBounds
 * Handles edge case where all points are at the same location
 */
export const calculateBounds = (
  coordinates: LocationCoordinates[]
): [[number, number], [number, number]] | null => {
  if (coordinates.length === 0) return null

  let minLng = Infinity
  let maxLng = -Infinity
  let minLat = Infinity
  let maxLat = -Infinity

  for (const coord of coordinates) {
    minLng = Math.min(minLng, coord.lng)
    maxLng = Math.max(maxLng, coord.lng)
    minLat = Math.min(minLat, coord.lat)
    maxLat = Math.max(maxLat, coord.lat)
  }

  // Handle single point or all points at same location
  // Add small padding (~1km) to create a visible bounds
  if (minLng === maxLng && minLat === maxLat) {
    const padding = 0.01
    return [
      [minLng - padding, minLat - padding],
      [maxLng + padding, maxLat + padding]
    ]
  }

  return [[minLng, minLat], [maxLng, maxLat]]
}

/**
 * Get crew type icon as SVG element
 * Returns JSX-compatible SVG path data for rendering crew type icons
 */
export const getCrewTypeIcon = (crewType: string): React.ReactNode => {
  // SVG icon content will be rendered directly in the CrewMarker component
  // This function returns the appropriate icon identifier
  const icons: Record<string, string> = {
    'pothole crew': 'construction',
    'drain crew': 'water',
    'tree crew': 'tree',
    'sign crew': 'sign',
    'snow crew': 'snow',
    'sanitation crew': 'trash',
  }
  return icons[crewType] || 'tools'
}
