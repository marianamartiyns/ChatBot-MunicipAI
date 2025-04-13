// frontend/app/sobre/page.tsx
export default function SobrePage() {
    return (
      <div className="space-y-6 max-w-3xl">
        <h1 className="text-3xl font-bold text-primary">ℹ️ Sobre o Aplicativo</h1>
  
        <p className="text-gray-700 leading-relaxed">
          Este aplicativo foi desenvolvido para facilitar o acesso a indicadores públicos de municípios e estados brasileiros.
          Através de um painel interativo e de um chatbot inteligente, qualquer cidadão pode consultar dados oficiais sobre demografia, educação, saúde, economia e outros temas importantes.
        </p>
  
        <p className="text-gray-700 leading-relaxed">
          As informações são coletadas automaticamente de fontes públicas confiáveis como o <strong>IBGE (SIDRA)</strong>,
          o <strong>Ministério da Saúde</strong> e o <strong>Ministério da Educação</strong>, garantindo dados sempre atualizados e transparentes.
        </p>
  
        <p className="text-gray-700 leading-relaxed">
          O projeto é mantido por uma equipe independente com foco em dados abertos, cidadania digital e acessibilidade à informação.
        </p>
  
        <div className="border-t pt-4 text-sm text-gray-500">
          © 2025 - Chatbot Municípios · Dados públicos, acessíveis e úteis.
        </div>
      </div>
    )
  }
  