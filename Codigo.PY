"""
Sistema avancado de triagem e gestao de chamados internos.

OBJETIVO:
Construir uma solucao computacional detalhada para classificar, priorizar,
monitorar e gerar insights sobre chamados de TI corporativa.

REQUISITOS DA ETAPA 6 (atendidos):
1) Variaveis:
   - dezenas de variaveis de estado e negocio (score, prioridade, status etc.)
2) Estruturas condicionais:
   - if / elif / else em regras de prioridade, SLA e validacao
3) Estruturas de repeticao:
   - while para menus e validacao
   - for para relatorios, filtros, simulacoes e agregacoes
4) Funcoes simples:
   - funcoes especializadas e pequenas para cada parte do fluxo

DIFERENCIAIS DO QUE FOI MOSTRADO EM AULA
- Arquitetura em camadas (modelo, regras, servico, repositorio, interface)
- Persistencia em JSON (historico fica salvo entre execucoes)
- Dashboard executivo com metricas de operacao
- Simulacao automatica de carga com dados realistas
- Filtro, busca, ordenacao e atualizacao de status
- Relatorio textual para copiar no PIM
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple


# ============================================================
# 1) CONFIGURACAO E REGRAS DE NEGOCIO
# ============================================================

DATA_FILE = Path("chamados_microsoft.json")

PONTOS_IMPACTO = {"baixo": 1, "medio": 3, "alto": 5}
PONTOS_URGENCIA = {"baixa": 1, "media": 3, "alta": 5}
PONTOS_TIPO = {"acesso": 1, "software": 2, "hardware": 2, "seguranca": 4, "rede": 3}

PRIORIDADE_ORDEM = {"Baixa": 1, "Media": 2, "Alta": 3, "Critica": 4}

SLA_POR_PRIORIDADE = {
    "Baixa": "72h",
    "Media": "24h",
    "Alta": "8h",
    "Critica": "1h",
}

STATUS_VALIDOS = ["aberto", "em_andamento", "resolvido", "cancelado"]

DESCRICOES_TIPO = {
    "acesso": "Problemas de login, MFA e permissoes",
    "software": "Erros em sistemas e aplicativos corporativos",
    "hardware": "Falhas em notebook, monitor, perifericos",
    "seguranca": "Risco de phishing, malware, vazamento",
    "rede": "Conectividade, VPN, latencia e indisponibilidade",
}


# ============================================================
# 2) MODELO DE DADOS
# ============================================================

@dataclass
class Chamado:
    """
    Modelo principal de chamado.
    Dataclass foi usada para deixar o codigo limpo, forte e legivel.
    """

    id: int
    titulo: str
    descricao: str
    area: str
    solicitante: str
    impacto: str
    urgencia: str
    tipo: str
    score: int
    prioridade: str
    sla: str
    status: str
    criado_em: str
    atualizado_em: str
    parecer: str


# ============================================================
# 3) FUNCOES UTILITARIAS
# ============================================================

def agora_iso() -> str:
    """Retorna data/hora atual em formato padrao para persistencia."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def normalizar_texto(texto: str) -> str:
    """Padroniza entradas para comparacao segura."""
    return texto.strip().lower()


def gerar_id(chamados: List[Chamado]) -> int:
    """Gera ID incremental unico para cada novo chamado."""
    if not chamados:
        return 1
    return max(c.id for c in chamados) + 1


def pedir_texto_obrigatorio(mensagem: str) -> str:
    """Solicita texto obrigatorio; repete ate valor valido."""
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("[ERRO] Campo obrigatorio. Digite um valor nao vazio.")


def pedir_opcao(mensagem: str, opcoes: List[str]) -> str:
    """Solicita opcao controlada com validacao por while + if."""
    while True:
        valor = normalizar_texto(input(mensagem))
        if valor in opcoes:
            return valor
        print(f"[ERRO] Opcao invalida. Escolha uma opcao em: {', '.join(opcoes)}")


