import { useQuery } from '@tanstack/react-query'
import { projectsApi } from '../model'

export function useProjectsViewModel() {
    const projects = useQuery({
        queryKey: ['projects'],
        queryFn: projectsApi.list,
        retry: false,
        // keep the list moving while the scanner works through a project
        refetchInterval: (query) =>
            query.state.data?.some((p) => p.status === 'scanning') ? 5000 : false,
    })

    return {
        projects: projects.data ?? [],
        isLoading: projects.isLoading,
        error: projects.error?.message,
    }
}
