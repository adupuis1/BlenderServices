import { http, postJson, putFile } from '../../shared/api'

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

// mirrors ProjectDetails: what the scanner found
export type ProjectDetails = {
    engine: string | null
    samples: number | null
    resolution_x: number | null
    resolution_y: number | null
    frame_start: number | null
    frame_end: number | null
    poly_count: number | null
    file_size_bytes: number | null
    addons: string[]
    external_paths: { type: string; name: string; path: string }[]
    has_registered_scripts: boolean
    has_python_drivers: boolean
    freestyle_enabled: boolean
    scanned_at: string
}

export type CreatedProject = { project: Project; upload_url: string }

export const projectsApi = {
    list: () => http<Project[]>('/api/v1/projects'),

    get: (id: string) =>
        http<{ project: Project; details: ProjectDetails | null }>(`/api/v1/projects/${id}`),

    create: (name: string) => http<CreatedProject>('/api/v1/projects', postJson({ name })),

    rename: (id: string, name: string) =>
        http<Project>(`/api/v1/projects/${id}`, { ...postJson({ name }), method: 'PATCH' }),

    remove: (id: string) => http<void>(`/api/v1/projects/${id}`, { method: 'DELETE' }),

    // the API only checks the file is in storage; it never sees the bytes
    complete: (id: string) => http<Project>(`/api/v1/projects/${id}/complete`, { method: 'POST' }),
}

// create → PUT the file to storage → tell the API it's there (scanning)
export async function createWithUpload(
    name: string,
    file: File,
    onProgress: (percent: number) => void,
): Promise<Project> {
    const { project, upload_url } = await projectsApi.create(name)
    await putFile(upload_url, file, onProgress)
    return projectsApi.complete(project.id)
}
