import { Link } from 'react-router'
import { Button, Card, ErrorMessage, Field, FilePicker, Page, Progress } from '../../../shared/ui'
import { useNewProjectViewModel } from './useNewProjectViewModel'

export function NewProjectPage() {
    const vm = useNewProjectViewModel()

    return (
        <Page title="New project">
            <Card>
                <form onSubmit={vm.submit} className="grid max-w-md gap-4">
                    <ErrorMessage message={vm.error} />
                    <FilePicker file={vm.file} onChange={vm.setFile} />
                    <Field
                        label="Name"
                        autoFocus
                        maxLength={200}
                        value={vm.name}
                        onChange={(e) => vm.setName(e.target.value)}
                    />
                    {vm.isSubmitting && (
                        <div className="grid gap-1">
                            <Progress percent={vm.percent} />
                            <p className="text-sm text-zinc-500">
                                {vm.percent < 100 ? `Uploading ${vm.percent}%` : 'Checking the upload...'}
                            </p>
                        </div>
                    )}
                    <div className="flex items-center gap-4">
                        <Button disabled={vm.isSubmitting}>
                            {vm.isSubmitting ? 'Working...' : 'Create project'}
                        </Button>
                        <Link to="/" className="text-sm text-zinc-500 hover:text-zinc-900">
                            Cancel
                        </Link>
                    </div>
                </form>
            </Card>
        </Page>
    )
}
