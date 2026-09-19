import { useState, type SyntheticEvent } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router'
import { projectsApi } from '../model'

export function useNewProjectViewModel() {
    const navigate = useNavigate()
    const queryClient = useQueryClient()
    const [name, setName] = useState('')

    const create = useMutation({
        mutationFn: async () => {
            // same rule as ProjectCreate on the backend (1-200 chars)
            if (!name.trim()) throw new Error('Name is required')
            return projectsApi.create(name.trim())
        },
        onSuccess: ({ project }) => {
            queryClient.invalidateQueries({ queryKey: ['projects'] })
            navigate(`/${project.id}/upload`)
        },
    })

    return {
        name,
        setName,
        submit: (e: SyntheticEvent) => {
            e.preventDefault()
            create.mutate()
        },
        isSubmitting: create.isPending,
        error: create.error?.message,
    }
}
