# guard-raiLLM

**Uma skill de auditoria de segurança para devs e vibecoders.**

Por [Paulo Leal Taveira](https://github.com/paulinholt) · MIT · v0.1.0

Transforme “meu projeto está seguro?” em uma revisão com **evidências, prioridades, correções e testes**. O fluxo cobre aplicações, APIs, bancos, infraestrutura e integrações com IA, com atenção especial a rate-limit, isolamento entre usuários e exposição de `.env`.

[English guide](docs/README.en.md) · [Instalação](docs/installation.md) · [Pesquisa comparativa](docs/research.md) · [Skill](skills/guard-raillm/SKILL.md) · [Avaliação](evals/README.md)

## Comece aqui

```sh
git clone https://github.com/paulinholt/guard-raiLLM.git
cd guard-raiLLM
python scripts/install.py --dest ~/.agents/skills
```

Esse exemplo instala para descoberta local no Codex. Para Claude Code, use `--dest ~/.claude/skills`; para Kimi Code, veja os diretórios e diferenças de versão no [guia](docs/installation.md). Requer Python 3.10+ apenas para os auxiliares. A skill pode ser copiada manualmente.

No agente, peça:

```text
Use guard-raillm para uma auditoria full deste projeto.
Priorize rate-limit, autorização entre usuários, banco de dados e exposição de segredos.
Entregue evidências, correções propostas e o que não foi possível verificar.
```

## Cobertura

| Módulo | O que orienta verificar |
|---|---|
| Aplicação | Autenticação, sessões, permissões, BOLA/IDOR, injeções, XSS, CSRF, SSRF e uploads |
| Rate-limit | Abuso, contadores distribuídos, confiança em proxies, concorrência e limites de custo |
| Dados | SQL/NoSQL, RLS, Supabase, Firebase, isolamento entre tenants, storage e backups |
| Segredos | `.env`, histórico Git, bundles, logs, CI, chaves públicas versus privilegiadas e rotação |
| Infraestrutura | Dependências, containers, IAM, CI/CD, IaC, exposição de serviços e cadeia de fornecimento |
| IA e agentes | Prompt injection, RAG, MCP, permissões de ferramentas, memória e gastos |
| Operação | Webhooks, pagamentos, idempotência, privacidade, auditoria e recuperação |
| Especializações | Encaminhamento para mobile, código nativo, criptografia, contratos e sistemas embarcados |

## Modos e resultados

- `quick`: triagem de caminhos críticos, com lacunas explícitas.
- `full`: revisão de todos os domínios aplicáveis.
- `diff`: mudanças e controles afetados, comparados à revisão-base.
- `fix`: correções solicitadas com testes de regressão.
- `verify`: revisão de uma correção e de seus efeitos.

Cada achado registra severidade, confiança, localização, pré-condições, impacto, correção e verificação. Hipóteses ficam separadas de falhas confirmadas. Um checklist não executado nunca vira aprovação.

## Compatibilidade e limites

O pacote segue o formato aberto `SKILL.md`, com instruções em inglês e respostas no idioma do usuário. Há caminhos de instalação documentados para **Codex/GPT, Claude Code e Kimi Code**. Em chats sem carregador de skills, forneça o `SKILL.md` e as referências relevantes como contexto; isso não concede acesso automático ao repositório nem executa testes.

A v0.1.0 tem validação estrutural e testes dos auxiliares; **não há benchmark de eficácia ou execução ponta a ponta em todos os modelos**. A skill orienta a análise: não é scanner autônomo, WAF, monitor de ataques ou certificação. Segurança do ambiente de execução depende do agente e de suas permissões.

O inventário incluído funciona offline e não lê conteúdos. Scanners especializados são opcionais e seguem o [guia de ferramentas](skills/guard-raillm/references/tooling.md). Auditorias começam pela revisão do projeto autorizado; testes ativos exigem escopo compatível com sua autorização.

## Desenvolvimento

```sh
python -m unittest discover -s tests -v
python scripts/validate.py
python skills/guard-raillm/scripts/inventory.py .
python scripts/package.py
```

O pacote ZIP gerado em `dist/` contém a skill completa e a licença. Não inclui a pesquisa nem os testes de manutenção. O CI verifica o projeto em Linux e Windows.

Veja [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) e a [pesquisa com fontes](docs/research.md). Os projetos pesquisados mantêm suas autorias e licenças; não são dependências nem endossam este projeto.
