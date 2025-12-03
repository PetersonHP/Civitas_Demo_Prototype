import { Marker } from 'react-map-gl/mapbox'
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
  const size = isSelected ? 32 : 24
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

  // All crew markers use wrench icon
  const renderIcon = () => {
    return (
      /*
      * Original from https://copyicon.com/:
      * <svg id='Open_End_Wrench_24' width='24' height='24' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'><rect width='24' height='24' stroke='none' fill='#000000' opacity='0'/>
      * <g transform="matrix(1 0 0 1 12 12)" >
      * <path style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-dashoffset: 0; stroke-linejoin: miter; stroke-miterlimit: 4; fill: rgb(0,0,0); fill-rule: nonzero; opacity: 1;" transform=" translate(-12, -12)" d="M 21.181 4.215 L 18.596 6.8 C 18.399 6.987 18.154 7.085 17.898 7.085 C 17.642 7.085 17.397 6.987 17.2 6.8 C 16.817 6.417 16.817 5.788 17.2 5.404 L 19.785 2.819 C 18.861 2.219 17.731 1.934 16.512 2.013 C 15.038 2.1109999999999998 13.612 2.7399999999999998 12.600000000000001 3.753 C 11.558000000000002 4.795 11.135000000000002 6.063000000000001 11.371000000000002 7.41 C 11.410000000000002 7.646 11.469000000000003 7.872 11.548000000000002 8.108 L 8.108000000000002 11.548 C 7.8720000000000026 11.469 7.646000000000003 11.41 7.410000000000002 11.371 C 6.063000000000002 11.135 4.795000000000002 11.558 3.753000000000002 12.600000000000001 C 2.741000000000002 13.613000000000001 2.111000000000002 15.038000000000002 2.0130000000000017 16.512 C 1.9340000000000017 17.741 2.2190000000000016 18.871000000000002 2.8190000000000017 19.795 L 5.404 17.2 C 5.787 16.817 6.417 16.817 6.8 17.2 C 7.183 17.583 7.183 18.213 6.8 18.596 L 4.215 21.181 C 5.031 21.722 6.024 21.997 7.085 21.997 C 7.213 21.997 7.35 21.997 7.4879999999999995 21.987 C 8.962 21.889 10.388 21.259999999999998 11.399999999999999 20.247 C 12.441999999999998 19.205 12.864999999999998 17.937 12.628999999999998 16.59 C 12.589999999999998 16.354 12.530999999999997 16.128 12.451999999999998 15.892 L 15.891999999999998 12.452 C 16.127999999999997 12.531 16.354 12.59 16.589999999999996 12.629 C 16.835999999999995 12.677999999999999 17.071999999999996 12.698 17.307999999999996 12.698 C 18.388999999999996 12.698 19.391999999999996 12.256 20.246999999999996 11.401 C 21.258999999999997 10.388 21.888999999999996 8.963 21.986999999999995 7.489 C 22.066 6.269 21.781 5.139 21.181 4.215 z" stroke-linecap="round" />
      * </g>
      * </svg>
      */
      <g transform="matrix(0.7 0 0 0.7 12 12)">
        <path
          style={{
            stroke: 'none',
            strokeWidth: 1,
            strokeDasharray: 'none',
            strokeLinecap: 'butt',
            strokeDashoffset: 0,
            strokeLinejoin: 'miter',
            strokeMiterlimit: 4,
            fill: '#ffffff',
            fillRule: 'nonzero',
            opacity: 1
          }}
          transform="translate(-12, -12)"
          d="M 21.181 4.215 L 18.596 6.8 C 18.399 6.987 18.154 7.085 17.898 7.085 C 17.642 7.085 17.397 6.987 17.2 6.8 C 16.817 6.417 16.817 5.788 17.2 5.404 L 19.785 2.819 C 18.861 2.219 17.731 1.934 16.512 2.013 C 15.038 2.1109999999999998 13.612 2.7399999999999998 12.600000000000001 3.753 C 11.558000000000002 4.795 11.135000000000002 6.063000000000001 11.371000000000002 7.41 C 11.410000000000002 7.646 11.469000000000003 7.872 11.548000000000002 8.108 L 8.108000000000002 11.548 C 7.8720000000000026 11.469 7.646000000000003 11.41 7.410000000000002 11.371 C 6.063000000000002 11.135 4.795000000000002 11.558 3.753000000000002 12.600000000000001 C 2.741000000000002 13.613000000000001 2.111000000000002 15.038000000000002 2.0130000000000017 16.512 C 1.9340000000000017 17.741 2.2190000000000016 18.871000000000002 2.8190000000000017 19.795 L 5.404 17.2 C 5.787 16.817 6.417 16.817 6.8 17.2 C 7.183 17.583 7.183 18.213 6.8 18.596 L 4.215 21.181 C 5.031 21.722 6.024 21.997 7.085 21.997 C 7.213 21.997 7.35 21.997 7.4879999999999995 21.987 C 8.962 21.889 10.388 21.259999999999998 11.399999999999999 20.247 C 12.441999999999998 19.205 12.864999999999998 17.937 12.628999999999998 16.59 C 12.589999999999998 16.354 12.530999999999997 16.128 12.451999999999998 15.892 L 15.891999999999998 12.452 C 16.127999999999997 12.531 16.354 12.59 16.589999999999996 12.629 C 16.835999999999995 12.677999999999999 17.071999999999996 12.698 17.307999999999996 12.698 C 18.388999999999996 12.698 19.391999999999996 12.256 20.246999999999996 11.401 C 21.258999999999997 10.388 21.888999999999996 8.963 21.986999999999995 7.489 C 22.066 6.269 21.781 5.139 21.181 4.215 z"
          strokeLinecap="round"
        />
      </g>
    )
  }

  return (
    <Marker
      longitude={crew.location_coordinates.lng}
      latitude={crew.location_coordinates.lat}
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
          <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            style={{
              cursor: 'pointer',
              transition: 'all 0.2s ease-in-out',
              filter: isSelected ? 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))' : 'none',
              opacity: opacity
            }}
          >
            <circle
              cx="12"
              cy="12"
              r="10"
              fill={markerColor}
            />
            {renderIcon()}
          </svg>
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
