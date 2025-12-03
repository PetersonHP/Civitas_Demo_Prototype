import { useCallback, RefObject } from 'react'
import type { MapRef } from 'react-map-gl/mapbox'
import type { LocationCoordinates } from '../services/ticketService'

/**
 * Custom hook for smooth map navigation
 * Provides flyToLocation function to pan and zoom to a specific coordinate
 *
 * @param mapRef - Reference to the react-map-gl MapRef
 * @returns Object with flyToLocation function
 */
export const useMapFlyTo = (mapRef: RefObject<MapRef | null>) => {
  const flyToLocation = useCallback(
    (coordinates: LocationCoordinates, zoom: number = 14) => {
      if (!mapRef.current) return

      mapRef.current.flyTo({
        center: [coordinates.lng, coordinates.lat],
        zoom,
        duration: 1500, // 1.5 seconds animation
        essential: true // Ensures animation completes even if user interrupts
      })
    },
    [mapRef]
  )

  return { flyToLocation }
}
