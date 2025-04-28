import "./globals.css"
import Sidebar from "./components/Sidebar"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt">
      <body className="bg-gradient-to-br from-[#25539E] to-[#35373A] text-dark flex min-h-screen">
        <Sidebar />
        <main className="ml-20 md:ml-64 p-6 w-full">
          <div className="bg-white rounded-2xl shadow-md p-6">
            {children}
          </div>
        </main>
      </body>
    </html>
  )
}