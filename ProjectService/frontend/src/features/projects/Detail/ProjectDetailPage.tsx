import { Link } from 'react-router'
import { Button, Card, ErrorMessage, Field, Page, StatusBadge } from '../../../shared/ui'
import type { ProjectDetails } from '../model'
import { useProjectViewModel } from './useProjectViewModel'

function Row({ label, value }: { label: string; value: string | number | null }) {
    if (value === null || value === '') return null
    return (
        <div className="flex justify-between gap-4 border-b border-zinc-100 py-2 last:border-0">
            <dt className="text-zinc-500">{label}</dt>
            <dd className="text-right font-medium">{value}</dd>
        </div>
    )
}

function ScanResults({ details }: { details: ProjectDetails }) {
    const size = details.file_size_bytes
    const frames =
        details.frame_start !== null && details.frame_end !== null
            ? `${details.frame_start} - ${details.frame_end}`
            : null
    const resolution =
        details.resolution_x !== null && details.resolution_y !== null
            ? `${details.resolution_x} x ${details.resolution_y}`
            : null

    return (
        <Card>
            <h2 className="mb-2 font-semibold">Scan results</h2>
            <dl className="text-sm">
                <Row label="Engine" value={details.engine} />
                <Row label="Samples" value={details.samples} />
                <Row label="Resolution" value={resolution} />
                <Row label="Frames" value={frames} />
                <Row label="Polygons" value={details.poly_count?.toLocaleString() ?? null} />
                <Row label="File size" value={size ? `${(size / 1024 / 1024).toFixed(1)} MB` : null} />
                <Row label="Add-ons" value={details.addons.join(', ')} />
                <Row label="Scanned" value={new Date(details.scanned_at).toLocaleString()} />
            </dl>
            {details.external_paths.length > 0 && (
                <p className="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">
                    {details.external_paths.length} external file(s) referenced. Pack resources into the
                    .blend, or renders will be missing them.
                </p>
            )}
        </Card>
    )
}

export function ProjectDetailPage() {
    const vm = useProjectViewModel()

    if (vm.isLoading) return <Page title="Project"><p className="text-zinc-500">Loading...</p></Page>
    if (!vm.project) {
        return (
            <Page title="Project">
                <Card>
                    <ErrorMessage message={vm.error ?? 'Project not found'} />
                    <Link to="/" className="mt-4 inline-block text-sm font-medium hover:underline">
                        ← Back to projects
                    </Link>
                </Card>
            </Page>
        )
    }

    const p = vm.project
    return (
        <Page title={p.name} actions={<StatusBadge status={p.status} />}>
            <div className="grid gap-4">
                <ErrorMessage message={vm.error} />

                <Card>
                    <dl className="text-sm">
                        <Row label="Created" value={new Date(p.created_at).toLocaleString()} />
                        <Row label="Blender" value={p.blender_series} />
                        <Row label="Rejected because" value={p.reject_reason} />
                    </dl>
                    {p.status === 'scanning' && (
                        <p className="mt-3 text-sm text-zinc-500">
                            Scanning. This page updates itself when it finishes.
                        </p>
                    )}
                    {p.status === 'pending_upload' && (
                        <p className="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">
                            No file was uploaded for this project. Delete it and create a new one:
                            re-uploading needs an endpoint that issues a fresh upload URL.
                        </p>
                    )}
                </Card>

                {vm.details && <ScanResults details={vm.details} />}

                <Card>
                    {vm.editedName === null ? (
                        <div className="flex items-center gap-4">
                            <Button onClick={vm.startRename}>Rename</Button>
                            <button
                                onClick={vm.remove}
                                disabled={vm.isDeleting}
                                className="text-sm font-medium text-red-700 hover:underline disabled:opacity-50"
                            >
                                {vm.isDeleting ? 'Deleting...' : 'Delete project'}
                            </button>
                            <Link to="/" className="ml-auto text-sm text-zinc-500 hover:text-zinc-900">
                                ← Back to projects
                            </Link>
                        </div>
                    ) : (
                        <div className="grid max-w-md gap-4">
                            <Field
                                label="Name"
                                autoFocus
                                maxLength={200}
                                value={vm.editedName}
                                onChange={(e) => vm.setName(e.target.value)}
                            />
                            <div className="flex items-center gap-4">
                                <Button onClick={vm.saveName} disabled={vm.isSaving}>
                                    {vm.isSaving ? 'Saving...' : 'Save'}
                                </Button>
                                <button
                                    onClick={vm.cancelRename}
                                    className="text-sm text-zinc-500 hover:text-zinc-900"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    )}
                </Card>
            </div>
        </Page>
    )
}
