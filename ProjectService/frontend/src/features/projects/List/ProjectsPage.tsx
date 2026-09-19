import { Link } from 'react-router'
import { ButtonLink, Card, ErrorMessage, Page } from '../../../shared/ui'
import type { ProjectStatus } from '../model'
import { useProjectsViewModel } from './useProjectsViewModel'

const statusStyle: Record<ProjectStatus, string> = {
    pending_upload: 'bg-zinc-100 text-zinc-700',
    scanning: 'bg-blue-50 text-blue-700',
    ready: 'bg-green-50 text-green-700',
    rejected: 'bg-red-50 text-red-700',
}

export function ProjectsPage() {
    const vm = useProjectsViewModel()

    return (
        <Page title="Projects" actions={<ButtonLink to="/new">New project</ButtonLink>}>
            <ErrorMessage message={vm.error} />
            {vm.isLoading && <p className="text-zinc-500">Loading...</p>}

            {!vm.isLoading && !vm.error && vm.projects.length === 0 && (
                <Card>
                    <p className="text-zinc-500">No projects yet.</p>
                </Card>
            )}

            {vm.projects.length > 0 && (
                <div className="overflow-hidden rounded-2xl bg-white shadow-sm">
                    <table className="w-full text-left text-sm">
                        <thead className="border-b border-zinc-200 text-zinc-500">
                            <tr>
                                <th className="px-4 py-3 font-medium">Name</th>
                                <th className="px-4 py-3 font-medium">Status</th>
                                <th className="px-4 py-3 font-medium">Created</th>
                            </tr>
                        </thead>
                        <tbody>
                            {vm.projects.map((p) => (
                                <tr key={p.id} className="border-b border-zinc-100 last:border-0 hover:bg-zinc-50">
                                    <td className="px-4 py-3">
                                        <Link to={`/${p.id}`} className="font-medium hover:underline">
                                            {p.name}
                                        </Link>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`rounded-full px-2 py-0.5 text-xs ${statusStyle[p.status]}`}>
                                            {p.status.replace('_', ' ')}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-zinc-500">
                                        {new Date(p.created_at).toLocaleDateString()}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </Page>
    )
}
