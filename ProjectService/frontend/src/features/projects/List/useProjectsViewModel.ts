import { useQuery } from '@tanstack/react-query'
import { projectsApi } from '../model'

export function useProjectsViewModel() {
    const projects = useQuery({
        queryKey: ['projects'],
        queryFn: projectsApi.list,
        retry: false,
    })

    return {
        projects: projects.data ?? [],
        isLoading: projects.isLoading,
        error: projects.error?.message,
    }
}
