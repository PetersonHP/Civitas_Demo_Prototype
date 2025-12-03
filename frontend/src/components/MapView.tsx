import { useEffect, useRef, useState, useMemo } from 'react'
import Map, { MapRef } from 'react-map-gl/mapbox'
import 'mapbox-gl/dist/mapbox-gl.css'
import { Box, Spinner, Text, Flex, VStack, Checkbox } from '@chakra-ui/react'
import { Ticket, SupportCrew } from '../services/ticketService'
import { TicketMarker } from './TicketMarker'
import { CrewMarker } from './CrewMarker'
import { useMapFlyTo } from '../hooks/useMapFlyTo'
import { calculateBounds, isValidCoordinates } from '../utils/mapHelpers'
import { crewService } from '../services/crewService'

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
  const [crews, setCrews] = useState<SupportCrew[]>([])
  const [selectedCrew, setSelectedCrew] = useState<SupportCrew | null>(null)
  const [showTickets, setShowTickets] = useState(true)
  const [showCrews, setShowCrews] = useState(false)

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

  // Filter crews with valid coordinates
  const crewsWithCoords = useMemo(
    () => crews.filter(c => isValidCoordinates(c.location_coordinates)),
    [crews]
  )

  // Fetch crews on mount
  useEffect(() => {
    const fetchCrews = async () => {
      try {
        const crewData = await crewService.getCrews()
        setCrews(crewData)
      } catch (error) {
        console.error('Failed to fetch crews:', error)
      }
    }
    fetchCrews()
  }, [])

  // Check for API token on mount
  useEffect(() => {
    const token = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN
    if (!token) {
      setMapError('Mapbox API token not configured. Please add VITE_MAPBOX_ACCESS_TOKEN to your .env file.')
    }
  }, [])

  // Fit bounds to all tickets and crews on mount or when data changes
  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return

    const allCoords = [
      ...ticketsWithCoords.map(t => t.location_coordinates!),
      ...crewsWithCoords.map(c => c.location_coordinates!)
    ]

    if (allCoords.length === 0) return

    const bounds = calculateBounds(allCoords)

    if (bounds) {
      // Handle single point case with appropriate zoom
      if (allCoords.length === 1) {
        mapRef.current.flyTo({
          center: [allCoords[0].lng, allCoords[0].lat],
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
  }, [ticketsWithCoords, crewsWithCoords, mapLoaded])

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

      {/* Map Layer Controls */}
      <Box
        position="absolute"
        top={4}
        right={4}
        bg="gray.800"
        borderRadius="md"
        p={3}
        boxShadow="lg"
        zIndex={100}
      >
        <VStack align="start" spacing={3}>
          <Text fontSize="sm" fontWeight="bold" color="gray.200">
            Map Layers
          </Text>
          <VStack align="start" spacing={2}>
            <Checkbox
              isChecked={showTickets}
              onChange={(e) => setShowTickets(e.target.checked)}
              colorScheme="blue"
            >
              <Text fontSize="sm" color="gray.300">Show Tickets</Text>
            </Checkbox>
            <Checkbox
              isChecked={showCrews}
              onChange={(e) => setShowCrews(e.target.checked)}
              colorScheme="purple"
            >
              <Text fontSize="sm" color="gray.300">Show Crews</Text>
            </Checkbox>
          </VStack>
        </VStack>
      </Box>

      <Map
        ref={mapRef}
        {...viewState}
        onMove={(evt: any) => setViewState(evt.viewState)}
        onLoad={() => setMapLoaded(true)}
        onClick={() => {
          onTicketSelect(null)
          setSelectedCrew(null)
        }}
        mapStyle="mapbox://styles/mapbox/dark-v11"
        mapboxAccessToken={import.meta.env.VITE_MAPBOX_ACCESS_TOKEN}
        onError={(error: any) => {
          console.error('Map error:', error)
          setMapError('Failed to load map. Please check your internet connection and Mapbox token.')
        }}
        style={{ width: '100%', height: '100%' }}
      >
        {mapLoaded && showTickets && ticketsWithCoords.map(ticket => (
          <TicketMarker
            key={ticket.ticket_id}
            ticket={ticket}
            isSelected={selectedTicket?.ticket_id === ticket.ticket_id}
            onClick={onTicketSelect}
          />
        ))}
        {mapLoaded && showCrews && crewsWithCoords.map(crew => (
          <CrewMarker
            key={crew.team_id}
            crew={crew}
            isSelected={selectedCrew?.team_id === crew.team_id}
            onClick={setSelectedCrew}
          />
        ))}
      </Map>
    </Box>
  )
}
