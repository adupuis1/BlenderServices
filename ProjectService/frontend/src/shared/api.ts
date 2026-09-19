// Same token store as the LoginService frontend. Both apps are served from one
// origin (the gateway), so they read and write the same localStorage keys.
export const tokenStore = {
    get access() { return localStorage.getItem('access_token') },
    get refresh() { return localStorage.getItem('refresh_token') },
    save(t: { access_token: string; refresh_token: string }) {
        localStorage.setItem('access_token', t.access_token)
        localStorage.setItem('refresh_token', t.refresh_token)
    },
    clear() {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
    },
}

// carries the HTTP status, so callers can tell "log in again" (401) from other errors
export class ApiError extends Error {
    status: number
    constructor(status: number, message: string) {
        super(message)
        this.status = status
    }
}

// single-flight: if several requests get 401 at once, they share ONE refresh call
// (two refreshes with the same token would trigger the backend's reuse detection and log you out)
let refreshing: Promise<boolean> | null = null

function refreshTokens(): Promise<boolean> {
    refreshing ??= (async () => {
        const refresh_token = tokenStore.refresh
        if (!refresh_token) return false
        const res = await fetch('/api/v1/login/refresh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token }),
        })
        if (!res.ok) {
            tokenStore.clear()
            return false
        }
        tokenStore.save(await res.json())
        return true
    })().finally(() => {
        refreshing = null
    })
    return refreshing
}

export async function http<T>(path: string, init: RequestInit = {}, auth = true): Promise<T> {
    const send = () => {
        const headers = new Headers(init.headers)
        if (auth && tokenStore.access) headers.set('Authorization', `Bearer ${tokenStore.access}`)
        return fetch(path, { ...init, headers })
    }

    let res = await send()
    if (auth && res.status === 401 && (await refreshTokens())) res = await send()

    if (!res.ok) {
        const body = await res.json().catch(() => null)
        throw new ApiError(
            res.status,
            typeof body?.detail === 'string' ? body.detail : 'Something went wrong',
        )
    }
    // 204 (DELETE) has no body to parse
    return res.status === 204 ? (undefined as T) : res.json()
}

// Presigned PUT straight to storage: the file never goes through the API.
// XHR rather than fetch, because it reports upload progress.
export function putFile(url: string, file: File, onProgress: (percent: number) => void) {
    return new Promise<void>((resolve, reject) => {
        const xhr = new XMLHttpRequest()
        xhr.open('PUT', url)
        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) onProgress(Math.round((e.loaded / e.total) * 100))
        }
        xhr.onload = () =>
            xhr.status >= 200 && xhr.status < 300
                ? resolve()
                : reject(new ApiError(xhr.status, `Upload failed (${xhr.status})`))
        // the browser hides the reason; almost always missing CORS on the storage
        xhr.onerror = () =>
            reject(new Error('Upload failed: could not reach storage (is CORS set on MinIO?)'))
        xhr.send(file)
    })
}

export const postJson = (body: unknown): RequestInit => ({
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
})
