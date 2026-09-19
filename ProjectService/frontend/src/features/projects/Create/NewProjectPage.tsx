import { Link } from 'react-router'
import { Button, Card, ErrorMessage, Field, Page } from '../../../shared/ui'
import { useNewProjectViewModel } from './useNewProjectViewModel'

export function NewProjectPage() {
    const vm = useNewProjectViewModel()

    return (
        <Page title="New project">
            <Card>
                <form onSubmit={vm.submit} className="grid max-w-sm gap-4">
                    <ErrorMessage message={vm.error} />
                    <Field
                        label="Name"
                        autoFocus
                        maxLength={200}
                        value={vm.name}
                        onChange={(e) => vm.setName(e.target.value)}
                    />
                    <div className="flex items-center gap-4">
                        <Button disabled={vm.isSubmitting}>
                            {vm.isSubmitting ? 'Creating...' : 'Create project'}
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
