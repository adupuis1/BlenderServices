import { Link } from 'react-router'
import { ButtonLink, Card, ErrorMessage, Page, StatusBadge } from '../../../shared/ui'
import { useProjectsViewModel } from './useProjectsViewModel'

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
                                        <StatusBadge status={p.status} />
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
