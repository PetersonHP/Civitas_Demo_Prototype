import { useState, useEffect } from 'react'
import './App.css'
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
    <div className="App">
      <h1>Civitas Demo</h1>
      <p>FastAPI + PostgreSQL + React + Vite</p>

      {error && <div className="error">{error}</div>}

      <div className="create-item">
        <h2>Create New Item</h2>
        <form onSubmit={handleCreateItem}>
          <input
            type="text"
            placeholder="Item name"
            value={newItemName}
            onChange={(e) => setNewItemName(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Description (optional)"
            value={newItemDescription}
            onChange={(e) => setNewItemDescription(e.target.value)}
          />
          <button type="submit">Create Item</button>
        </form>
      </div>

      <div className="items-list">
        <h2>Items</h2>
        {loading ? (
          <p>Loading...</p>
        ) : items.length === 0 ? (
          <p>No items yet. Create one above!</p>
        ) : (
          <ul>
            {items.map((item) => (
              <li key={item.id}>
                <div>
                  <strong>{item.name}</strong>
                  {item.description && <p>{item.description}</p>}
                  <small>Created: {new Date(item.created_at).toLocaleString()}</small>
                </div>
                <button onClick={() => handleDeleteItem(item.id)}>Delete</button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

export default App
