import { useState, useEffect } from 'react'
import {
  Box,
  Flex,
  Heading,
  Image,
  VStack,
  HStack,
  Card,
  CardBody,
  Text,
  Badge,
  Spinner,
  Select,
  FormLabel,
  useColorModeValue,
} from '@chakra-ui/react'
import {
  ticketService,
  Ticket,
  TicketWithRelations,
  TicketStatus,
  TicketPriority,
  Label,
} from '../services/ticketService'
import { MapView } from './MapView'

// Color coding for status
const getStatusColor = (status: TicketStatus): string => {
  const colors: Record<TicketStatus, string> = {
    [TicketStatus.AWAITING_RESPONSE]: 'yellow',
    [TicketStatus.RESPONSE_IN_PROGRESS]: 'blue',
    [TicketStatus.RESOLVED]: 'green',
  }
  return colors[status]
}

// Color coding for priority
const getPriorityColor = (priority: TicketPriority): string => {
  const colors: Record<TicketPriority, string> = {
    [TicketPriority.LOW]: 'green',
    [TicketPriority.MEDIUM]: 'blue',
    [TicketPriority.HIGH]: 'red',
  }
  return colors[priority]
}

// Format status for display
const formatStatus = (status: string): string => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

// Format priority for display
const formatPriority = (priority: string): string => {
  return priority.charAt(0).toUpperCase() + priority.slice(1)
}

interface TicketCardProps {
  ticket: Ticket | TicketWithRelations
  onClick: (ticket: Ticket | TicketWithRelations) => void
  isSelected: boolean
}

const TicketCard = ({ ticket, onClick, isSelected }: TicketCardProps) => {
  const cardBg = useColorModeValue('white', 'gray.800')
  const selectedBg = useColorModeValue('blue.50', 'blue.900')
  const borderColor = useColorModeValue('gray.200', 'gray.600')
  const selectedBorderColor = useColorModeValue('blue.500', 'blue.400')

  // Truncate body text to fit in card
  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text
    return text.slice(0, maxLength) + '...'
  }

  // Check if ticket has relations (labels)
  const labels = (ticket as TicketWithRelations).labels || []

  return (
    <Card
      bg={isSelected ? selectedBg : cardBg}
      borderWidth="1px"
      borderColor={isSelected ? selectedBorderColor : borderColor}
      cursor="pointer"
      onClick={() => onClick(ticket)}
      _hover={{ shadow: 'md' }}
      transition="all 0.2s"
    >
      <CardBody p={4}>
        <VStack align="stretch" spacing={2}>
          {/* Subject */}
          <Heading size="sm" noOfLines={2}>
            {ticket.ticket_subject}
          </Heading>

          {/* Body preview */}
          <Text fontSize="sm" color="gray.600" noOfLines={3}>
            {truncateText(ticket.ticket_body, 120)}
          </Text>

          {/* Status and Priority */}
          <HStack spacing={2}>
            <Badge colorScheme={getStatusColor(ticket.status)} fontSize="xs">
              {formatStatus(ticket.status)}
            </Badge>
            <Badge colorScheme={getPriorityColor(ticket.priority)} fontSize="xs">
              {formatPriority(ticket.priority)}
            </Badge>
          </HStack>

          {/* Labels with custom colors */}
          {labels.length > 0 && (
            <HStack spacing={1} wrap="wrap">
              {labels.map((label: Label) => (
                <Badge
                  key={label.label_id}
                  style={{ backgroundColor: label.color_hex }}
                  color="white"
                  fontSize="xs"
                >
                  {label.label_name}
                </Badge>
              ))}
            </HStack>
          )}

          {/* Report date */}
          <Text fontSize="xs" color="gray.500">
            {new Date(ticket.time_created).toLocaleDateString()} {new Date(ticket.time_created).toLocaleTimeString()}
          </Text>
        </VStack>
      </CardBody>
    </Card>
  )
}

