import { Marker } from 'react-map-gl/mapbox'
import { FaExclamationTriangle, FaHardHat, FaRoad, FaSnowplow, FaTrashAlt, FaTree, FaWater } from "react-icons/fa";
import { Tooltip, Text, VStack } from '@chakra-ui/react'
import { SupportCrew } from '../services/ticketService'

interface CrewMarkerProps {
  crew: SupportCrew
  isSelected: boolean
  onClick: (crew: SupportCrew) => void
}

/**
 * Individual crew marker component for the map
 * Displays a purple circular marker with crew type icon
 */
export const CrewMarker = ({ crew, isSelected, onClick }: CrewMarkerProps) => {
  if (!crew.location_coordinates) return null

  const markerColor = '#9F7AEA' // Chakra purple.400
  const size = 24
  const scale = isSelected ? 1.33 : 1
  const opacity = 0.75

  const formatStatus = (status: string): string => {
    return status.charAt(0).toUpperCase() + status.slice(1).replace(/_/g, ' ')
  }

  const formatCrewType = (crewType: string): string => {
    return crewType
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  const formatDateTime = (dateString: string): string => {
    const date = new Date(dateString)
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`
  }

  const renderIcon = () => {
    switch (crew.crew_type) {
      case 'pothole crew':
        return <FaRoad />;
      case 'drain crew':
        return <FaWater />;
      case 'tree crew':
        return <FaTree />;
      case 'sign crew':
        return <FaExclamationTriangle />;
      case 'snow crew':
        return <FaSnowplow />;
      case 'sanitation crew':
        return <FaTrashAlt />;
      default:
        return <FaHardHat />;
    }
  }

  return (
    <Marker
      longitude={crew.location_coordinates.lng}
      latitude={crew.location_coordinates.lat}
      anchor="center"
      onClick={(e: any) => {
        e.originalEvent.stopPropagation()
        onClick(crew)
      }}
      style={{ zIndex: isSelected ? 1000 : 1 }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Tooltip
          label={
            <VStack align="start" spacing={1}>
              <Text fontWeight="bold" fontSize="sm">
                {crew.team_name}
              </Text>
              {crew.description && (
                <Text fontSize="xs" color="gray.300" noOfLines={2}>
                  {crew.description}
                </Text>
              )}
              <Text fontSize="xs" mt={1}>
                Type: {formatCrewType(crew.crew_type)}
              </Text>
              <Text fontSize="xs">
                Status: {formatStatus(crew.status)}
              </Text>
              <Text fontSize="xs" color="gray.400">
                Created: {formatDateTime(crew.time_created)}
              </Text>
              {crew.time_edited && (
                <Text fontSize="xs" color="gray.400">
                  Updated: {formatDateTime(crew.time_edited)}
                </Text>
              )}
            </VStack>
          }
          placement="top"
          hasArrow
          openDelay={200}
          bg="gray.700"
          color="white"
        >
          <div
            style={{
              position: 'relative',
              width: `${size}px`,
              height: `${size}px`,
              cursor: 'pointer',
              transition: 'transform 0.2s ease-in-out, filter 0.2s ease-in-out',
              transform: `scale(${scale})`,
              filter: isSelected ? 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))' : 'none',
            }}
          >
            <svg
              width={size}
              height={size}
              viewBox="0 0 24 24"
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                opacity: opacity
              }}
            >
              <circle
                cx="12"
                cy="12"
                r="10"
                fill={markerColor}
              />
            </svg>
            <div
              style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: `${size * 0.5}px`,
              }}
            >
              {renderIcon()}
            </div>
          </div>
        </Tooltip>
        <div
          style={{
            color: markerColor,
            fontSize: '12px',
            fontWeight: 'bold',
            marginTop: '4px',
            textAlign: 'center',
            maxWidth: '240px',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            textShadow: '0 1px 2px rgba(0,0,0,0.8), 0 0 4px rgba(0,0,0,0.5)',
            pointerEvents: 'none'
          }}
        >
          {crew.team_name}
        </div>
      </div>
    </Marker>
  )
}
