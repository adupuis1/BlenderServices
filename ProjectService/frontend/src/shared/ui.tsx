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

function formatSize(bytes: number) {
    if (bytes < 1024 * 1024) return `${Math.ceil(bytes / 1024)} KB`
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

// Clicking opens the OS file browser. The picked file stays in the browser's
// memory as a File object; nothing is sent anywhere until code uploads it.
export function FilePicker({ file, onChange }: { file: File | null; onChange: (file: File | null) => void }) {
    return (
        <label className="grid cursor-pointer gap-1 rounded-lg border-2 border-dashed border-zinc-300 p-6 text-center text-sm hover:border-zinc-900">
            <input
                type="file"
                accept=".blend"
                className="sr-only"
                onChange={(e) => onChange(e.target.files?.[0] ?? null)}
            />
            {file ? (
                <>
                    <span className="font-medium">{file.name}</span>
                    <span className="text-zinc-500">{formatSize(file.size)} · click to pick another</span>
                </>
            ) : (
                <>
                    <span className="font-medium">Choose a .blend file</span>
                    <span className="text-zinc-500">opens your computer's file browser</span>
                </>
            )}
        </label>
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

export function Progress({ percent }: { percent: number }) {
    return (
        <div className="h-2 overflow-hidden rounded-full bg-zinc-200">
            <div className="h-full bg-zinc-900 transition-[width]" style={{ width: `${percent}%` }} />
        </div>
    )
}

const statusStyle: Record<string, string> = {
    pending_upload: 'bg-zinc-100 text-zinc-700',
    scanning: 'bg-blue-50 text-blue-700',
    ready: 'bg-green-50 text-green-700',
    rejected: 'bg-red-50 text-red-700',
}

export function StatusBadge({ status }: { status: string }) {
    return (
        <span className={`rounded-full px-2 py-0.5 text-xs ${statusStyle[status] ?? statusStyle.pending_upload}`}>
            {status.replace('_', ' ')}
        </span>
    )
}
