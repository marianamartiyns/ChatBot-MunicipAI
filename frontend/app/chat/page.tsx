"use client"

import { useState, useEffect, useRef } from "react"
import { UserCircleIcon, CommandLineIcon } from "@heroicons/react/24/solid"
import ReactMarkdown from "react-markdown"

type Mensagem = {
  autor: "user" | "bot"
  texto: string
}

export default function ChatPage() {
  const [mensagem, setMensagem] = useState("")
  const [historico, setHistorico] = useState<Mensagem[]>([])
  const [carregando, setCarregando] = useState(false)
  const chatRef = useRef<HTMLDivElement>(null)

  // Carrega a mensagem inicial
  useEffect(() => {
    const carregarMensagemInicial = async () => {
      const resposta = await fetch("http://localhost:8000/mensagem-inicial")
      const data = await resposta.json()
      const msgInicial: Mensagem = { autor: "bot", texto: data.mensagem }
      setHistorico([msgInicial])
    }
    carregarMensagemInicial()
  }, [])

  // Função para detectar se a pergunta é sobre a empresa Houer
  const ehPerguntaHouer = (texto: string) => {
    const textoLower = texto.toLowerCase()
    const termosEmpresa = [
      "houer", "empresa houer", "grupo houer", "missão", "valores", "visão",
      "propósito", "cultura", "ética", "compliance", "houer engenharia",
      "houer concessões", "houer tecnologia", "contato houer", "escritório houer"
    ]
    return termosEmpresa.some((termo) => textoLower.includes(termo))
  }  

  // Envio da pergunta com roteamento condicional
  const enviarMensagem = async () => {
    if (!mensagem.trim()) return
    const novaPergunta: Mensagem = { autor: "user", texto: mensagem }
    setHistorico((prev) => [...prev, novaPergunta])
    setMensagem("")
    setCarregando(true)
  
    try {
      const endpoint = ehPerguntaHouer(novaPergunta.texto)
        ? "http://localhost:8000/dados-houer"
        : "http://localhost:8000/responder"
  
      console.log("🔍 Enviando para:", endpoint)
  
      const resposta = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto: novaPergunta.texto }),
      })
  
      const data = await resposta.json()
      const respostaBot: Mensagem = { autor: "bot", texto: data.resposta }
      setHistorico((prev) => [...prev, respostaBot])
    } catch (e) {
      setHistorico((prev) => [...prev, { autor: "bot", texto: "Erro ao obter resposta." }])
    }
  
    setCarregando(false)
  }
  
  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: "smooth" })
  }, [historico, carregando])

  return (
    <div className=" bg-gray-50 flex items-center justify-center overflow-hidden">
      <div className="max-w-4xl h-full flex flex-col p-6">
        <h1 className="text-3xl font-bold text-center text-primary mb-4">
          Chatbot de Indicadores
        </h1>

        {/* Área de mensagens */}
        <div
          ref={chatRef}
          className="flex-1 bg-white border border-gray-200 rounded-2xl p-4 overflow-y-auto shadow-sm flex flex-col space-y-4"
        >
          {historico.map((msg, i) => (
            <div
              key={i}
              className={`flex items-start gap-3 max-w-[80%] ${
                msg.autor === "user" ? "self-end flex-row-reverse" : "self-start"
              }`}
            >
              <div className="flex-shrink-0">
                {msg.autor === "user" ? (
                  <UserCircleIcon className="w-8 h-8 text-blue-900" />
                ) : (
                  <CommandLineIcon className="w-8 h-8 text-gray-600" />
                )}
              </div>
              <div
                className={`p-3 rounded-xl text-sm transition-all duration-300 ${
                  msg.autor === "user"
                    ? "bg-primary text-white"
                    : "bg-gray-100 text-gray-800 prose prose-sm max-w-none"
                }`}
              >
                {msg.autor === "bot" ? (
                  <ReactMarkdown>{msg.texto}</ReactMarkdown>
                ) : (
                  <span>{msg.texto}</span>
                )}
              </div>
            </div>
          ))}
          {carregando && (
            <p className="text-gray-400 text-sm italic animate-pulse">Digitando...</p>
          )}
        </div>

        {/* Input */}
        <div className="flex gap-2 mt-4">
          <input
            type="text"
            value={mensagem}
            onChange={(e) => setMensagem(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && enviarMensagem()}
            placeholder="Digite sua pergunta..."
            className="flex-1 border border-gray-300 rounded-xl px-4 py-2 shadow-sm transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <button
            onClick={enviarMensagem}
            disabled={carregando}
            className={`px-4 py-2 rounded-xl transition-all duration-300 ${
              carregando ? "bg-gray-300 cursor-not-allowed" : "bg-primary text-white hover:scale-105 hover:bg-blue-900"
            }`}
          >
            {carregando ? "Enviando..." : "Enviar"}
          </button>
        </div>
      </div>
    </div>
  )
}