def pedir_int_positivo(mensagem: str) -> int:
    """Solicita numero inteiro positivo com tratamento de excecao."""
    while True:
        try:
            numero = int(input(mensagem))
            if numero > 0:
                return numero
            print("[ERRO] Digite um numero maior que zero.")
        except ValueError:
            print("[ERRO] Digite apenas numeros inteiros.")


# ============================================================
# 4) MOTOR DE PRIORIZACAO (ALGORITMO CENTRAL)
# ============================================================

def calcular_score(impacto: str, urgencia: str, tipo: str) -> int:
    """
    ALGORITMO:
    score = pontos_impacto + pontos_urgencia + pontos_tipo
    """
    return PONTOS_IMPACTO[impacto] + PONTOS_URGENCIA[urgencia] + PONTOS_TIPO[tipo]


def classificar_prioridade(score: int) -> str:
    """
    Regras de classificacao por faixa de score.
    """
    if score >= 13:
        return "Critica"
    if score >= 9:
        return "Alta"
    if score >= 5:
        return "Media"
    return "Baixa"


def definir_parecer(score: int, tipo: str) -> str:
    """
    Gera parecer de negocio explicando o risco do chamado.
    """
    descricao_tipo = DESCRICOES_TIPO.get(tipo, "Incidente tecnico corporativo")
    if score >= 13:
        return f"Risco maximo. {descricao_tipo}. Necessita escalonamento imediato."
    if score >= 9:
        return f"Risco alto. {descricao_tipo}. Atendimento priorizado no turno atual."
    if score >= 5:
        return f"Risco moderado. {descricao_tipo}. Tratar dentro do SLA padrao."
    return f"Risco baixo. {descricao_tipo}. Tratar em fila de rotina."


def montar_chamado(
    chamados_existentes: List[Chamado],
    titulo: str,
    descricao: str,
    area: str,
    solicitante: str,
    impacto: str,
    urgencia: str,
    tipo: str,
) -> Chamado:
    """
    Fabrica um chamado completo aplicando todas as regras de negocio.
    """
    score = calcular_score(impacto, urgencia, tipo)
    prioridade = classificar_prioridade(score)
    sla = SLA_POR_PRIORIDADE[prioridade]
    momento = agora_iso()

    return Chamado(
        id=gerar_id(chamados_existentes),
        titulo=titulo,
        descricao=descricao,
        area=area,
        solicitante=solicitante,
        impacto=impacto,
        urgencia=urgencia,
        tipo=tipo,
        score=score,
        prioridade=prioridade,
        sla=sla,
        status="aberto",
        criado_em=momento,
        atualizado_em=momento,
        parecer=definir_parecer(score, tipo),
    )


# ============================================================
# 5) PERSISTENCIA (JSON)
# ============================================================

def salvar_chamados(chamados: List[Chamado], caminho: Path = DATA_FILE) -> None:
    """Salva lista de chamados em arquivo JSON."""
    dados = [asdict(chamado) for chamado in chamados]
    caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")


def criar_chamados_demo_iniciais() -> List[Chamado]:
    """
    Cria uma base padrao para demonstracao.
    Essa base e usada automaticamente na primeira execucao do sistema.
    """
    base: List[Chamado] = []

    exemplos = [
        {
            "titulo": "Falha de login no Teams - filial SP",
            "descricao": "Usuarios da filial nao conseguem autenticar no Teams.",
            "area": "Operacoes",
            "solicitante": "Ana",
            "impacto": "alto",
            "urgencia": "alta",
            "tipo": "acesso",
            "status": "em_andamento",
        },
        {
            "titulo": "Suspeita de phishing em email corporativo",
            "descricao": "Email suspeito recebido por diversos colaboradores.",
            "area": "Seguranca da Informacao",
            "solicitante": "Bruno",
            "impacto": "alto",
            "urgencia": "alta",
            "tipo": "seguranca",
            "status": "aberto",
        },
        {
            "titulo": "Instalacao de software de design",
            "descricao": "Solicitacao de instalacao para equipe de marketing.",
            "area": "Marketing",
            "solicitante": "Carla",
            "impacto": "baixo",
            "urgencia": "baixa",
            "tipo": "software",
            "status": "resolvido",
        },
        {
            "titulo": "Queda intermitente de VPN",
            "descricao": "Usuarios remotos relatam desconexao frequente da VPN.",
            "area": "Comercial",
            "solicitante": "Diego",
            "impacto": "medio",
            "urgencia": "alta",
            "tipo": "rede",
            "status": "aberto",
        },
        {
            "titulo": "Notebook nao inicializa",
            "descricao": "Equipamento sem boot apos atualizacao automatica.",
            "area": "Financeiro",
            "solicitante": "Erica",
            "impacto": "medio",
            "urgencia": "media",
            "tipo": "hardware",
            "status": "aberto",
        },
    ]

    for item in exemplos:
        chamado = montar_chamado(
            chamados_existentes=base,
            titulo=item["titulo"],
            descricao=item["descricao"],
            area=item["area"],
            solicitante=item["solicitante"],
            impacto=item["impacto"],
            urgencia=item["urgencia"],
            tipo=item["tipo"],
        )
        chamado.status = item["status"]
        chamado.atualizado_em = agora_iso()
        base.append(chamado)

    return base


