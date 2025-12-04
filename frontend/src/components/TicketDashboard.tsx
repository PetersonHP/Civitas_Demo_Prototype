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
  IconButton,
  useToast,
  Input,
  Tag,
  TagLabel,
  TagCloseButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
} from '@chakra-ui/react'
import { ArrowBackIcon, CloseIcon, AddIcon } from '@chakra-ui/icons'
import { FaExclamationTriangle, FaHardHat, FaRoad, FaSnowplow, FaTrashAlt, FaTree, FaWater } from 'react-icons/fa'
import {
  ticketService,
  Ticket,
  TicketWithRelations,
  TicketStatus,
  TicketPriority,
  Label,
  SupportCrew,
} from '../services/ticketService'
import { userService, CivitasUser } from '../services/userService'
import { labelService, Label as LabelType } from '../services/labelService'
import { crewService } from '../services/crewService'
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

// Get crew type icon
const getCrewIcon = (crewType: string) => {
  switch (crewType) {
    case 'pothole crew':
      return <FaRoad />
    case 'drain crew':
      return <FaWater />
    case 'tree crew':
      return <FaTree />
    case 'sign crew':
      return <FaExclamationTriangle />
    case 'snow crew':
      return <FaSnowplow />
    case 'sanitation crew':
      return <FaTrashAlt />
    default:
      return <FaHardHat />
  }
}

