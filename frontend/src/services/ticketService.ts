import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ============================================================================
// Enums matching backend
// ============================================================================

export enum TicketOrigin {
  PHONE = 'phone',
  WEB_FORM = 'web form',
  TEXT = 'text',
}

export enum TicketStatus {
  AWAITING_RESPONSE = 'awaiting response',
  RESPONSE_IN_PROGRESS = 'response in progress',
  RESOLVED = 'resolved',
}

export enum TicketPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
}

// ============================================================================
// Type definitions
// ============================================================================

export interface LocationCoordinates {
  lat: number
  lng: number
}

export interface Label {
  label_id: string
  label_name: string
  label_description: string | null
  color_hex: string
  meta_data: Record<string, any>
  time_created: string
  time_updated: string | null
  created_by: string | null
}

export interface CivitasUser {
  user_id: string
  firstname: string
  lastname: string
  email: string | null
  phone_number: string | null
  status: string
  time_created: string
  time_updated: string | null
  time_last_login: string | null
  google_id: string | null
  google_email: string | null
  google_avatar_url: string | null
  meta_data: Record<string, any>
}

export interface SupportCrew {
  team_id: string
  team_name: string
  description: string | null
  crew_type: string
  status: string
  location_coordinates: LocationCoordinates | null
  meta_data: Record<string, any>
  time_created: string
  time_edited: string | null
}

export interface Ticket {
  ticket_id: string
  ticket_subject: string
  ticket_body: string
  origin: TicketOrigin
  status: TicketStatus
  priority: TicketPriority
  time_created: string
  time_updated: string | null
  reporter_id: string | null
  location_coordinates: LocationCoordinates | null
  meta_data: Record<string, any>
}

export interface TicketWithRelations extends Ticket {
  user_assignees: CivitasUser[]
  crew_assignees: SupportCrew[]
  reporter: CivitasUser | null
  labels: Label[]
}

export interface TicketCreate {
  ticket_subject: string
  ticket_body: string
  origin: TicketOrigin
  status?: TicketStatus
  priority?: TicketPriority
  reporter_id?: string | null
  user_assignee_ids?: string[]
  crew_assignee_ids?: string[]
  label_ids?: string[]
  location_coordinates?: LocationCoordinates | null
  meta_data?: Record<string, any>
}

export interface TicketUpdate {
  ticket_subject?: string
  ticket_body?: string
  origin?: TicketOrigin
  status?: TicketStatus
  priority?: TicketPriority
  reporter_id?: string | null
  user_assignee_ids?: string[]
  crew_assignee_ids?: string[]
  label_ids?: string[]
  location_coordinates?: LocationCoordinates | null
  meta_data?: Record<string, any>
}

export interface TicketComment {
  comment_id: string
  comment_body: string
  time_created: string
  is_edited: boolean
  time_edited: string | null
  commenter: string | null
  ticket_id: string
}

export interface TicketCommentWithUser extends TicketComment {
  commenter_user: CivitasUser | null
}

export interface TicketCommentCreate {
  comment_body: string
  ticket_id: string
  commenter: string
}

export interface TicketCommentUpdate {
  comment_body?: string
}

export interface TicketStatusUpdate {
  status: TicketStatus
}

export interface AssignUserRequest {
  user_ids: string[]
}

export interface AssignCrewRequest {
  crew_ids: string[]
}

export interface ManageLabelsRequest {
  label_ids: string[]
}

// ============================================================================
// Ticket API Service
// ============================================================================

