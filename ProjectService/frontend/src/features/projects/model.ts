import { http, postJson } from '../../shared/api'

export type ProjectStatus = 'pending_upload' | 'scanning' | 'ready' | 'rejected'

// mirrors ProjectPublic in ProjectService/backend/app/models.py
export type Project = {
    id: string
    name: string
    status: ProjectStatus
    blender_series: string | null
    reject_reason: string | null
    created_at: string
}

export type CreatedProject = {
    project: Project
    upload_url: string // presigned PUT to MinIO, used by the upload view (not built yet)
}

export const projectsApi = {
    list: () => http<Project[]>('/api/v1/projects'),

    create: (name: string) => http<CreatedProject>('/api/v1/projects', postJson({ name })),
}
