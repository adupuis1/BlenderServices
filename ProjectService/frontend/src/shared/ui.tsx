import type { ComponentProps, ReactNode } from 'react'
import { Link } from 'react-router'
import { logout } from './auth'

export function Page({ title, actions, children }: { title: string; actions?: ReactNode; children: ReactNode }) {
    return (
        <div className="min-h-screen bg-zinc-100">
            <header className="border-b border-zinc-200 bg-white">
                <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
                    <Link to="/" className="font-semibold">Blender Projects</Link>
                    <button onClick={logout} className="text-sm text-zinc-500 hover:text-zinc-900">
                        Log out
                    </button>
                </div>
            </header>
            <main className="mx-auto max-w-4xl p-4">
                <div className="mb-4 flex items-center justify-between gap-4">
                    <h1 className="text-2xl font-semibold">{title}</h1>
                    {actions}
                </div>
                {children}
            </main>
        </div>
    )
}

export function Card({ children }: { children: ReactNode }) {
    return <div className="rounded-2xl bg-white p-6 shadow-sm">{children}</div>
}

export function Field({ label, ...props }: { label: string } & ComponentProps<'input'>) {
    return (
        <label className="grid gap-1 text-sm font-medium">
            {label}
            <input
                {...props}
                className="rounded-lg border border-zinc-300 px-3 py-2 font-normal outline-none focus:border-zinc-900 focus:ring-2 focus:ring-zinc-900/10"
            />
        </label>
    )
}

export function Button({ className = '', ...props }: ComponentProps<'button'>) {
    return (
        <button
            {...props}
            className={`rounded-lg bg-zinc-900 px-3 py-2 font-medium text-white hover:bg-zinc-700 disabled:opacity-50 ${className}`}
        />
    )
}

// a Link that looks like a Button
export function ButtonLink(props: ComponentProps<typeof Link>) {
    return (
        <Link
            {...props}
            className="rounded-lg bg-zinc-900 px-3 py-2 text-sm font-medium text-white hover:bg-zinc-700"
        />
    )
}

export function ErrorMessage({ message }: { message?: string }) {
    if (!message) return null
    return (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {message}
        </p>
    )
}

// empty view for features that aren't built yet
export function NotBuiltYet({ title, what }: { title: string; what: string }) {
    return (
        <Page title={title}>
            <Card>
                <p className="text-zinc-500">Not built yet: {what}</p>
                <Link to="/" className="mt-4 inline-block text-sm font-medium hover:underline">
                    ← Back to projects
                </Link>
            </Card>
        </Page>
    )
}