def carregar_chamados(caminho: Path = DATA_FILE) -> List[Chamado]:
    """
    Carrega dados persistidos para continuar operacao entre execucoes.
    Se arquivo nao existir, retorna lista vazia.
    """
    if not caminho.exists():
        base_inicial = criar_chamados_demo_iniciais()
        salvar_chamados(base_inicial, caminho)
        print("[INFO] Base inicial de demonstracao criada automaticamente.")
        return base_inicial

    try:
        conteudo = caminho.read_text(encoding="utf-8").strip()
        if not conteudo:
            base_inicial = criar_chamados_demo_iniciais()
            salvar_chamados(base_inicial, caminho)
            print("[INFO] Arquivo vazio detectado. Base inicial de demonstracao recriada.")
            return base_inicial
        dados = json.loads(conteudo)
        return [Chamado(**item) for item in dados]
    except (json.JSONDecodeError, TypeError) as erro:
        print(f"[ALERTA] Falha ao carregar base de dados ({erro}). Usando lista vazia.")
        return []


# ============================================================
# 6) OPERACOES DE DOMINIO
# ============================================================

def cadastrar_manual(chamados: List[Chamado]) -> None:
    """
    Fluxo completo de cadastro manual de um chamado.
    """
    print("\n=== NOVO CHAMADO ===")
    titulo = pedir_texto_obrigatorio("Titulo: ")
    descricao = pedir_texto_obrigatorio("Descricao resumida: ")
    area = pedir_texto_obrigatorio("Area afetada (ex: Financeiro, RH, TI): ")
    solicitante = pedir_texto_obrigatorio("Solicitante: ")

    impacto = pedir_opcao("Impacto (baixo/medio/alto): ", list(PONTOS_IMPACTO.keys()))
    urgencia = pedir_opcao("Urgencia (baixa/media/alta): ", list(PONTOS_URGENCIA.keys()))
    tipo = pedir_opcao("Tipo (acesso/software/hardware/seguranca/rede): ", list(PONTOS_TIPO.keys()))

    novo = montar_chamado(
        chamados_existentes=chamados,
        titulo=titulo,
        descricao=descricao,
        area=area,
        solicitante=solicitante,
        impacto=impacto,
        urgencia=urgencia,
        tipo=tipo,
    )
    chamados.append(novo)
    salvar_chamados(chamados)

    print("\n[SUCESSO] Chamado criado!")
    exibir_chamado(novo)


def exibir_chamado(chamado: Chamado) -> None:
    """Exibe detalhes de um unico chamado de forma organizada."""
    print("-" * 80)
    print(f"ID           : {chamado.id}")
    print(f"Titulo       : {chamado.titulo}")
    print(f"Descricao    : {chamado.descricao}")
    print(f"Area         : {chamado.area}")
    print(f"Solicitante  : {chamado.solicitante}")
    print(f"Tipo         : {chamado.tipo}")
    print(f"Impacto      : {chamado.impacto}")
    print(f"Urgencia     : {chamado.urgencia}")
    print(f"Score        : {chamado.score}")
    print(f"Prioridade   : {chamado.prioridade}")
    print(f"SLA          : {chamado.sla}")
    print(f"Status       : {chamado.status}")
    print(f"Criado em    : {chamado.criado_em}")
    print(f"Atualizado em: {chamado.atualizado_em}")
    print(f"Parecer      : {chamado.parecer}")
    print("-" * 80)


