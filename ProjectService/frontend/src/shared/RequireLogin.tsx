import { useEffect } from 'react'
import { Outlet } from 'react-router'
import { tokenStore } from './api'
import { goToLogin } from './auth'

// Wraps every page: no token → off to the login app. An expired token is fine
// here, http() refreshes it on the first 401.
export function RequireLogin() {
    const loggedIn = tokenStore.access !== null

    useEffect(() => {
        if (!loggedIn) goToLogin()
    }, [loggedIn])

    return loggedIn ? <Outlet /> : null
}
