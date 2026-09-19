import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { MutationCache, QueryCache, QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createBrowserRouter, Navigate, RouterProvider } from 'react-router'
import { ApiError } from './shared/api'
import { goToLogin } from './shared/auth'
import { RequireLogin } from './shared/RequireLogin'
import { ProjectsPage } from './features/projects/List/ProjectsPage'
import { NewProjectPage } from './features/projects/Create/NewProjectPage'
import { ProjectDetailPage } from './features/projects/Detail/ProjectDetailPage'

import './index.css'

const router = createBrowserRouter(
  [
    {
      element: <RequireLogin />,
      children: [
        { path: '/', element: <ProjectsPage /> },
        { path: '/new', element: <NewProjectPage /> },
        { path: '/:id', element: <ProjectDetailPage /> },
        { path: '/*', element: <Navigate to="/" replace /> },
      ],
    },
  ],
  { basename: '/projects' }
)

// still 401 after http() tried a refresh → the session is gone, log in again
const onError = (error: Error) => {
  if (error instanceof ApiError && error.status === 401) goToLogin()
}

const queryClient = new QueryClient({
  queryCache: new QueryCache({ onError }),
  mutationCache: new MutationCache({ onError }),
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
)