def listar_chamados(chamados: List[Chamado]) -> None:
    """
    Lista chamados ordenando por prioridade e score.
    """
    if not chamados:
        print("[INFO] Nenhum chamado cadastrado.")
        return

    ordenados = sorted(
        chamados,
        key=lambda c: (PRIORIDADE_ORDEM[c.prioridade], c.score, c.id),
        reverse=True,
    )

    print("\n=== LISTAGEM COMPLETA (ordem de criticidade) ===")
    for chamado in ordenados:
        print(
            f"ID {chamado.id:03d} | {chamado.prioridade:<8} | Score {chamado.score:<2} | "
            f"Status {chamado.status:<12} | Tipo {chamado.tipo:<10} | {chamado.titulo}"
        )


def buscar_por_id(chamados: List[Chamado], id_chamado: int) -> Chamado | None:
    """Busca chamado por id. Retorna None se nao encontrar."""
    for chamado in chamados:
        if chamado.id == id_chamado:
            return chamado
    return None


def atualizar_status(chamados: List[Chamado]) -> None:
    """
    Atualiza status operacional do chamado.
    Ex.: aberto -> em_andamento -> resolvido.
    """
    if not chamados:
        print("[INFO] Nao ha chamados para atualizar.")
        return

    id_chamado = pedir_int_positivo("Digite o ID do chamado para atualizar status: ")
    chamado = buscar_por_id(chamados, id_chamado)
    if not chamado:
        print("[ERRO] ID nao encontrado.")
        return

    print(f"Status atual: {chamado.status}")
    novo_status = pedir_opcao(
        "Novo status (aberto/em_andamento/resolvido/cancelado): ",
        STATUS_VALIDOS,
    )
    chamado.status = novo_status
    chamado.atualizado_em = agora_iso()
    salvar_chamados(chamados)
    print("[SUCESSO] Status atualizado.")
    exibir_chamado(chamado)


def filtrar_chamados(chamados: List[Chamado]) -> None:
    """
    Permite filtro rapido por prioridade ou tipo.
    """
    if not chamados:
        print("[INFO] Nao ha chamados cadastrados.")
        return

    print("\n=== FILTROS ===")
    print("1 - Por prioridade")
    print("2 - Por tipo")
    opcao = pedir_opcao("Escolha (1/2): ", ["1", "2"])

    if opcao == "1":
        prioridade = pedir_opcao("Prioridade (Baixa/Media/Alta/Critica): ", ["baixa", "media", "alta", "critica"]).capitalize()
        filtrados = [c for c in chamados if c.prioridade == prioridade]
    else:
        tipo = pedir_opcao("Tipo (acesso/software/hardware/seguranca/rede): ", list(PONTOS_TIPO.keys()))
        filtrados = [c for c in chamados if c.tipo == tipo]

    if not filtrados:
        print("[INFO] Nenhum chamado encontrado para o filtro informado.")
        return

    for c in filtrados:
        print(f"ID {c.id:03d} | {c.prioridade:<8} | {c.status:<12} | {c.tipo:<10} | {c.titulo}")


# ============================================================
# 7) DASHBOARD ANALITICO
# ============================================================

def contar_por_campo(chamados: List[Chamado], campo: str, universo: List[str]) -> Dict[str, int]:
    """Conta frequencia por qualquer campo textual do chamado."""
    resultado = {item: 0 for item in universo}
    for chamado in chamados:
        valor = getattr(chamado, campo, "")
        if valor in resultado:
            resultado[valor] += 1
    return resultado


