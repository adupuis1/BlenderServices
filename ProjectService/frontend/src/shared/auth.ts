import { http, postJson, tokenStore } from './api'

// Login lives in the LoginService app (/auth/). Full page load, because it's a
// different app; ?next= brings the user back here after login.
export function goToLogin() {
    tokenStore.clear()
    const next = encodeURIComponent(window.location.pathname + window.location.search)
    window.location.assign(`/auth/login?next=${next}`)
}

export async function logout() {
    const refresh_token = tokenStore.refresh
    // log out locally even if the server call fails
    if (refresh_token) {
        await http('/api/v1/logout', postJson({ refresh_token }), false).catch(() => {})
    }
    tokenStore.clear()
    window.location.assign('/auth/login')
}
