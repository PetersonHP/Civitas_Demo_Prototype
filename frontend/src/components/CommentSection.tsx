import { useState, useEffect, useMemo, useCallback } from 'react'
import {
  Box,
  VStack,
  Text,
  Divider,
  Spinner,
  Button,
  useColorModeValue,
  Card,
  CardBody,
  HStack,
} from '@chakra-ui/react'
import SimpleMDE from 'react-simplemde-editor'
import ReactMarkdown from 'react-markdown'
import 'easymde/dist/easymde.min.css'
import {
  ticketService,
  TicketCommentWithUser,
  TicketCommentCreate,
} from '../services/ticketService'

interface CommentSectionProps {
  ticketId: string
  userId: string // The user creating comments
}

const CommentCard = ({ comment }: { comment: TicketCommentWithUser }) => {
  const cardBg = useColorModeValue('white', 'gray.700')
  const borderColor = useColorModeValue('gray.200', 'gray.600')

  const commenterName = comment.commenter_user
    ? `${comment.commenter_user.firstname} ${comment.commenter_user.lastname}`
    : 'Anonymous'

  return (
    <Card bg={cardBg} borderWidth="1px" borderColor={borderColor} size="sm">
      <CardBody>
        <VStack align="stretch" spacing={2}>
          <HStack justify="space-between">
            <Text fontWeight="bold" fontSize="sm">
              {commenterName}
            </Text>
            <Text fontSize="xs" color="gray.500">
              {new Date(comment.time_created).toLocaleDateString()} at{' '}
              {new Date(comment.time_created).toLocaleTimeString()}
            </Text>
          </HStack>
          <Box fontSize="sm">
            <ReactMarkdown>{comment.comment_body}</ReactMarkdown>
          </Box>
          {comment.is_edited && (
            <Text fontSize="xs" color="gray.500" fontStyle="italic">
              Edited
            </Text>
          )}
        </VStack>
      </CardBody>
    </Card>
  )
}

export const CommentSection = ({ ticketId, userId }: CommentSectionProps) => {
  const [comments, setComments] = useState<TicketCommentWithUser[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [commentBody, setCommentBody] = useState('')

  const sectionBg = useColorModeValue('gray.50', 'gray.800')
  const editorBg = useColorModeValue('white', 'gray.700')
  const editorTextColor = useColorModeValue('#000000', '#e2e8f0')
  const editorBorderColor = useColorModeValue('#e2e8f0', '#4a5568')
  const editorButtonHover = useColorModeValue('#e2e8f0', '#4a5568')

  // Fetch comments
  const fetchComments = useCallback(async () => {
    try {
      setLoading(true)
      const fetchedComments = await ticketService.getComments(ticketId)
      setComments(fetchedComments)
      setError(null)
    } catch (err) {
      setError('Failed to load comments')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [ticketId])

  useEffect(() => {
    fetchComments()
  }, [fetchComments])

  // Handle comment submission
  const handleSubmitComment = async () => {
    if (!commentBody.trim()) {
      return
    }

    try {
      setSubmitting(true)
      const newCommentData: TicketCommentCreate = {
        comment_body: commentBody,
        ticket_id: ticketId,
        commenter: userId,
      }

      await ticketService.createComment(ticketId, newCommentData)

      // Clear the editor and refresh comments
      setCommentBody('')
      await fetchComments()
    } catch (err) {
      setError('Failed to create comment')
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  // Configure SimpleMDE options
  const editorOptions = useMemo(() => {
    return {
      spellChecker: false,
      placeholder: 'Write a comment (Markdown supported)...',
      status: false,
      toolbar: [
        'bold',
        'italic',
        'heading',
        '|',
        'quote',
        'unordered-list',
        'ordered-list',
        '|',
        'link',
        'image',
        '|',
        'preview',
        'guide',
      ] as any,
      minHeight: '150px',
    } as any
  }, [])

  return (
    <Box bg={sectionBg} p={4} borderRadius="md">
      <VStack align="stretch" spacing={4}>
        {/* Comments header */}
        <Text fontSize="lg" fontWeight="bold">
          Comments
        </Text>

        <Divider />

        {/* Comments list */}
        <Box maxH="400px" overflowY="auto">
          {loading ? (
            <Spinner size="md" />
          ) : error && comments.length === 0 ? (
            <Text color="red.500">{error}</Text>
          ) : comments.length === 0 ? (
            <Text color="gray.500" fontSize="sm">
              No comments yet.
            </Text>
          ) : (
            <VStack align="stretch" spacing={3}>
              {comments.map((comment) => (
                <CommentCard key={comment.comment_id} comment={comment} />
              ))}
            </VStack>
          )}
        </Box>

        <Divider />

        {/* Comment editor */}
        <VStack align="stretch" spacing={2}>
          <Text fontSize="md" fontWeight="semibold">
            Add a comment
          </Text>
          <Box
            sx={{
              '& .EasyMDEContainer': {
                backgroundColor: editorBg,
              },
              '& .CodeMirror': {
                backgroundColor: editorBg,
                color: editorTextColor,
                borderColor: editorBorderColor,
              },
              '& .CodeMirror-cursor': {
                borderLeftColor: editorTextColor,
              },
              '& .editor-toolbar': {
                backgroundColor: editorBg,
                borderColor: editorBorderColor,
              },
              '& .editor-toolbar button': {
                color: editorTextColor,
              },
              '& .editor-toolbar button:hover': {
                backgroundColor: editorButtonHover,
              },
              '& .editor-preview': {
                backgroundColor: editorBg,
                color: editorTextColor,
              },
            }}
          >
            <SimpleMDE
              value={commentBody}
              onChange={setCommentBody}
              options={editorOptions}
            />
          </Box>
          <Button
            colorScheme="blue"
            size="sm"
            onClick={handleSubmitComment}
            isLoading={submitting}
            isDisabled={!commentBody.trim()}
            alignSelf="flex-end"
          >
            Submit Comment
          </Button>
        </VStack>
      </VStack>
    </Box>
  )
}
