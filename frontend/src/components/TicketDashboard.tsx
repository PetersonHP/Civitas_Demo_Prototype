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
  Button,
} from '@chakra-ui/react'
import { ArrowBackIcon } from '@chakra-ui/icons'
import {
  ticketService,
  Ticket,
  TicketWithRelations,
  TicketStatus,
  TicketPriority,
  Label,
} from '../services/ticketService'
import { MapView } from './MapView'
import { CommentSection } from './CommentSection'

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
  onOpenTicket: (ticket: Ticket | TicketWithRelations) => void
}

const TicketCard = ({ ticket, onOpenTicket }: TicketCardProps) => {
  const cardBg = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('transparent', 'transparent')

  // Truncate body text to fit in card
  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text
    return text.slice(0, maxLength) + '...'
  }

  // Check if ticket has relations (labels)
  const labels = (ticket as TicketWithRelations).labels || []

  return (
    <Card
      bg={cardBg}
      borderWidth="1px"
      borderColor={borderColor}
      cursor="pointer"
      onClick={() => onOpenTicket(ticket)}
      _hover={{ shadow: 'md' }}
      transition="all 0.2s"
      position="relative"
    >
      <CardBody p={3}>
        <VStack align="stretch" spacing={1.5}>
          {/* Subject */}
          <Heading size="xs" noOfLines={2}>
            {ticket.ticket_subject}
          </Heading>
          {/* Report date */}
          <Text fontSize="2xs" color="gray.500">
            Reported on {new Date(ticket.time_created).toLocaleDateString()} {new Date(ticket.time_created).toLocaleTimeString()}
          </Text>

          {/* Body preview */}
          <Text fontSize="xs" color="gray.400" noOfLines={3}>
            {truncateText(ticket.ticket_body, 120)}
          </Text>

          {/* Status and Priority */}
          <HStack spacing={1.5}>
            <Badge colorScheme={getStatusColor(ticket.status)} fontSize="2xs">
              {formatStatus(ticket.status)}
            </Badge>
            <Badge colorScheme={getPriorityColor(ticket.priority)} fontSize="2xs">
              {formatPriority(ticket.priority)}
            </Badge>
          </HStack>

          {/* Labels with custom colors */}
          {labels.length > 0 && (
            <HStack spacing={0.8} wrap="wrap">
              {labels.map((label: Label) => (
                <Badge
                  key={label.label_id}
                  style={{ backgroundColor: label.color_hex }}
                  color="white"
                  fontSize="2xs"
                >
                  {label.label_name}
                </Badge>
              ))}
            </HStack>
          )}
        </VStack>
      </CardBody>
    </Card>
  )
}

export const TicketDashboard = () => {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [openedTicket, setOpenedTicket] = useState<Ticket | TicketWithRelations | null>(null)

  // Filter states
  const [selectedStatus, setSelectedStatus] = useState<TicketStatus | undefined>(undefined)
  const [selectedPriority, setSelectedPriority] = useState<TicketPriority | undefined>(undefined)

  const headerBg = useColorModeValue('white', '#4b2e83')
  const filterBg = useColorModeValue('white', 'gray.700')
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
        borderColor="transparent"
        p={3}
        shadow="sm"
      >
        <HStack spacing={3}>
          <Image
            src="/Civitas_white.png"
            alt="Civitas Logo"
            h="32px"
            objectFit="contain"
          />
          <Heading size="md">Dispatcher Dashboard</Heading>
        </HStack>
      </Box>

      {/* Main content area */}
      <Flex direction="column" flex={1} overflow="hidden">
        {/* Filter section spanning full width at top */}
        <Box
          bg={filterBg}
          borderBottom="1px"
          borderColor="transparent"
          py={1.5}
          px={3}
        >
          <Flex justify="left">
            <HStack spacing={4.5}>
              <HStack spacing={1.5}>
                <FormLabel fontSize="xs" mb={0}>Status</FormLabel>
                <Select
                  placeholder="All statuses"
                  value={selectedStatus || ''}
                  onChange={(e) => setSelectedStatus(e.target.value as TicketStatus || undefined)}
                  size="xs"
                  w="144px"
                  fontSize="xs"
                >
                  {Object.values(TicketStatus).map(status => (
                    <option key={status} value={status}>
                      {formatStatus(status)}
                    </option>
                  ))}
                </Select>
              </HStack>
              <HStack spacing={1.5}>
                <FormLabel fontSize="xs" mb={0}>Priority</FormLabel>
                <Select
                  placeholder="All priorities"
                  value={selectedPriority || ''}
                  onChange={(e) => setSelectedPriority(e.target.value as TicketPriority || undefined)}
                  size="xs"
                  w="144px"
                  fontSize="xs"
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
          {/* Left side - Ticket list (50%) */}
          <Box
            w="50%"
            borderRight="1px"
            borderColor="transparent"
            overflowY="auto"
            bg={listBg}
            p={4}
          >
            {openedTicket ? (
              /* Ticket detail view */
              <VStack align="stretch" spacing={4}>
                <Button
                  leftIcon={<ArrowBackIcon />}
                  onClick={() => setOpenedTicket(null)}
                  colorScheme="blue"
                  variant="outline"
                  size="sm"
                  alignSelf="flex-start"
                >
                </Button>
                <Box>
                  <Heading size="lg" mb={2}>
                    {openedTicket.ticket_subject}
                  </Heading>
                  <Text fontSize="sm" color="gray.500" mb={4}>
                    Ticket ID: {openedTicket.ticket_id}
                  </Text>
                  <HStack spacing={2} mb={4}>
                    <Badge colorScheme={getStatusColor(openedTicket.status)}>
                      {formatStatus(openedTicket.status)}
                    </Badge>
                    <Badge colorScheme={getPriorityColor(openedTicket.priority)}>
                      {formatPriority(openedTicket.priority)}
                    </Badge>
                    <Text fontSize="sm" color="gray.500">
                      Reported on {new Date(openedTicket.time_created).toLocaleDateString()} at {new Date(openedTicket.time_created).toLocaleTimeString()}
                    </Text>
                  </HStack>
                  <Text mb={2} fontWeight="semibold"></Text>
                  <Text mb={4}>{openedTicket.ticket_body}</Text>

                  {/* Comments Section */}
                  <CommentSection
                    ticketId={openedTicket.ticket_id}
                    userId="b3cdcf8f-3c7a-4001-b7fb-646e909d2fa9"
                  />
                </Box>
              </VStack>
            ) : loading ? (
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
              <VStack spacing={2.5} align="stretch">
                {tickets.map((ticket) => (
                  <TicketCard
                    key={ticket.ticket_id}
                    ticket={ticket}
                    onOpenTicket={setOpenedTicket}
                  />
                ))}
              </VStack>
            )}
          </Box>

          {/* Right side - Map view (50%) */}
          <Box flex={1} position="relative">
            <MapView
              tickets={openedTicket ? [openedTicket] : tickets}
              selectedTicket={openedTicket}
              onTicketSelect={setOpenedTicket}
            />
          </Box>
        </Flex>
      </Flex>
    </Flex>
  )
}
