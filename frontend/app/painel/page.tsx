// frontend\app\painel\page.tsx

'use client'

import { useEffect, useState } from 'react'
import SelectComBusca from '../components/SelectComBusca'

type Local = { codigo: string, nome: string, sigla?: string }

export default function PainelPage() {
  const [tipo, setTipo] = useState<'municipio' | 'estado'>('municipio')
  const [listaEstados, setListaEstados] = useState<Local[]>([])
  const [listaMunicipios, setListaMunicipios] = useState<Local[]>([])
  const [selecionado, setSelecionado] = useState<Local | null>(null)
  const [dados, setDados] = useState<any | null>(null)
  const [erro, setErro] = useState('')

  useEffect(() => {
    const carregarListas = async () => {
      const [estRes, munRes] = await Promise.all([
        fetch('http://localhost:8000/lista-estados'),
        fetch('http://localhost:8000/lista-municipios'),
      ])
      setListaEstados(await estRes.json())
      setListaMunicipios(await munRes.json())
    }
    carregarListas()
  }, [])

  const buscarIndicadores = async () => {
    setErro('')
    setDados(null)
    if (!selecionado) {
      setErro('Selecione um local antes de buscar.')
      return
    }

    try {
      const res = await fetch(`http://localhost:8000/dados-${tipo}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ codigo: selecionado.codigo }),
      })

      if (!res.ok) throw new Error('Erro ao buscar dados')

      const json = await res.json()
      setDados(json)
    } catch (err) {
      console.error(err)
      setErro('Erro ao buscar dados do servidor.')
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-primary"> Indicadores Municipais e Estaduais</h1>

      <div className="flex flex-wrap items-end gap-4">
        <div>
          <label className="text-sm text-gray-600 mb-1 block">Tipo de local</label>
          <select
            value={tipo}
            onChange={(e) => setTipo(e.target.value as 'municipio' | 'estado')}
            className="border rounded-md px-4 py-2"
          >
            <option value="municipio">Município</option>
            <option value="estado">Estado</option>
          </select>
        </div>

        <SelectComBusca
          opcoes={tipo === 'municipio' ? listaMunicipios : listaEstados}
          onChange={(codigo) => {
            const lista = tipo === 'municipio' ? listaMunicipios : listaEstados
            const selecionadoObj = lista.find((l) => l.codigo === codigo) || null
            setSelecionado(selecionadoObj)
          }}
          label={`Selecione um ${tipo}`}
        />

        <button
          onClick={buscarIndicadores}
          className="bg-blue-900 text-white px-6 py-2 rounded-md hover:bg-blue-500 transition"
        >
          Buscar
        </button>
      </div>

      {erro && <p className="text-red-600 mt-4">{erro}</p>}

      {dados && (
        <>
          <div className="mt-6">
            <h2 className="text-lg font-semibold text-gray-700 border-b pb-1 mb-2">📊 Indicadores</h2>
            <div className="grid grid-cols-[repeat(auto-fit,minmax(260px,1fr))] gap-4">
              {Object.entries(dados).map(([chave, valor]) => {
                let texto = typeof valor === "string" ? valor : String(valor)
                let valorPrincipal = texto
                let ano = null

                const matchAno = texto.match(/\[(\d{4})\]/)
                if (matchAno) {
                  ano = matchAno[1]
                  valorPrincipal = texto.replace(/\s*\[\d{4}\]/, "")
                }

                const isLink = typeof valorPrincipal === "string" && valorPrincipal.startsWith("http")

                return (
                  <div key={chave} className="bg-gray-50 rounded-xl p-4 shadow-sm border">
                    <p className="text-sm text-gray-500 mb-1">{chave}</p>
                    <div className="flex items-center justify-between flex-wrap gap-2">
                      {isLink ? (
                        <a
                          href={valorPrincipal}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-700 underline hover:text-blue-900 break-words text-sm"
                        >
                          {valorPrincipal}
                        </a>
                      ) : (
                        <p className="text-2xl font-bold text-blue-800 break-words">
                          {valorPrincipal}
                        </p>
                      )}
                      {ano && (
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full flex items-center gap-1">
                          🗓️ {ano}
                        </span>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
