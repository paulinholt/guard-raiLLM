# Instalação e uso

Clone este repositório e revise os arquivos antes de instalar. A instalação copia somente `skills/guard-raillm`; não baixa dependências, não configura hooks e recusa sobrescrever uma instalação existente. Execute os comandos na raiz do repositório clonado.

## Codex e agentes GPT

```sh
python scripts/install.py --dest ~/.agents/skills
```

Ou instale no projeto auditado usando um caminho explícito:

```sh
python scripts/install.py --dest /caminho/do/projeto/.agents/skills
```

Invoque `$guard-raillm` ou peça a auditoria pelo nome. A descoberta depende do host, não apenas do modelo GPT escolhido. A documentação oficial descreve `.agents/skills` como diretório local de skills do Codex. [Fonte](https://learn.chatgpt.com/docs/build-skills).

## Claude Code

```sh
python scripts/install.py --dest ~/.claude/skills
```

Invoque `/guard-raillm`. Para compartilhar no projeto, use `/caminho/do/projeto/.claude/skills`. Instalações pessoais locais não implicam disponibilidade em sessões cloud. [Fonte](https://code.claude.com/docs/en/skills).

## Kimi Code

Na documentação consultada, o diretório específico padrão é `~/.kimi-code/skills`, alterado quando `KIMI_CODE_HOME` é configurado:

```sh
python scripts/install.py --dest ~/.kimi-code/skills
```

Invoque `/skill:guard-raillm`. Versões anteriores usavam outros diretórios; confira a documentação correspondente à versão instalada. Se houver `KIMI_CODE_HOME`, forneça seu caminho efetivo acrescido de `/skills`. [Fonte](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html).

## Windows

Os mesmos comandos funcionam em PowerShell quando `python` está no PATH; o instalador expande `~`. Para caminhos com espaços, use aspas:

```powershell
python scripts/install.py --dest 'C:/Meus Projetos/app/.agents/skills'
```

## Chats e instalação manual

Copie a pasta completa `guard-raillm` para o diretório de skills do host, mantendo as referências. Em um chat sem instalação nativa, forneça `SKILL.md` e as referências aplicáveis junto com trechos sanitizados do projeto. Solicite que o modelo siga o fluxo e sinalize arquivos ausentes. Um upload de instruções não prova que o chat pode acessar disco, executar scripts ou verificar produção.

O ZIP da release contém uma pasta `guard-raillm/`; extraia-a para o diretório adequado. O suporte a upload direto do ZIP varia por produto. Reinicie a sessão caso a skill não apareça. Verifique se o agente consegue ler `references/reporting.md` antes de depender do relatório.

## Atualização e remoção

Revise o diff da nova versão e guarde personalizações. O instalador não substitui arquivos existentes; mova ou remova deliberadamente apenas a instalação antiga após revisar o destino. Para desinstalar, remova a pasta `guard-raillm` no diretório onde a instalou. Não há serviço ou hook adicional.

## Exemplos

```text
Use guard-raillm no meu endpoint https://meu-app.example/health; autorizo a auditoria básica dessa URL.
Use guard-raillm em modo quick antes do deploy e destaque o que exige acesso ao ambiente.
Use guard-raillm em modo diff entre a branch base e esta branch; verifique mudanças de autorização.
Use guard-raillm em modo full no Supabase: confira RLS, RPCs e acesso entre dois tenants.
Use guard-raillm em modo verify para avaliar a correção de GR-001 com testes locais.
```

Relatórios são potencialmente sensíveis. Use uma pasta privada ignorada pelo Git, confira seu conteúdo antes de compartilhar e não inclua credenciais reais nos prompts.

Para auditorias sem código-fonte, veja [o modo endpoint](endpoint.md). A partir da v0.2.0, o pacote inclui o executor HTTP; instalações da v0.1.0 precisam ser atualizadas para usá-lo.
