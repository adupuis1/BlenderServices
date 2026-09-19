import { useState, type SyntheticEvent } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router'
import { createWithUpload } from '../model'

export function useNewProjectViewModel() {
    const navigate = useNavigate()
    const queryClient = useQueryClient()
    const [name, setName] = useState('')
    const [file, setFile] = useState<File | null>(null)
    const [percent, setPercent] = useState(0)

    const create = useMutation({
        mutationFn: async () => {
            // same rules as ProjectCreate on the backend (1-200 chars)
            if (!name.trim()) throw new Error('Name is required')
            if (!file) throw new Error('Pick a .blend file')
            if (!file.name.toLowerCase().endsWith('.blend')) throw new Error('That is not a .blend file')
            setPercent(0)
            return createWithUpload(name.trim(), file, setPercent)
        },
        onSuccess: (project) => {
            queryClient.invalidateQueries({ queryKey: ['projects'] })
            navigate(`/${project.id}`)
        },
    })

    return {
        name,
        setName,
        file,
        setFile: (picked: File | null) => {
            setFile(picked)
            // default the project name to the file name, like most upload forms
            if (picked && !name) setName(picked.name.replace(/\.blend$/i, ''))
        },
        percent,
        submit: (e: SyntheticEvent) => {
            e.preventDefault()
            create.mutate()
        },
        isSubmitting: create.isPending,
        error: create.error?.message,
    }
}
