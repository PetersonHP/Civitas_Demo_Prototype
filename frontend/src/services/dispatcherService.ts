import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface DispatchTicketResponse {
  status: string;
  priority: string;
  user_assignees: string[];
  crew_assignees: string[];
  labels: string[];
  comment: {
    comment_body: string;
  };
  justification: string;
}

/**
 * Dispatch a ticket using the AI dispatcher agent.
 *
 * This service calls the dispatcher API endpoint which uses an AI agent to:
 * - Assess ticket priority
 * - Find and assign appropriate crews based on location and issue type
 * - Assign relevant staff members
 * - Categorize with appropriate labels
 * - Generate a response comment for the citizen
 *
 * @param ticketId - UUID of the ticket to process
 * @returns Dispatcher recommendations
 */
export const dispatchTicket = async (
  ticketId: string
): Promise<DispatchTicketResponse> => {
  try {
    const response = await axios.post<DispatchTicketResponse>(
      `${API_BASE_URL}/api/dispatcher/${ticketId}/dispatch`
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail ||
        'Failed to dispatch ticket with AI agent'
      );
    }
    throw error;
  }
};
