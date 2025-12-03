import { useEffect, useRef, useState, useMemo } from 'react'
import Map, { MapRef } from 'react-map-gl/mapbox'
import 'mapbox-gl/dist/mapbox-gl.css'
import { Box, Spinner, Text, Flex } from '@chakra-ui/react'
import { Ticket } from '../services/ticketService'
import { TicketMarker } from './TicketMarker'
import { useMapFlyTo } from '../hooks/useMapFlyTo'
import { calculateBounds, isValidCoordinates } from '../utils/mapHelpers'

interface MapViewProps {
  tickets: Ticket[]
  selectedTicket: Ticket | null
  onTicketSelect: (ticket: Ticket | null) => void
}

/**
 * Main map component displaying ticket locations with Mapbox
 * Handles auto-fitting bounds, selection synchronization, and marker rendering
 */
export const MapView = ({ tickets, selectedTicket, onTicketSelect }: MapViewProps) => {
  const mapRef = useRef<MapRef>(null)
  const { flyToLocation } = useMapFlyTo(mapRef)
  const [mapError, setMapError] = useState<string | null>(null)
  const [mapLoaded, setMapLoaded] = useState(false)

  const [viewState, setViewState] = useState({
    longitude: -98.5795, // Center of USA
    latitude: 39.8283,
    zoom: 4
  })

  // Filter tickets with valid coordinates
  const ticketsWithCoords = useMemo(
    () => tickets.filter(t => isValidCoordinates(t.location_coordinates)),
    [tickets]
  )

  // Check for API token on mount
  useEffect(() => {
    const token = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN
    if (!token) {
      setMapError('Mapbox API token not configured. Please add VITE_MAPBOX_ACCESS_TOKEN to your .env file.')
    }
  }, [])

  // Fit bounds to all tickets on mount or when tickets change
  useEffect(() => {
    if (!mapRef.current || !mapLoaded || ticketsWithCoords.length === 0) return

    const coords = ticketsWithCoords.map(t => t.location_coordinates!)
    const bounds = calculateBounds(coords)

    if (bounds) {
      // Handle single ticket case with appropriate zoom
      if (ticketsWithCoords.length === 1) {
        mapRef.current.flyTo({
          center: [coords[0].lng, coords[0].lat],
          zoom: 12,
          duration: 1000
        })
      } else {
        mapRef.current.fitBounds(bounds, {
          padding: 40,
          duration: 1000,
          maxZoom: 15
        })
      }
    }
  }, [ticketsWithCoords, mapLoaded])

  // Fly to selected ticket when selection changes
  useEffect(() => {
    if (selectedTicket?.location_coordinates && mapLoaded) {
      flyToLocation(selectedTicket.location_coordinates, 14)
    }
  }, [selectedTicket, flyToLocation, mapLoaded])

  if (mapError) {
    return (
      <Flex alignItems="center" justifyContent="center" h="full" bg="gray.700">
        <Text color="red.400" textAlign="center" px={4}>
          {mapError}
        </Text>
      </Flex>
    )
  }

  return (
    <Box position="relative" h="full" w="full">
      {!mapLoaded && (
        <Flex
          position="absolute"
          top={0}
          left={0}
          right={0}
          bottom={0}
          alignItems="center"
          justifyContent="center"
          bg="gray.700"
          zIndex={10}
        >
          <Spinner size="xl" color="blue.400" />
        </Flex>
      )}
      <Map
        ref={mapRef}
        {...viewState}
        onMove={(evt: any) => setViewState(evt.viewState)}
        onLoad={() => setMapLoaded(true)}
        onClick={() => onTicketSelect(null)}
        mapStyle="mapbox://styles/mapbox/dark-v11"
        mapboxAccessToken={import.meta.env.VITE_MAPBOX_ACCESS_TOKEN}
        onError={(error: any) => {
          console.error('Map error:', error)
          setMapError('Failed to load map. Please check your internet connection and Mapbox token.')
        }}
        style={{ width: '100%', height: '100%' }}
      >
        {mapLoaded && ticketsWithCoords.map(ticket => (
          <TicketMarker
            key={ticket.ticket_id}
            ticket={ticket}
            isSelected={selectedTicket?.ticket_id === ticket.ticket_id}
            onClick={onTicketSelect}
          />
        ))}
      </Map>
    </Box>
  )
}