def calcular_kpis(chamados: List[Chamado]) -> Dict[str, float]:
    """
    Calcula indicadores-chave:
    - total de chamados
    - percentual critico
    - backlog aberto (nao resolvido/cancelado)
    - score medio
    """
    total = len(chamados)
    if total == 0:
        return {
            "total": 0,
            "pct_critico": 0.0,
            "backlog_aberto": 0,
            "score_medio": 0.0,
        }

    criticos = 0
    backlog = 0
    soma_score = 0

    for c in chamados:
        soma_score += c.score
        if c.prioridade == "Critica":
            criticos += 1
        if c.status in ("aberto", "em_andamento"):
            backlog += 1

    return {
        "total": total,
        "pct_critico": (criticos / total) * 100,
        "backlog_aberto": backlog,
        "score_medio": soma_score / total,
    }


def exibir_dashboard(chamados: List[Chamado]) -> None:
    """Mostra visao executiva com metricas para tomada de decisao."""
    print("\n=== DASHBOARD EXECUTIVO ===")
    if not chamados:
        print("[INFO] Sem dados para analise.")
        return

    kpis = calcular_kpis(chamados)
    por_prioridade = contar_por_campo(chamados, "prioridade", ["Baixa", "Media", "Alta", "Critica"])
    por_status = contar_por_campo(chamados, "status", STATUS_VALIDOS)
    por_tipo = contar_por_campo(chamados, "tipo", list(PONTOS_TIPO.keys()))

    tipo_mais = max(por_tipo, key=por_tipo.get)
    prioridade_mais = max(por_prioridade, key=por_prioridade.get)

    print("-" * 80)
    print(f"Total de chamados....................: {kpis['total']}")
    print(f"Percentual de chamados criticos......: {kpis['pct_critico']:.2f}%")
    print(f"Backlog aberto.......................: {kpis['backlog_aberto']}")
    print(f"Score medio da base..................: {kpis['score_medio']:.2f}")
    print(f"Tipo mais frequente..................: {tipo_mais}")
    print(f"Prioridade predominante..............: {prioridade_mais}")
    print("-" * 80)
    print("Distribuicao por prioridade:")
    for chave, valor in por_prioridade.items():
        print(f"  - {chave:<8}: {valor}")
    print("Distribuicao por status:")
    for chave, valor in por_status.items():
        print(f"  - {chave:<12}: {valor}")
    print("Distribuicao por tipo:")
    for chave, valor in por_tipo.items():
        print(f"  - {chave:<10}: {valor}")
    print("-" * 80)


# ============================================================
# 8) SIMULADOR DE CARGA (PARA DEMONSTRACAO)
# ============================================================

def gerar_chamado_aleatorio(chamados: List[Chamado], indice: int) -> Chamado:
    """
    Gera chamados sintenticos para testes e apresentacao.
    """
    titulos = [
        "Falha de login no Teams",
        "VPN instavel em horario comercial",
        "Possivel phishing em email executivo",
        "Notebook sem inicializar",
        "Erro no sistema de ponto",
        "Latencia alta no SharePoint",
        "Acesso negado no Power BI",
        "Atualizacao critica de seguranca pendente",
    ]
    areas = ["Financeiro", "RH", "Juridico", "Operacoes", "Comercial", "TI"]
    pessoas = ["Ana", "Bruno", "Carla", "Diego", "Erica", "Felipe", "Giovana", "Heitor"]

    impacto = random.choice(list(PONTOS_IMPACTO.keys()))
    urgencia = random.choice(list(PONTOS_URGENCIA.keys()))
    tipo = random.choice(list(PONTOS_TIPO.keys()))

    titulo = f"{random.choice(titulos)} [{indice}]"
    descricao = f"Registro automatico para teste de capacidade ({indice})."
    area = random.choice(areas)
    solicitante = random.choice(pessoas)

    chamado = montar_chamado(
        chamados_existentes=chamados,
        titulo=titulo,
        descricao=descricao,
        area=area,
        solicitante=solicitante,
        impacto=impacto,
        urgencia=urgencia,
        tipo=tipo,
    )

    # Probabilidade de alguns chamados ja estarem em andamento/resolvidos.
    sorteio = random.random()
    if sorteio > 0.80:
        chamado.status = "resolvido"
    elif sorteio > 0.60:
        chamado.status = "em_andamento"
    return chamado


