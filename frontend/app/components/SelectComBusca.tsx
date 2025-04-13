// app/components/SelectComBusca.tsx
"use client"

import { useState } from "react"
import { Combobox } from "@headlessui/react"

type Opcao = {
  codigo: string
  nome: string
}

type Props = {
  opcoes: Opcao[]
  onChange: (codigo: string) => void
  label?: string
}

export default function SelectComBusca({ opcoes, onChange, label }: Props) {
  const [query, setQuery] = useState("")
  const [selecionado, setSelecionado] = useState<Opcao | null>(null)

  const filtradas =
    query === ""
      ? opcoes
      : opcoes.filter((o) =>
          o.nome.toLowerCase().includes(query.toLowerCase())
        )

  return (
    <div className="w-80">
      {label && <label className="text-sm text-gray-600 mb-1 block">{label}</label>}
      <Combobox value={selecionado} onChange={(e) => {
        setSelecionado(e)
        if (e) onChange(e.codigo)
      }}>
        <div className="relative">
          <Combobox.Input
            onChange={(e) => setQuery(e.target.value)}
            className="w-full border rounded-md px-4 py-2"
            displayValue={(o: Opcao) => o?.nome || ""}
            placeholder="Digite para buscar"
          />
          <Combobox.Options className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 overflow-auto rounded-md border">
            {filtradas.length === 0 ? (
              <div className="p-2 text-sm text-gray-500">Nenhuma opção encontrada</div>
            ) : (
              filtradas.map((opcao) => (
                <Combobox.Option
                  key={opcao.codigo}
                  value={opcao}
                  className={({ active }) =>
                    `cursor-pointer px-4 py-2 text-sm ${
                      active ? "bg-blue-100" : ""
                    }`
                  }
                >
                  {opcao.nome}
                </Combobox.Option>
              ))
            )}
          </Combobox.Options>
        </div>
      </Combobox>
    </div>
  )
}
