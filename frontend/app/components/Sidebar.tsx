"use client"

import Link from "next/link"
import { LayoutDashboard, MessageCircle, Info } from "lucide-react"

export default function Sidebar() {
  return (
    <aside className="bg-[#F9FAFB] text-black w-20 md:w-64 h-screen p-4 flex flex-col gap-4 fixed top-0 left-0">
      {/* Logo da empresa */}
      <img
        src="/Houer-1920w.png"
        alt="Logo"
        className="w-full h-auto mb-6 object-contain mx-auto"
      />

      <nav className="flex flex-col gap-6">
        <Link href="/painel" className="flex items-center gap-2 hover:text-blue-600">
          <LayoutDashboard /> <span className="hidden md:inline">Painel</span>
        </Link>
        <Link href="/chat" className="flex items-center gap-2 hover:text-blue-600">
          <MessageCircle /> <span className="hidden md:inline">Chatbot</span>
        </Link>
        <Link href="/sobre" className="flex items-center gap-2 hover:text-blue-600">
          <Info /> <span className="hidden md:inline">Sobre</span>
        </Link>
      </nav>
    </aside>
  )
}