export const TicketDashboard = () => {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null)

  // Filter states
  const [selectedStatus, setSelectedStatus] = useState<TicketStatus | undefined>(undefined)
  const [selectedPriority, setSelectedPriority] = useState<TicketPriority | undefined>(undefined)

  const headerBg = useColorModeValue('white', 'gray.800')
  const filterBg = useColorModeValue('white', 'gray.800')
  const listBg = useColorModeValue('gray.50', 'gray.900')

  // Fetch tickets when filters change
  useEffect(() => {
    const fetchTickets = async () => {
      try {
        setLoading(true)
        // Fetch tickets with API-level filtering
        const ticketList = await ticketService.getTickets({
          limit: 100,
          status: selectedStatus,
          priority: selectedPriority,
        })

        setTickets(ticketList)
        setError(null)
      } catch (err) {
        setError('Failed to fetch tickets. Make sure the backend is running.')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchTickets()
  }, [selectedStatus, selectedPriority])

  return (
    <Flex direction="column" h="100vh">
      {/* Header */}
      <Box
        bg={headerBg}
        borderBottom="1px"
        borderColor="gray.200"
        p={4}
        shadow="sm"
      >
        <HStack spacing={4}>
          <Image
            src="/Civitas_white.png"
            alt="Civitas Logo"
            h="40px"
            objectFit="contain"
          />
          <Heading size="lg">Dispatcher Dashboard</Heading>
        </HStack>
      </Box>

      {/* Main content area */}
      <Flex direction="column" flex={1} overflow="hidden">
        {/* Filter section spanning full width at top */}
        <Box
          bg={filterBg}
          borderBottom="1px"
          borderColor="gray.200"
          py={2}
          px={4}
        >
          <Flex justify="left">
            <HStack spacing={6}>
              <HStack spacing={2}>
                <FormLabel fontSize="sm" mb={0}>Status</FormLabel>
                <Select
                  placeholder="All statuses"
                  value={selectedStatus || ''}
                  onChange={(e) => setSelectedStatus(e.target.value as TicketStatus || undefined)}
                  size="sm"
                  w="180px"
                >
                  {Object.values(TicketStatus).map(status => (
                    <option key={status} value={status}>
                      {formatStatus(status)}
                    </option>
                  ))}
                </Select>
              </HStack>
              <HStack spacing={2}>
                <FormLabel fontSize="sm" mb={0}>Priority</FormLabel>
                <Select
                  placeholder="All priorities"
                  value={selectedPriority || ''}
                  onChange={(e) => setSelectedPriority(e.target.value as TicketPriority || undefined)}
                  size="sm"
                  w="180px"
                >
                  {Object.values(TicketPriority).map(priority => (
                    <option key={priority} value={priority}>
                      {formatPriority(priority)}
                    </option>
                  ))}
                </Select>
              </HStack>
            </HStack>
          </Flex>
        </Box>

        <Flex flex={1} overflow="hidden">
          {/* Left side - Ticket list (25%) */}
          <Box
            w="33%"
            borderRight="1px"
            borderColor="gray.200"
            overflowY="auto"
            bg={listBg}
            p={4}
          >
            {loading ? (
              <Flex justify="center" align="center" h="full">
                <Spinner size="xl" color="blue.500" />
              </Flex>
            ) : error ? (
              <Text color="red.500" textAlign="center">
                {error}
              </Text>
            ) : tickets.length === 0 ? (
              <Text color="gray.500" textAlign="center">
                No tickets match the current filters
              </Text>
            ) : (
              <VStack spacing={3} align="stretch">
                {tickets.map((ticket) => (
                  <TicketCard
                    key={ticket.ticket_id}
                    ticket={ticket}
                    onClick={setSelectedTicket}
                    isSelected={selectedTicket?.ticket_id === ticket.ticket_id}
                  />
                ))}
              </VStack>
            )}
          </Box>

          {/* Right side - Map view (75%) */}
          <Box flex={1} position="relative">
            <MapView
              tickets={tickets}
              selectedTicket={selectedTicket}
              onTicketSelect={setSelectedTicket}
            />
          </Box>
        </Flex>
      </Flex>
    </Flex>
  )
}
