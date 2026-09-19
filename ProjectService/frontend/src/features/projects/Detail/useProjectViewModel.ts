import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router'
import { projectsApi } from '../model'

export function useProjectViewModel() {
    const { id = '' } = useParams()
    const navigate = useNavigate()
    const queryClient = useQueryClient()
    const [name, setName] = useState<string | null>(null) // null = not editing

    const project = useQuery({
        queryKey: ['project', id],
        queryFn: () => projectsApi.get(id),
        retry: false,
        // the scanner works in the background, so poll until it settles
        refetchInterval: (query) =>
            query.state.data?.project.status === 'scanning' ? 3000 : false,
    })

    const invalidate = () => {
        queryClient.invalidateQueries({ queryKey: ['project', id] })
        queryClient.invalidateQueries({ queryKey: ['projects'] })
    }

    const rename = useMutation({
        mutationFn: async () => {
            if (!name?.trim()) throw new Error('Name is required')
            return projectsApi.rename(id, name.trim())
        },
        onSuccess: () => {
            setName(null)
            invalidate()
        },
    })

    const remove = useMutation({
        mutationFn: () => projectsApi.remove(id),
        onSuccess: () => {
            invalidate()
            navigate('/', { replace: true })
        },
    })

    return {
        project: project.data?.project,
        details: project.data?.details ?? null,
        isLoading: project.isLoading,
        error: project.error?.message ?? rename.error?.message ?? remove.error?.message,

        editedName: name,
        startRename: () => setName(project.data?.project.name ?? ''),
        setName,
        cancelRename: () => setName(null),
        saveName: () => rename.mutate(),
        isSaving: rename.isPending,

        // deleting is not undoable, so confirm first
        remove: () => {
            if (window.confirm('Delete this project? This cannot be undone.')) remove.mutate()
        },
        isDeleting: remove.isPending,
    }
}
