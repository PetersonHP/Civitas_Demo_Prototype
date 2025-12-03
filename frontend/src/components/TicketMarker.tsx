import { Marker } from 'react-map-gl/mapbox'
import { Tooltip, Text, VStack } from '@chakra-ui/react'
import { Ticket } from '../services/ticketService'
import { getPriorityMarkerColor } from '../utils/mapHelpers'

interface TicketMarkerProps {
  ticket: Ticket
  isSelected: boolean
  onClick: (ticket: Ticket) => void
}

/**
 * Individual ticket marker component for the map
 * Displays a colored circle based on ticket priority with hover tooltip
 */
export const TicketMarker = ({ ticket, isSelected, onClick }: TicketMarkerProps) => {
  if (!ticket.location_coordinates) return null

  const markerColor = getPriorityMarkerColor(ticket.priority)
  const size = isSelected ? 32 : 24
  const radius = isSelected ? 13 : 10
  const strokeWidth = isSelected ? 3 : 2
  const strokeColor = isSelected ? '#3182CE' : '#fff' // Chakra blue.600 for selected

  const formatStatus = (status: string): string => {
    return status.charAt(0).toUpperCase() + status.slice(1).replace(/_/g, ' ')
  }

  const formatPriority = (priority: string): string => {
    return priority.charAt(0).toUpperCase() + priority.slice(1)
  }

  const formatDateTime = (dateString: string): string => {
    const date = new Date(dateString)
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`
  }

  return (
    <Marker
      longitude={ticket.location_coordinates.lng}
      latitude={ticket.location_coordinates.lat}
      onClick={(e: any) => {
        e.originalEvent.stopPropagation() // Prevent map click event
        onClick(ticket)
      }}
      style={{ zIndex: isSelected ? 1000 : 1 }}
    >
      <Tooltip
        label={
          <VStack align="start" spacing={1}>
            <Text fontWeight="bold" fontSize="sm" noOfLines={2}>
              {ticket.ticket_subject}
            </Text>
            <Text fontSize="xs" color="gray.300" noOfLines={2}>
              {ticket.ticket_body.length > 60
                ? ticket.ticket_body.slice(0, 60) + '...'
                : ticket.ticket_body}
            </Text>
            <Text fontSize="xs" mt={1}>
              Priority: {formatPriority(ticket.priority)} | Status: {formatStatus(ticket.status)}
            </Text>
            <Text fontSize="xs" color="gray.400">
              Created: {formatDateTime(ticket.time_created)}
            </Text>
            {ticket.time_updated && (
              <Text fontSize="xs" color="gray.400">
                Updated: {formatDateTime(ticket.time_updated)}
              </Text>
            )}
          </VStack>
        }
        placement="top"
        hasArrow
        openDelay={200}
      >
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          style={{
            cursor: 'pointer',
            transition: 'all 0.2s ease-in-out',
            filter: isSelected ? 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))' : 'none'
          }}
        >
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill={markerColor}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
          />
        </svg>
      </Tooltip>
    </Marker>
  )
}
