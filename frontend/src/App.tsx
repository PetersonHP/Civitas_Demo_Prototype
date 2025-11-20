import { useState, useEffect } from 'react'
import {
  Box,
  Button,
  Container,
  Heading,
  Input,
  VStack,
  HStack,
  Card,
  CardBody,
  Text,
  Spinner,
  IconButton,
  useColorMode,
  useColorModeValue,
} from '@chakra-ui/react'
import { DeleteIcon, MoonIcon, SunIcon } from '@chakra-ui/icons'
import { apiService } from './services/api'

interface Item {
  id: number
  name: string
  description: string | null
  created_at: string
  updated_at: string | null
}

function App() {
  const [items, setItems] = useState<Item[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [newItemName, setNewItemName] = useState('')
  const [newItemDescription, setNewItemDescription] = useState('')

  // Dark mode hooks
  const { colorMode, toggleColorMode } = useColorMode()
  const bgColor = useColorModeValue('gray.50', 'gray.900')
  const cardBg = useColorModeValue('white', 'gray.800')

  useEffect(() => {
    fetchItems()
  }, [])

  const fetchItems = async () => {
    try {
      setLoading(true)
      const data = await apiService.getItems()
      setItems(data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch items. Make sure the backend is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateItem = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await apiService.createItem({
        name: newItemName,
        description: newItemDescription || null,
      })
      setNewItemName('')
      setNewItemDescription('')
      fetchItems()
    } catch (err) {
      setError('Failed to create item')
      console.error(err)
    }
  }

  const handleDeleteItem = async (id: number) => {
    try {
      await apiService.deleteItem(id)
      fetchItems()
    } catch (err) {
      setError('Failed to delete item')
      console.error(err)
    }
  }

  return (
    <Box minH="100vh" bg={bgColor} py={8}>
      <Container maxW="container.md">
        <VStack spacing={8} align="stretch">
          {/* Header with Dark Mode Toggle */}
          <HStack justify="space-between" align="center">
            <Box textAlign="center" flex={1}>
              <Heading size="2xl" mb={2}>
                Civitas Demo
              </Heading>
              <Text color="gray.500">
                FastAPI + PostgreSQL + React + Vite + Chakra UI
              </Text>
            </Box>
            <IconButton
              aria-label="Toggle dark mode"
              icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
              onClick={toggleColorMode}
              size="lg"
              variant="ghost"
            />
          </HStack>

          {/* Error Alert */}
          {error && (
            <Box bg="red.50" border="1px" borderColor="red.200" borderRadius="md" p={4}>
              <Text color="red.700">{error}</Text>
            </Box>
          )}

          {/* Create Item Form */}
          <Card bg={cardBg}>
            <CardBody>
              <Heading size="lg" mb={4}>
                Create New Item
              </Heading>
              <form onSubmit={handleCreateItem}>
                <VStack spacing={4}>
                  <Input
                    placeholder="Item name"
                    value={newItemName}
                    onChange={(e) => setNewItemName(e.target.value)}
                    required
                    size="lg"
                  />
                  <Input
                    placeholder="Description (optional)"
                    value={newItemDescription}
                    onChange={(e) => setNewItemDescription(e.target.value)}
                    size="lg"
                  />
                  <Button
                    type="submit"
                    colorScheme="blue"
                    size="lg"
                    width="full"
                  >
                    Create Item
                  </Button>
                </VStack>
              </form>
            </CardBody>
          </Card>

          {/* Items List */}
          <Card bg={cardBg}>
            <CardBody>
              <Heading size="lg" mb={4}>
                Items
              </Heading>
              {loading ? (
                <Box textAlign="center" py={8}>
                  <Spinner size="xl" color="blue.500" />
                </Box>
              ) : items.length === 0 ? (
                <Text color="gray.500" textAlign="center" py={8}>
                  No items yet. Create one above!
                </Text>
              ) : (
                <VStack spacing={4} align="stretch">
                  {items.map((item) => (
                    <Card key={item.id} variant="outline">
                      <CardBody>
                        <HStack justify="space-between" align="start">
                          <Box flex={1}>
                            <Heading size="md" mb={2}>
                              {item.name}
                            </Heading>
                            {item.description && (
                              <Text color="gray.600" mb={2}>
                                {item.description}
                              </Text>
                            )}
                            <Text fontSize="sm" color="gray.500">
                              Created: {new Date(item.created_at).toLocaleString()}
                            </Text>
                          </Box>
                          <IconButton
                            aria-label="Delete item"
                            icon={<DeleteIcon />}
                            colorScheme="red"
                            variant="ghost"
                            onClick={() => handleDeleteItem(item.id)}
                          />
                        </HStack>
                      </CardBody>
                    </Card>
                  ))}
                </VStack>
              )}
            </CardBody>
          </Card>
        </VStack>
      </Container>
    </Box>
  )
}

export default App