export const ticketService = {
  // ============================================================================
  // Core Ticket CRUD
  // ============================================================================

  /**
   * Get paginated list of tickets with relations
   */
  getTickets: async (params?: {
    skip?: number
    limit?: number
    status?: TicketStatus
    priority?: TicketPriority
  }): Promise<TicketWithRelations[]> => {
    const response = await api.get<TicketWithRelations[]>('/api/tickets/', { params })
    return response.data
  },

  /**
   * Get a specific ticket by ID with all relations
   */
  getTicket: async (ticketId: string): Promise<TicketWithRelations> => {
    const response = await api.get<TicketWithRelations>(`/api/tickets/${ticketId}`)
    return response.data
  },

  /**
   * Create a new ticket
   */
  createTicket: async (ticket: TicketCreate): Promise<Ticket> => {
    const response = await api.post<Ticket>('/api/tickets/', ticket)
    return response.data
  },

  /**
   * Update a ticket
   */
  updateTicket: async (ticketId: string, ticket: TicketUpdate): Promise<Ticket> => {
    const response = await api.patch<Ticket>(`/api/tickets/${ticketId}`, ticket)
    return response.data
  },

  /**
   * Update only the status of a ticket
   */
  updateTicketStatus: async (ticketId: string, status: TicketStatus): Promise<Ticket> => {
    const response = await api.patch<Ticket>(`/api/tickets/${ticketId}/status`, { status })
    return response.data
  },

  /**
   * Delete a ticket
   */
  deleteTicket: async (ticketId: string): Promise<void> => {
    await api.delete(`/api/tickets/${ticketId}`)
  },

  // ============================================================================
  // Ticket Assignment Operations
  // ============================================================================

  /**
   * Assign users to a ticket (replaces existing)
   */
  assignUsers: async (ticketId: string, userIds: string[]): Promise<Ticket> => {
    const response = await api.post<Ticket>(`/api/tickets/${ticketId}/assign-users`, {
      user_ids: userIds,
    })
    return response.data
  },

  /**
   * Assign crews to a ticket (replaces existing)
   */
  assignCrews: async (ticketId: string, crewIds: string[]): Promise<Ticket> => {
    const response = await api.post<Ticket>(`/api/tickets/${ticketId}/assign-crews`, {
      crew_ids: crewIds,
    })
    return response.data
  },

  /**
   * Remove a user assignee from a ticket
   */
  unassignUser: async (ticketId: string, userId: string): Promise<Ticket> => {
    const response = await api.delete<Ticket>(`/api/tickets/${ticketId}/unassign-user/${userId}`)
    return response.data
  },

  /**
   * Remove a crew assignee from a ticket
   */
  unassignCrew: async (ticketId: string, crewId: string): Promise<Ticket> => {
    const response = await api.delete<Ticket>(`/api/tickets/${ticketId}/unassign-crew/${crewId}`)
    return response.data
  },

  // ============================================================================
  // Ticket Comments
  // ============================================================================

  /**
   * Get all comments for a ticket
   */
  getComments: async (ticketId: string): Promise<TicketCommentWithUser[]> => {
    const response = await api.get<TicketCommentWithUser[]>(`/api/tickets/${ticketId}/comments`)
    return response.data
  },

  /**
   * Create a new comment on a ticket
   */
  createComment: async (ticketId: string, comment: TicketCommentCreate): Promise<TicketCommentWithUser> => {
    const response = await api.post<TicketCommentWithUser>(`/api/tickets/${ticketId}/comments`, comment)
    return response.data
  },

  /**
   * Update a ticket comment
   */
  updateComment: async (commentId: string, comment: TicketCommentUpdate): Promise<TicketCommentWithUser> => {
    const response = await api.patch<TicketCommentWithUser>(`/api/tickets/comments/${commentId}`, comment)
    return response.data
  },

  /**
   * Delete a ticket comment
   */
  deleteComment: async (commentId: string): Promise<void> => {
    await api.delete(`/api/tickets/comments/${commentId}`)
  },

  // ============================================================================
  // Ticket Labels
  // ============================================================================

  /**
   * Set labels on a ticket (replaces existing)
   */
  setLabels: async (ticketId: string, labelIds: string[]): Promise<Ticket> => {
    const response = await api.post<Ticket>(`/api/tickets/${ticketId}/labels`, {
      label_ids: labelIds,
    })
    return response.data
  },

  /**
   * Remove a label from a ticket
   */
  removeLabel: async (ticketId: string, labelId: string): Promise<Ticket> => {
    const response = await api.delete<Ticket>(`/api/tickets/${ticketId}/labels/${labelId}`)
    return response.data
  },
}
