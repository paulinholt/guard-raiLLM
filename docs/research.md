# Skills de segurança no GitHub e o desenho do guard-raiLLM

## Síntese

O ecossistema oferece componentes úteis, mas distribuídos entre auditoria especializada, revisão de mudanças, boas práticas de banco e inspeção de extensões de agentes. A oportunidade do guard-raiLLM é organizar uma revisão transversal para quem desenvolve aplicações com assistência de modelos: sair de uma preocupação como “vazou minha `.env`?” e chegar a um achado rastreável, uma medida de contenção e um teste que confirme a correção.

Essa é uma decisão de produto, não uma afirmação de superioridade sobre as alternativas. A amostra consultada não permite concluir que inexista outra skill com cobertura semelhante. Também não permite comparar precisão de detecção: documentação de capacidades não equivale a benchmark. A proposta é um ponto de entrada acessível, com referências carregadas conforme o projeto e integração opcional com ferramentas estabelecidas.

## Escopo e método

Consulta realizada em 12 de setembro de 2026. Foram pesquisados repositórios públicos do GitHub, examinadas páginas dos projetos e arquivos de skills selecionados, e confrontadas as propostas com documentação primária de plataformas e controles. O levantamento distingue uma skill instalável de um framework, uma GitHub Action e um scanner. Não usa estrelas como medida de segurança ou manutenção.

A seleção considera relevância para auditoria de aplicações, evidência pública do fluxo, complementaridade, portabilidade e implicações de instalação/licenciamento. Não foram executados scripts dos projetos pesquisados nem realizadas auditorias independentes desses projetos. As revisões abaixo foram obtidas pela API do GitHub para permitir reencontrar o estado consultado; páginas de documentação externas são mutáveis.

| Projeto | Revisão consultada | Licença indicada no repositório |
|---|---|---|
| Trail of Bits skills | `321ccfe628eca0d314b0ee4eaffcdd8a05639aaf` | CC-BY-SA-4.0 |
| obra/superpowers | `b36e0829c6d0140e93cfef2ca599b1b07d4a7797` | MIT |
| anthropics/claude-code-security-review | `0c6a49f1fa56a1d472575da86a94dbc1edb78eda` | MIT |
| supabase/agent-skills | `8331f910845103c08d51f6ca1d86ebb7d1f745e3` | MIT |
| dkleptsov/skill-security-review | `d19fd5eff9762bada5ab2f18b0417f7e8d3f4fef` | Apache-2.0 |
| openai/skills | `49f948faa9258a0c61caceaf225e179651397431` | Verificar por skill; metadado global não identificado |

As licenças descrevem os projetos consultados, não uma autorização para copiar indiscriminadamente. O guard-raiLLM mantém implementação e redação próprias e cita as referências. Reutilização futura de arquivos exige preservar as condições aplicáveis, especialmente atribuição e compartilhamento sob licença compatível quando exigidos.

## Panorama comparativo

| Projeto | Natureza e contribuição | Limite para o objetivo deste projeto |
|---|---|---|
| Trail of Bits | Coleção especializada em pesquisa, análise de código, variantes e ferramentas | Exige selecionar e combinar especialidades conforme o alvo |
| OpenAI skills | Skills de boas práticas, threat modeling e ownership | O escopo de cada skill é específico; não implica auditoria universal |
| Supabase agent-skills | Orientação de PostgreSQL, incluindo segurança e RLS | Não cobre sozinho aplicação, identidade, pagamentos e infraestrutura completa |
| Anthropic security review | Action para revisão semântica de mudanças | Integração de CI e dependência de provedor; superfície de prompt injection reconhecida |
| skill-security-review | Inspeção estática de skills antes de confiar/instalar | Avalia a extensão do agente, não toda a aplicação auditada |
| Superpowers | Metodologia de desenvolvimento com skills compostas | Organização do trabalho não substitui controles de segurança específicos |

### Trail of Bits