def simular_carga(chamados: List[Chamado]) -> None:
    """
    Permite gerar diversos chamados em lote para testes estatisticos.
    """
    quantidade = pedir_int_positivo("Quantos chamados aleatorios deseja gerar? ")
    for i in range(1, quantidade + 1):
        chamados.append(gerar_chamado_aleatorio(chamados, i))
    salvar_chamados(chamados)
    print(f"[SUCESSO] {quantidade} chamados aleatorios gerados com sucesso.")


# ============================================================
# 9) RELATORIO FINAL PARA O PIM
# ============================================================

def montar_relatorio_textual(chamados: List[Chamado]) -> str:
    """
    Cria texto detalhado para voce copiar no trabalho.
    """
    kpis = calcular_kpis(chamados)
    por_prioridade = contar_por_campo(chamados, "prioridade", ["Baixa", "Media", "Alta", "Critica"])
    por_tipo = contar_por_campo(chamados, "tipo", list(PONTOS_TIPO.keys()))

    tipo_mais = max(por_tipo, key=por_tipo.get) if chamados else "nenhum"

    linhas = []
    linhas.append("RELATORIO TECNICO - ETAPA 6")
    linhas.append("Problema: alta demanda de chamados e risco de priorizacao inadequada.")
    linhas.append("Algoritmo: score = impacto + urgencia + tipo; prioridade por faixas.")
    linhas.append("Implementacao: Python com funcoes, condicionais, repeticao e persistencia JSON.")
    linhas.append(f"Total de chamados processados: {kpis['total']}")
    linhas.append(f"Percentual critico: {kpis['pct_critico']:.2f}%")
    linhas.append(f"Backlog aberto: {kpis['backlog_aberto']}")
    linhas.append(f"Score medio: {kpis['score_medio']:.2f}")
    linhas.append(f"Tipo mais frequente: {tipo_mais}")
    linhas.append("Distribuicao por prioridade:")
    for p, v in por_prioridade.items():
        linhas.append(f"  - {p}: {v}")
    linhas.append("Conclusao: o algoritmo padroniza a triagem e acelera resposta a incidentes criticos.")
    return "\n".join(linhas)


def exibir_relatorio_textual(chamados: List[Chamado]) -> None:
    """Mostra relatorio consolidado no terminal."""
    print("\n" + "=" * 80)
    print(montar_relatorio_textual(chamados))
    print("=" * 80)


# ============================================================
# 10) INTERFACE DE MENU
# ============================================================

def exibir_menu() -> str:
    """Menu principal do sistema."""
    print("\n=== MENU PRINCIPAL ===")
    print("1 - Cadastrar chamado manual")
    print("2 - Listar chamados")
    print("3 - Atualizar status de chamado")
    print("4 - Filtrar chamados")
    print("5 - Exibir dashboard executivo")
    print("6 - Simular carga de chamados")
    print("7 - Exibir relatorio textual para o PIM")
    print("0 - Sair")
    return pedir_opcao("Escolha (0-7): ", ["0", "1", "2", "3", "4", "5", "6", "7"])


def main() -> None:
    """
    Orquestrador geral do sistema.
    """
    print("=" * 80)
    print("MICROSOFT - SISTEMA AVANCADO DE PRIORIZACAO DE CHAMADOS (PIM)")
    print("=" * 80)

    chamados = carregar_chamados()
    print(f"[INFO] Base carregada com {len(chamados)} chamado(s).")

    while True:
        opcao = exibir_menu()

        if opcao == "1":
            cadastrar_manual(chamados)
        elif opcao == "2":
            listar_chamados(chamados)
        elif opcao == "3":
            atualizar_status(chamados)
        elif opcao == "4":
            filtrar_chamados(chamados)
        elif opcao == "5":
            exibir_dashboard(chamados)
        elif opcao == "6":
            simular_carga(chamados)
        elif opcao == "7":
            exibir_relatorio_textual(chamados)
        else:
            salvar_chamados(chamados)
            print("Encerrando sistema. Dados salvos com sucesso.")
            break


if __name__ == "__main__":
    main()