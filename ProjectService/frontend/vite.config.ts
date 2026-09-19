import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
    base: "/projects/",
    plugins: [react(), tailwindcss()],
    // npm run dev: send login + API traffic to the gateway, so the dev server
    // is one origin (localhost:5173) and shares localStorage with /auth/
    server: {
        proxy: {
            "/api": "http://localhost:8088",
            "/auth": "http://localhost:8088",
        },
    },
})
