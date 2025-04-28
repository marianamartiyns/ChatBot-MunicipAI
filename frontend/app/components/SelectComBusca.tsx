"use client"

import { useState, useEffect } from "react"

type Opcao = {
  codigo: string
  nome: string
  sigla?: string
}

interface SelectComBuscaProps {
  opcoes: Opcao[]
  onChange: (codigo: string) => void
  label: string
}

export default function SelectComBusca({ opcoes, onChange, label }: SelectComBuscaProps) {
  const [busca, setBusca] = useState("")
  const [aberto, setAberto] = useState(false)
  const [selecionado, setSelecionado] = useState<Opcao | null>(null)

  const opcoesFiltradas = opcoes.filter((opcao) =>
    opcao.nome.toLowerCase().includes(busca.toLowerCase()) ||
    (opcao.sigla && opcao.sigla.toLowerCase().includes(busca.toLowerCase()))
  )

  const selecionar = (codigo: string) => {
    const escolhido = opcoes.find((op) => op.codigo === codigo)
    if (escolhido) {
      setSelecionado(escolhido)
      setBusca(escolhido.nome) // Mostra o nome no campo
      onChange(codigo)
    }
    setAberto(false)
  }

  // Caso o usuário apague manualmente o conteúdo do input
  useEffect(() => {
    if (busca === "") {
      setSelecionado(null)
    }
  }, [busca])

  return (
    <div className="relative w-64">
      <label className="text-sm text-gray-600 mb-1 block">{label}</label>
      <input
        type="text"
        value={busca}
        onChange={(e) => setBusca(e.target.value)}
        onFocus={() => setAberto(true)}
        placeholder="Digite para buscar..."
        className="w-full border rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
      />
      {aberto && (
        <div className="absolute z-10 mt-1 w-full bg-white border rounded-md shadow-lg max-h-60 overflow-auto">
          {opcoesFiltradas.length > 0 ? (
            opcoesFiltradas.map((opcao) => (
              <div
                key={opcao.codigo}
                onClick={() => selecionar(opcao.codigo)}
                className="px-4 py-2 cursor-pointer hover:bg-blue-100 text-sm"
              >
                {opcao.nome} {opcao.sigla ? `(${opcao.sigla})` : ""}
              </div>
            ))
          ) : (
            <div className="px-4 py-2 text-gray-400 text-sm">Nenhuma opção encontrada</div>
          )}
        </div>
      )}
    </div>
  )
}