// Format crew type for display
const formatCrewType = (crewType: string): string => {
  return crewType
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

interface TicketCardProps {
  ticket: Ticket | TicketWithRelations
  onOpenTicket: (ticket: Ticket | TicketWithRelations) => void
}

const TicketCard = ({ ticket, onOpenTicket }: TicketCardProps) => {
  const cardBg = useColorModeValue('white', 'gray.700')
  const borderColor = useColorModeValue('transparent', 'transparent')

  // Truncate body text to fit in card
  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text
    return text.slice(0, maxLength) + '...'
  }

  // Check if ticket has relations
  const ticketWithRelations = ticket as TicketWithRelations
  const labels = ticketWithRelations.labels || []

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
          {/* Subject with status badge in upper right */}
          <Flex justify="space-between" align="start" gap={2}>
            <Heading size="xs" noOfLines={2} flex={1}>
              {ticket.ticket_subject}
            </Heading>
            <Badge colorScheme={getStatusColor(ticket.status)} fontSize="2xs" flexShrink={0}>
              {formatStatus(ticket.status)}
            </Badge>
          </Flex>

          {/* Report date */}
          <Text fontSize="2xs" color="gray.500">
            Reported on {new Date(ticket.time_created).toLocaleDateString()} {new Date(ticket.time_created).toLocaleTimeString()}
          </Text>

          {/* Body preview */}
          <Text fontSize="xs" color="gray.400" noOfLines={3}>
            {truncateText(ticket.ticket_body, 120)}
          </Text>

          {/* Priority only */}
          <HStack spacing={1.5}>
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
  const [tickets, setTickets] = useState<TicketWithRelations[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [openedTicket, setOpenedTicket] = useState<Ticket | TicketWithRelations | null>(null)

  // User search and assignee states
  const [userSearchQuery, setUserSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<CivitasUser[]>([])
  const [searchLoading, setSearchLoading] = useState(false)
  const [showUserSearch, setShowUserSearch] = useState(false)

  // Label search states
  const [labelSearchQuery, setLabelSearchQuery] = useState('')
  const [labelSearchResults, setLabelSearchResults] = useState<LabelType[]>([])
  const [labelSearchLoading, setLabelSearchLoading] = useState(false)
  const [showLabelSearch, setShowLabelSearch] = useState(false)

  // Crew search states
  const [crewSearchQuery, setCrewSearchQuery] = useState('')
  const [crewSearchResults, setCrewSearchResults] = useState<SupportCrew[]>([])
  const [crewSearchLoading, setCrewSearchLoading] = useState(false)
  const [showCrewSearch, setShowCrewSearch] = useState(false)
  const [hoveredCrewId, setHoveredCrewId] = useState<string | null>(null)

  // Filter states
  const [selectedStatus, setSelectedStatus] = useState<TicketStatus | undefined>(undefined)
  const [selectedPriority, setSelectedPriority] = useState<TicketPriority | undefined>(undefined)

  const civitasBg = useColorModeValue('white', '#4b2e83')
  const filterBg = useColorModeValue('white', 'gray.700')
  const listBg = useColorModeValue('gray.50', 'gray.900')
  const toast = useToast()

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

  // Search users when query changes
  useEffect(() => {
    const searchUsers = async () => {
      if (!userSearchQuery.trim()) {
        setSearchResults([])
        return
      }

      try {
        setSearchLoading(true)
        const users = await userService.getUsers({
          search: userSearchQuery,
          limit: 10,
        })
        setSearchResults(users)
      } catch (err) {
        console.error('Failed to search users:', err)
        setSearchResults([])
      } finally {
        setSearchLoading(false)
      }
    }

    const debounceTimer = setTimeout(searchUsers, 300)
    return () => clearTimeout(debounceTimer)
  }, [userSearchQuery])

  // Search labels when query changes
  useEffect(() => {
    const searchLabels = async () => {
      if (!labelSearchQuery.trim()) {
        setLabelSearchResults([])
        return
      }

      try {
        setLabelSearchLoading(true)
        const labels = await labelService.getLabels({
          search: labelSearchQuery,
          limit: 20,
        })
        setLabelSearchResults(labels)
      } catch (err) {
        console.error('Failed to search labels:', err)
        setLabelSearchResults([])
      } finally {
        setLabelSearchLoading(false)
      }
    }

    const debounceTimer = setTimeout(searchLabels, 300)
    return () => clearTimeout(debounceTimer)
  }, [labelSearchQuery])

  // Search crews when query changes
  useEffect(() => {
    const searchCrews = async () => {
      if (!crewSearchQuery.trim()) {
        setCrewSearchResults([])
        return
      }

      try {
        setCrewSearchLoading(true)
        const crews = await crewService.getCrews({
          search: crewSearchQuery,
          limit: 10,
        })
        setCrewSearchResults(crews)
      } catch (err) {
        console.error('Failed to search crews:', err)
        setCrewSearchResults([])
      } finally {
        setCrewSearchLoading(false)
      }
    }

    const debounceTimer = setTimeout(searchCrews, 300)
    return () => clearTimeout(debounceTimer)
  }, [crewSearchQuery])

  // Helper function to refresh a ticket and update both the opened ticket and list
  const refreshTicket = async (ticketId: string) => {
    try {
      const updatedTicket = await ticketService.getTicket(ticketId)
      setOpenedTicket(updatedTicket)

      // Update the ticket in the list as well
      setTickets(prevTickets =>
        prevTickets.map(t => (t.ticket_id === ticketId ? updatedTicket : t))
      )
    } catch (err) {
      console.error('Failed to refresh ticket:', err)
    }
  }

  // Handle opening a ticket - fetch full details
  const handleOpenTicket = async (ticket: Ticket | TicketWithRelations) => {
    try {
      const fullTicket = await ticketService.getTicket(ticket.ticket_id)
      setOpenedTicket(fullTicket)
    } catch (err) {
      console.error('Failed to fetch ticket details:', err)
      toast({
        title: 'Error',
        description: 'Failed to load ticket details',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  // Handle adding a user assignee
  const handleAddAssignee = async (user: CivitasUser) => {
    if (!openedTicket) return

    const ticketWithRelations = openedTicket as TicketWithRelations
    const currentAssigneeIds = ticketWithRelations.user_assignees?.map(u => u.user_id) || []

    if (currentAssigneeIds.includes(user.user_id)) {
      toast({
        title: 'Already tagged',
        description: 'This user is already tagged to the ticket',
        status: 'info',
        duration: 2000,
        isClosable: true,
      })
      return
    }

    try {
      await ticketService.assignUsers(openedTicket.ticket_id, [...currentAssigneeIds, user.user_id])

      // Refresh the ticket data
      await refreshTicket(openedTicket.ticket_id)

      // Clear search
      setUserSearchQuery('')
      setShowUserSearch(false)

      toast({
        title: 'User tagged',
        description: `${user.firstname} ${user.lastname} has been tagged to the ticket`,
        status: 'success',
        duration: 2000,
        isClosable: true,
      })
    } catch (err) {
      console.error('Failed to assign user:', err)
      toast({
        title: 'Error',
        description: 'Failed to assign user to ticket',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  // Handle removing a user assignee
  const handleRemoveAssignee = async (userId: string, userName: string) => {
    if (!openedTicket) return

    try {
      await ticketService.unassignUser(openedTicket.ticket_id, userId)

      // Refresh the ticket data
      await refreshTicket(openedTicket.ticket_id)

      toast({
        title: 'User untagged',
        description: `${userName} has been removed from the ticket`,
        status: 'success',
        duration: 2000,
        isClosable: true,
      })
    } catch (err) {
      console.error('Failed to unassign user:', err)
      toast({
        title: 'Error',
        description: 'Failed to remove user from ticket',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  // Handle adding a label
  const handleAddLabel = async (label: LabelType) => {
    if (!openedTicket) return

    const ticketWithRelations = openedTicket as TicketWithRelations
    const currentLabelIds = ticketWithRelations.labels?.map(l => l.label_id) || []

    if (currentLabelIds.includes(label.label_id)) {
      toast({
        title: 'Already added',
        description: 'This label is already on the ticket',
        status: 'info',
        duration: 2000,
        isClosable: true,
      })
      return
    }

    try {
      await ticketService.setLabels(openedTicket.ticket_id, [...currentLabelIds, label.label_id])

      // Refresh the ticket data
      await refreshTicket(openedTicket.ticket_id)

      // Clear search
      setLabelSearchQuery('')
      setShowLabelSearch(false)

      toast({
        title: 'Label added',
        description: `Label "${label.label_name}" has been added to the ticket`,
        status: 'success',
        duration: 2000,
        isClosable: true,
      })
    } catch (err) {
      console.error('Failed to add label:', err)
      toast({
        title: 'Error',
        description: 'Failed to add label to ticket',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  // Handle removing a label
  const handleRemoveLabel = async (labelId: string, labelName: string) => {
    if (!openedTicket) return

    try {
      await ticketService.removeLabel(openedTicket.ticket_id, labelId)

      // Refresh the ticket data
      await refreshTicket(openedTicket.ticket_id)

      toast({
        title: 'Label removed',
        description: `Label "${labelName}" has been removed from the ticket`,
        status: 'success',
        duration: 2000,
        isClosable: true,
      })
    } catch (err) {
      console.error('Failed to remove label:', err)
      toast({
        title: 'Error',
        description: 'Failed to remove label from ticket',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  // Handle adding a crew assignee
  const handleAddCrew = async (crew: SupportCrew) => {
    if (!openedTicket) return

    const ticketWithRelations = openedTicket as TicketWithRelations
    const currentCrewIds = ticketWithRelations.crew_assignees?.map(c => c.team_id) || []

    if (currentCrewIds.includes(crew.team_id)) {
      toast({
        title: 'Already assigned',
        description: 'This crew is already assigned to the ticket',
        status: 'info',
        duration: 2000,
        isClosable: true,
      })
      return
    }

    try {
      await ticketService.assignCrews(openedTicket.ticket_id, [...currentCrewIds, crew.team_id])

      // Refresh the ticket data
      await refreshTicket(openedTicket.ticket_id)

      // Clear search
      setCrewSearchQuery('')
      setShowCrewSearch(false)

      toast({
        title: 'Crew assigned',
        description: `${crew.team_name} has been assigned to the ticket`,
        status: 'success',
        duration: 2000,
        isClosable: true,
      })
    } catch (err) {
      console.error('Failed to assign crew:', err)
      toast({
        title: 'Error',
        description: 'Failed to assign crew to ticket',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  // Handle removing a crew assignee
  const handleRemoveCrew = async (crewId: string, crewName: string) => {
    if (!openedTicket) return

    try {
      await ticketService.unassignCrew(openedTicket.ticket_id, crewId)

      // Refresh the ticket data
      await refreshTicket(openedTicket.ticket_id)

      toast({
        title: 'Crew unassigned',
        description: `${crewName} has been removed from the ticket`,
        status: 'success',
        duration: 2000,
        isClosable: true,
      })
    } catch (err) {
      console.error('Failed to unassign crew:', err)
      toast({
        title: 'Error',
        description: 'Failed to remove crew from ticket',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  // Handle updating ticket status
  const handleUpdateStatus = async (newStatus: TicketStatus) => {
    if (!openedTicket) return

    try {
      await ticketService.updateTicket(openedTicket.ticket_id, { status: newStatus })

      // Refresh the ticket data
      await refreshTicket(openedTicket.ticket_id)

      toast({
        title: 'Status updated',
        description: `Ticket status changed to ${formatStatus(newStatus)}`,
        status: 'success',
        duration: 2000,
        isClosable: true,
      })
    } catch (err) {
      console.error('Failed to update status:', err)
      toast({
        title: 'Error',
        description: 'Failed to update ticket status',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  // Handle updating ticket priority
  const handleUpdatePriority = async (newPriority: TicketPriority) => {
    if (!openedTicket) return

    try {
      await ticketService.updateTicket(openedTicket.ticket_id, { priority: newPriority })

      // Refresh the ticket data
      await refreshTicket(openedTicket.ticket_id)

      toast({
        title: 'Priority updated',
        description: `Ticket priority changed to ${formatPriority(newPriority)}`,
        status: 'success',
        duration: 2000,
        isClosable: true,
      })
    } catch (err) {
      console.error('Failed to update priority:', err)
      toast({
        title: 'Error',
        description: 'Failed to update ticket priority',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  return (
    <Flex direction="column" h="100vh">
      {/* Header */}
      <HStack spacing={3}>
        <Box
          bg={civitasBg}
          p={3}
          display="flex"
          alignItems="center"
        >
          <HStack spacing={3} align="center" direction="row">
            <Image
              src="/Civitas_white.png"
              alt="Civitas Logo"
              h="32px"
              objectFit="contain"
            />
            <Heading size="md">CIVITAS</Heading>
          </HStack>
        </Box>
        <Text fontSize="sm" color="gray.300">Dispatcher Control Center</Text>
      </HStack>

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
                  <Text mb={2} fontSize="sm" color="gray.500">
                    Reported on {new Date(openedTicket.time_created).toLocaleDateString()} at {new Date(openedTicket.time_created).toLocaleTimeString()}
                  </Text>
                  <HStack spacing={2} mb={4}>
                    <Menu>
                      <MenuButton
                        as={Badge}
                        colorScheme={getStatusColor(openedTicket.status)}
                        cursor="pointer"
                        _hover={{ opacity: 0.8 }}
                      >
                        {formatStatus(openedTicket.status)}
                      </MenuButton>
                      <MenuList>
                        {Object.values(TicketStatus).map((status) => (
                          <MenuItem
                            key={status}
                            onClick={() => handleUpdateStatus(status)}
                            bg={status === openedTicket.status ? useColorModeValue('gray.100', 'gray.700') : undefined}
                          >
                            <Badge colorScheme={getStatusColor(status)} mr={2}>
                              {formatStatus(status)}
                            </Badge>
                          </MenuItem>
                        ))}
                      </MenuList>
                    </Menu>
                    <Menu>
                      <MenuButton
                        as={Badge}
                        colorScheme={getPriorityColor(openedTicket.priority)}
                        cursor="pointer"
                        _hover={{ opacity: 0.8 }}
                      >
                        {formatPriority(openedTicket.priority)}
                      </MenuButton>
                      <MenuList>
                        {Object.values(TicketPriority).map((priority) => (
                          <MenuItem
                            key={priority}
                            onClick={() => handleUpdatePriority(priority)}
                            bg={priority === openedTicket.priority ? useColorModeValue('gray.100', 'gray.700') : undefined}
                          >
                            <Badge colorScheme={getPriorityColor(priority)} mr={2}>
                              {formatPriority(priority)}
                            </Badge>
                          </MenuItem>
                        ))}
                      </MenuList>
                    </Menu>
                  </HStack>
                  <Text mb={2} fontWeight="semibold"></Text>
                  <Text mb={4}>{openedTicket.ticket_body}</Text>
                  <Text fontSize="sm" color="gray.500" mb={4}>
                    Ticket ID: {openedTicket.ticket_id}
                  </Text>

                  {/* Assignees Section */}
                  <Box mb={4}>
                    <HStack spacing={2} mb={2}>
                      <Text fontWeight="semibold" fontSize="sm">Tagged Users</Text>
                      <Button
                        size="xs"
                        leftIcon={<AddIcon />}
                        colorScheme="blue"
                        variant="outline"
                        onClick={() => setShowUserSearch(!showUserSearch)}
                      >
                        Tag User
                      </Button>
                    </HStack>

                    {/* User Search Box */}
                    {showUserSearch && (
                      <Box mb={2} position="relative">
                        <Input
                          placeholder="Search users by name, email, or phone..."
                          value={userSearchQuery}
                          onChange={(e) => setUserSearchQuery(e.target.value)}
                          size="sm"
                          mb={1}
                        />
                        {searchLoading && (
                          <Box p={2}>
                            <Spinner size="sm" />
                          </Box>
                        )}
                        {searchResults.length > 0 && (
                          <VStack
                            align="stretch"
                            spacing={1}
                            maxH="200px"
                            overflowY="auto"
                            bg={useColorModeValue('white', 'gray.700')}
                            border="1px"
                            borderColor={useColorModeValue('gray.200', 'gray.600')}
                            borderRadius="md"
                            p={2}
                          >
                            {searchResults.map((user) => (
                              <Box
                                key={user.user_id}
                                p={2}
                                cursor="pointer"
                                _hover={{ bg: useColorModeValue('gray.100', 'gray.600') }}
                                borderRadius="sm"
                                onClick={() => handleAddAssignee(user)}
                              >
                                <Text fontSize="sm" fontWeight="medium">
                                  {user.firstname} {user.lastname}
                                </Text>
                                {user.email && (
                                  <Text fontSize="xs" color="gray.500">
                                    {user.email}
                                  </Text>
                                )}
                              </Box>
                            ))}
                          </VStack>
                        )}
                      </Box>
                    )}

                    {/* Current Assignees */}
                    {(openedTicket as TicketWithRelations).user_assignees?.length > 0 ? (
                      <VStack align="stretch" spacing={1}>
                        {(openedTicket as TicketWithRelations).user_assignees.map((user) => (
                          <HStack
                            key={user.user_id}
                            justify="space-between"
                            p={2}
                            bg={useColorModeValue('gray.50', 'gray.700')}
                            borderRadius="md"
                          >
                            <Box>
                              <Text fontSize="sm" fontWeight="medium">
                                {user.firstname} {user.lastname}
                              </Text>
                              {user.email && (
                                <Text fontSize="xs" color="gray.500">
                                  {user.email}
                                </Text>
                              )}
                            </Box>
                            <IconButton
                              icon={<CloseIcon />}
                              size="xs"
                              colorScheme="red"
                              variant="ghost"
                              aria-label="Remove assignee"
                              onClick={() => handleRemoveAssignee(user.user_id, `${user.firstname} ${user.lastname}`)}
                            />
                          </HStack>
                        ))}
                      </VStack>
                    ) : (
                      <Text fontSize="sm" color="gray.500">
                        No users assigned
                      </Text>
                    )}
                  </Box>

                  {/* Labels Section */}
                  <Box mb={4}>
                    <HStack spacing={2} mb={2}>
                      <Text fontWeight="semibold" fontSize="sm">Labels</Text>
                      <Button
                        size="xs"
                        leftIcon={<AddIcon />}
                        colorScheme="blue"
                        variant="outline"
                        onClick={() => setShowLabelSearch(!showLabelSearch)}
                      >
                        Add Label
                      </Button>
                    </HStack>

                    {/* Label Search Box */}
                    {showLabelSearch && (
                      <Box mb={2} position="relative">
                        <Input
                          placeholder="Search labels by name or description..."
                          value={labelSearchQuery}
                          onChange={(e) => setLabelSearchQuery(e.target.value)}
                          size="sm"
                          mb={1}
                        />
                        {labelSearchLoading && (
                          <Box p={2}>
                            <Spinner size="sm" />
                          </Box>
                        )}
                        {labelSearchResults.length > 0 && (
                          <VStack
                            align="stretch"
                            spacing={1}
                            maxH="200px"
                            overflowY="auto"
                            bg={useColorModeValue('white', 'gray.700')}
                            border="1px"
                            borderColor={useColorModeValue('gray.200', 'gray.600')}
                            borderRadius="md"
                            p={2}
                          >
                            {labelSearchResults.map((label) => (
                              <Box
                                key={label.label_id}
                                p={2}
                                cursor="pointer"
                                _hover={{ bg: useColorModeValue('gray.100', 'gray.600') }}
                                borderRadius="sm"
                                onClick={() => handleAddLabel(label)}
                              >
                                <HStack spacing={2}>
                                  <Tag
                                    size="sm"
                                    style={{ backgroundColor: label.color_hex }}
                                    color="white"
                                  >
                                    <TagLabel>{label.label_name}</TagLabel>
                                  </Tag>
                                  {label.label_description && (
                                    <Text fontSize="xs" color="gray.500">
                                      {label.label_description}
                                    </Text>
                                  )}
                                </HStack>
                              </Box>
                            ))}
                          </VStack>
                        )}
                      </Box>
                    )}

                    {/* Current Labels */}
                    {(openedTicket as TicketWithRelations).labels?.length > 0 ? (
                      <HStack spacing={2} wrap="wrap">
                        {(openedTicket as TicketWithRelations).labels.map((label) => (
                          <Tag
                            key={label.label_id}
                            size="md"
                            style={{ backgroundColor: label.color_hex }}
                            color="white"
                          >
                            <TagLabel>{label.label_name}</TagLabel>
                            <TagCloseButton
                              onClick={() => handleRemoveLabel(label.label_id, label.label_name)}
                            />
                          </Tag>
                        ))}
                      </HStack>
                    ) : (
                      <Text fontSize="sm" color="gray.500">
                        No labels added
                      </Text>
                    )}
                  </Box>

                  {/* Crew Assignees Section */}
                  <Box mb={4}>
                    <HStack spacing={2} mb={2}>
                      <Text fontWeight="semibold" fontSize="sm">Assigned Crews</Text>
                      <Button
                        size="xs"
                        leftIcon={<AddIcon />}
                        colorScheme="purple"
                        variant="outline"
                        onClick={() => setShowCrewSearch(!showCrewSearch)}
                      >
                        Assign Crew
                      </Button>
                    </HStack>

                    {/* Crew Search Box */}
                    {showCrewSearch && (
                      <Box mb={2} position="relative">
                        <Input
                          placeholder="Search crews by name or description..."
                          value={crewSearchQuery}
                          onChange={(e) => setCrewSearchQuery(e.target.value)}
                          size="sm"
                          mb={1}
                        />
                        {crewSearchLoading && (
                          <Box p={2}>
                            <Spinner size="sm" />
                          </Box>
                        )}
                        {crewSearchResults.length > 0 && (
                          <VStack
                            align="stretch"
                            spacing={1}
                            maxH="200px"
                            overflowY="auto"
                            bg={useColorModeValue('white', 'gray.700')}
                            border="1px"
                            borderColor={useColorModeValue('gray.200', 'gray.600')}
                            borderRadius="md"
                            p={2}
                          >
                            {crewSearchResults.map((crew) => (
                              <Box
                                key={crew.team_id}
                                p={2}
                                cursor="pointer"
                                _hover={{ bg: useColorModeValue('gray.100', 'gray.600') }}
                                borderRadius="sm"
                                onClick={() => handleAddCrew(crew)}
                                onMouseEnter={() => setHoveredCrewId(crew.team_id)}
                                onMouseLeave={() => setHoveredCrewId(null)}
                              >
                                <HStack spacing={2}>
                                  <Box
                                    bg="purple.400"
                                    color="white"
                                    p={1.5}
                                    borderRadius="md"
                                    display="flex"
                                    alignItems="center"
                                    justifyContent="center"
                                  >
                                    {getCrewIcon(crew.crew_type)}
                                  </Box>
                                  <VStack align="start" spacing={0}>
                                    <Text fontSize="sm" fontWeight="medium">
                                      {crew.team_name}
                                    </Text>
                                    <Text fontSize="xs" color="gray.500">
                                      {formatCrewType(crew.crew_type)}
                                    </Text>
                                  </VStack>
                                </HStack>
                              </Box>
                            ))}
                          </VStack>
                        )}
                      </Box>
                    )}

                    {/* Current Crew Assignees */}
                    {(openedTicket as TicketWithRelations).crew_assignees?.length > 0 ? (
                      <VStack align="stretch" spacing={1}>
                        {(openedTicket as TicketWithRelations).crew_assignees.map((crew) => (
                          <HStack
                            key={crew.team_id}
                            justify="space-between"
                            p={2}
                            bg={useColorModeValue('purple.50', 'purple.900')}
                            borderRadius="md"
                          >
                            <HStack spacing={2}>
                              <Box
                                bg="purple.400"
                                color="white"
                                p={1.5}
                                borderRadius="md"
                                display="flex"
                                alignItems="center"
                                justifyContent="center"
                              >
                                {getCrewIcon(crew.crew_type)}
                              </Box>
                              <VStack align="start" spacing={0}>
                                <Text fontSize="sm" fontWeight="medium">
                                  {crew.team_name}
                                </Text>
                                <Text fontSize="xs" color="gray.500">
                                  {formatCrewType(crew.crew_type)}
                                </Text>
                              </VStack>
                            </HStack>
                            <IconButton
                              icon={<CloseIcon />}
                              size="xs"
                              colorScheme="red"
                              variant="ghost"
                              aria-label="Remove crew"
                              onClick={() => handleRemoveCrew(crew.team_id, crew.team_name)}
                            />
                          </HStack>
                        ))}
                      </VStack>
                    ) : (
                      <Text fontSize="sm" color="gray.500">
                        No crews assigned
                      </Text>
                    )}
                  </Box>

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
                    onOpenTicket={handleOpenTicket}
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
              assignedCrews={(openedTicket as TicketWithRelations)?.crew_assignees || []}
              showAllCrews={showCrewSearch}
              hoveredCrewId={hoveredCrewId}
            />
          </Box>
        </Flex>
      </Flex>
    </Flex>
  )
}
