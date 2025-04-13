// frontend/app/components/CardIndicador.tsx
import React from "react"

type Props = {
  titulo: string
  valor: string
  descricao?: string
}

export default function CardIndicador({ titulo, valor, descricao }: Props) {
  return (
    <div className="bg-light rounded-2xl shadow p-4 border border-gray-200 hover:shadow-md transition duration-300">
      <h3 className="text-sm text-gray-600">{titulo}</h3>
      <p className="text-2xl font-bold text-primary mt-1">{valor}</p>
      {descricao && <p className="text-xs text-gray-500 mt-2">{descricao}</p>}
    </div>
  )
}