A coleção reúne auditoria diferencial, construção de contexto, análise estática, busca de variantes e especializações. O arquivo de `differential-review` exige evidência e explicitação de cobertura, e encaminha procedimentos detalhados para arquivos de apoio. Essa modularidade é relevante para revisões que ultrapassam uma única lista de vulnerabilidades. A licença indicada é CC-BY-SA-4.0. [Repositório](https://github.com/trailofbits/skills), [skill examinada na revisão consultada](https://github.com/trailofbits/skills/blob/321ccfe628eca0d314b0ee4eaffcdd8a05639aaf/plugins/differential-review/skills/differential-review/SKILL.md).

Decisão para o guard-raiLLM: adotar um fluxo próprio orientado a evidência e carregar módulos conforme a superfície encontrada. Não transformar tamanho do repositório ou ausência de testes em substitutos automáticos da avaliação de impacto. Uma mudança pequena pode exigir análise profunda; uma recomendação genérica ainda não é um achado confirmado.

### Skills de segurança do catálogo OpenAI

Foram identificadas `security-best-practices`, `security-threat-model` e `security-ownership-map`. A primeira delimita linguagens suportadas e fornece orientação por framework; a segunda trata ativos, fronteiras e caminhos de abuso. São referências úteis para diferenciar orientação de implementação de um modelo de ameaças. [Boas práticas](https://github.com/openai/skills/blob/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/security-best-practices/SKILL.md), [threat model](https://github.com/openai/skills/blob/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/security-threat-model/SKILL.md).

Decisão: usar um inventário de atores, operações e dados para direcionar a auditoria, mantendo limites de linguagem e ferramentas explícitos. O pacote não depende dessas skills nem presume que estejam instaladas. Uma arquitetura sem acesso ao ambiente de produção só permite conclusões condicionais sobre essa implantação.

### Supabase agent-skills

A skill `supabase-postgres-best-practices` organiza referências de PostgreSQL, incluindo desempenho, conexões, schema, concorrência e segurança/RLS. É um exemplo de conhecimento especializado mantido perto da plataforma. O próprio escopo inclui mais que performance, mas não equivale a uma revisão completa do produto que usa o banco. [Skill examinada](https://github.com/supabase/agent-skills/blob/8331f910845103c08d51f6ca1d86ebb7d1f745e3/skills/supabase-postgres-best-practices/SKILL.md).

Decisão: avaliar políticas junto com o papel efetivo da conexão, funções privilegiadas, API e storage. O teste decisivo deve representar dois usuários e dois tenants, com operações permitidas e proibidas. Revisar somente SELECT ou somente o cliente deixa caminhos relevantes sem evidência.

### Anthropic Claude Code Security Review

O projeto oferece uma GitHub Action para analisar mudanças e publicar resultados em pull requests. A documentação informa que a action não está endurecida contra prompt injection e recomenda cuidado com contribuições externas. Essa limitação é especialmente relevante quando o material analisado pode conter instruções adversariais e o job possui credenciais. [Projeto e considerações de segurança](https://github.com/anthropics/claude-code-security-review#security-considerations).

Decisão: não incluir um agente com credenciais de provedor no CI inicial. Os workflows do guard-raiLLM executam testes determinísticos dos próprios auxiliares. A futura automação de auditorias de terceiros precisará de desenho separado de permissões, isolamento, privacidade e custo.

### skill-security-review

O projeto de Denis Kleptsov inspeciona skills estaticamente, incluindo saídas de rede, execução de processos, acesso a credenciais, código dinâmico, instalação e instruções maliciosas. Declara não executar a skill auditada e considera links que saem da árvore. Essa classe de revisão protege a cadeia de ferramentas usada para desenvolver e auditar. [Repositório](https://github.com/dkleptsov/skill-security-review).

Decisão: separar segurança da aplicação de segurança do agente. O guard-raiLLM inclui ambas como superfícies, mas não se apresenta como sandbox. O inventário auxiliar evita ler conteúdos e seguir links; ele serve para descoberta de arquivos e não herda as capacidades do scanner desse projeto.

### Superpowers

Superpowers organiza desenvolvimento por skills, com planejamento, testes e revisão. Sua contribuição é metodológica: decompor trabalho e verificar resultados. Não deve ser tratado como catálogo suficiente de controles de segurança ou requisito universal de instalação. [Repositório](https://github.com/obra/superpowers).

Decisão: manter o guard-raiLLM independente. Equipes podem combiná-lo com seu método de desenvolvimento existente. A auditoria deve preservar o escopo autorizado e produzir evidências úteis mesmo sem ferramentas de delegação ou plugins adicionais.

## Fundamentos de cobertura

O ASVS fornece uma base de requisitos verificáveis para aplicações. É mais útil para estruturar avaliação de controles que uma coleção informal de palavras-chave. O guard-raiLLM usa essa orientação como referência temática, sem declarar cobertura integral, nível ASVS atingido ou certificação. [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/).

O API Security Top 10 de 2023 destaca classes como autorização em objetos/propriedades/funções, consumo irrestrito de recursos, abuso de fluxos de negócio, SSRF e inventário de APIs. Isso justifica conferir operações e identidades, além de entradas malformadas. [OWASP API Security](https://owasp.org/API-Security/editions/2023/en/0x11-t10/).

As orientações de GenAI acrescentam riscos próprios da combinação entre conteúdo não confiável, modelos e ferramentas. A consequência arquitetural adotada é exigir controle de acesso fora do modelo e reconhecer limites de instruções textuais. [OWASP GenAI](https://genai.owasp.org/llm-top-10/).

### Rate-limit como controle de recursos

Uma verificação útil começa por identificar o recurso protegido: CPU, conexões, consultas, banda, tentativas de autenticação ou chamadas pagas. O parecer deve registrar qual identidade acumula o consumo e em que camada o limite é aplicado. Essa decomposição evita concluir que qualquer middleware de throttling resolve abuso.

Para o projeto, os casos de aceitação incluem múltiplas instâncias compartilhando orçamento, headers de proxy que não alterem arbitrariamente identidade, operações caras com peso adequado e falhas do armazenamento do contador. Limites de custo precisam considerar chamadas paralelas e trabalho enfileirado. O valor numérico deve vir do produto e de seu perfil de uso, não de uma constante genérica.

A orientação de DoS da OWASP reforça a necessidade de analisar recursos e camadas diferentes; limites de aplicação não substituem proteção de rede. Por isso, uma revisão de fonte não afirma resistência a DDoS volumétrico. [OWASP DoS](https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html).

### Banco e isolamento

Documentação de RLS precisa ser lida junto com o papel efetivo da conexão e caminhos privilegiados. No Supabase, políticas e credenciais de serviço têm comportamentos diferentes; no Firebase, clientes e SDKs administrativos não dependem dos mesmos controles. [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security), [Firebase Rules](https://firebase.google.com/docs/rules/basics).

O requisito próprio do guard-raiLLM é registrar a matriz de permissões e testar a fronteira com dados sintéticos. Uma identificação pública de objeto não constitui autorização, e tornar o identificador imprevisível não elimina uma falha de controle de acesso. Para storage, a mesma análise acompanha a geração de URLs assinadas e a propriedade do objeto.

### Segredos e exposição

A gestão de segredos abrange criação, armazenamento, distribuição, uso e revogação. A resposta a uma exposição precisa cuidar do ciclo de vida da credencial, não apenas do arquivo. [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html).

Na implementação proposta, a mera existência de `.env` não é uma vulnerabilidade. Devem ser distinguidos um arquivo local normal, um arquivo versionado, uma variável incorporada ao bundle e uma credencial privilegiada acessível externamente. Evidência deve mostrar a trajetória de exposição sem reproduzir o valor. A avaliação também não deve validar tokens reais contra provedores: isso amplia o risco sem ser necessário para identificar o defeito.

## Ferramentas complementares

Gitleaks atende à busca de candidatos a segredos; Semgrep e CodeQL à análise de código; Trivy à inspeção de vulnerabilidades/configuração em diferentes artefatos; OSV-Scanner à relação entre dependências e advisories; ZAP a testes HTTP. São ferramentas diferentes de uma skill e exigem registro do escopo e de suas limitações. [Gitleaks](https://github.com/gitleaks/gitleaks), [Semgrep](https://semgrep.dev/docs/), [CodeQL](https://codeql.github.com/docs/), [Trivy](https://github.com/aquasecurity/trivy), [OSV-Scanner](https://github.com/google/osv-scanner), [ZAP](https://www.zaproxy.org/docs/).

O guard-raiLLM não instala todas automaticamente. Um comando que falhou não pode produzir um resultado “sem achados”. Banco de advisories desatualizado, linguagem não suportada ou diretório excluído devem aparecer no relatório. Ferramentas de análise dinâmica também geram tráfego; “baseline” não significa ausência de efeitos.

## Portabilidade

O padrão Agent Skills define um diretório com `SKILL.md` e metadados de nome/descrição, com recursos adicionais. Essa organização permite distribuir um núcleo textual comum e referências relativas. [Especificação](https://agentskills.io/specification).

Codex documenta descoberta local em `.agents/skills`; Claude Code documenta `.claude/skills`; Kimi Code documenta skills e sua invocação. A compatibilidade do pacote é documental e estrutural: suporte ao mesmo formato não prova que diferentes modelos seguirão o fluxo com a mesma precisão. [Codex](https://learn.chatgpt.com/docs/build-skills), [Claude Code](https://code.claude.com/docs/en/skills), [Kimi Code](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html).

Em chats sem carregador ou filesystem, o uso é por instruções e arquivos fornecidos. O relatório precisa declarar essa limitação. Nenhum guia deve sugerir que o simples nome GPT, Claude ou Kimi concede acesso a um repositório ou capacidade de rodar testes.

## Arquitetura entregue e critérios de qualidade

A v0.1.0 usa um ponto de entrada curto, oito domínios de referência, orientação de ferramentas, contrato de relatório, um inventário de nomes de arquivos e um instalador sem sobrescrita. O CI verifica integridade do pacote e comportamento dos auxiliares, com ações fixadas por revisão e permissões mínimas. A documentação do GitHub fundamenta essa escolha de endurecimento do workflow. [GitHub secure use](https://docs.github.com/en/actions/reference/security/secure-use).

O diferencial pretendido é operacional: tornar claros achados, incertezas e próximos passos. Cada domínio precisa terminar com evidência ou lacuna registrada; cada correção precisa preservar um uso legítimo além de negar o caso indevido. Severidade e confiança são dimensões separadas. Uma hipótese grave não deve ser disfarçada como reprodução confirmada.

Os cenários de avaliação incluem falso positivo de chave pública, tentativa de exfiltração por instrução em arquivo, scanner indisponível, limitação distribuída e autorização entre tenants. Eles estabelecem comportamento esperado para futuras execuções. Os testes de Python não medem a qualidade do raciocínio dos modelos; não há resultado quantitativo de recall, precisão ou resistência a prompt injection nesta release.

## Limitações e evolução

A pesquisa é uma amostra dirigida, não um censo do GitHub. Capacidade e manutenção podem mudar após a revisão registrada. Um arquivo bem escrito não prova que uma skill detecta falhas em produção; um scanner sem resultados também não prova ausência de vulnerabilidades. As recomendações do projeto devem ser revistas quando surgirem casos reais, mudanças de plataforma ou regressões demonstradas.

Próximas avaliações úteis são executar os mesmos cenários em cada host, registrar versão/modelo/permissões, comparar achados com um conjunto independente de resultados esperados e repetir contra versões corrigidas. Domínios especializados, como criptografia nova, sistemas embarcados e contratos, exigem evidência e ferramentas próprias. A ambição é amplitude organizada com limites honestos, não a promessa impossível de cobrir toda a segurança com um único prompt.

## Fontes

Todas as fontes abaixo foram consultadas em 12/09/2026; projetos e skills específicos têm revisões registradas acima. As datas de atualização das páginas de documentação não são uniformes.

1. Trail of Bits. [Skills](https://github.com/trailofbits/skills) — auditoria e módulos especializados.
2. OpenAI. [Skills catalog](https://github.com/openai/skills) — boas práticas e modelagem de ameaças.
3. Supabase. [Agent skills](https://github.com/supabase/agent-skills) — PostgreSQL e RLS.
4. Anthropic. [Claude Code Security Review](https://github.com/anthropics/claude-code-security-review) — revisão de PRs e limitações.
5. Denis Kleptsov. [skill-security-review](https://github.com/dkleptsov/skill-security-review) — inspeção estática de skills.
6. obra. [Superpowers](https://github.com/obra/superpowers) — metodologia de desenvolvimento.
7. Agent Skills. [Specification](https://agentskills.io/specification) — formato interoperável.
8. OWASP. [ASVS](https://owasp.org/www-project-application-security-verification-standard/) — verificação de aplicações.
9. OWASP. [API Security Top 10, edição 2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) — riscos de APIs.
10. OWASP. [GenAI risks](https://genai.owasp.org/llm-top-10/) — riscos de sistemas com modelos.
11. OWASP. [Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html), [DoS](https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html), [Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html), [SSRF](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) — controles temáticos.
12. Supabase. [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security) — semântica de políticas.
13. Google Firebase. [Basic security rules](https://firebase.google.com/docs/rules/basics) — controles de acesso.
14. GitHub. [Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use) — segurança de workflows.
15. OpenAI. [Build skills](https://learn.chatgpt.com/docs/build-skills) — descoberta no Codex.
16. Anthropic. [Claude Code skills](https://code.claude.com/docs/en/skills) — instalação e invocação.
17. Moonshot AI. [Kimi Code skills](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html) — instalação e invocação.
18. Mantenedores das ferramentas. [Gitleaks](https://github.com/gitleaks/gitleaks), [Semgrep](https://semgrep.dev/docs/), [CodeQL](https://codeql.github.com/docs/), [Trivy](https://github.com/aquasecurity/trivy), [OSV-Scanner](https://github.com/google/osv-scanner), [ZAP](https://www.zaproxy.org/docs/) — ferramentas complementares.
