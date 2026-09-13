# Auditoria por endpoint

O modo `endpoint` recebe uma URL autorizada, faz verificações HTTP limitadas e entrega evidências em JSON e Markdown. Você não precisa fornecer o código para começar.

## Pelo agente

Depois de instalar a skill, use:

```text
Use guard-raillm para verificar meu endpoint https://meu-app.example/health.
Autorizo a auditoria básica dessa URL.
Explique os problemas encontrados, as correções e o que não foi possível testar.
```

O agente reutiliza essa autorização e executa o modo básico quando possui Python e acesso à rede. Não precisa pedir a mesma permissão novamente. Se não tiver ferramentas de execução, deve informar que nenhum teste foi realizado.

## Pelo terminal

Na raiz do repositório, veja o plano sem fazer requisições:

```sh
python skills/guard-raillm/scripts/endpoint_audit.py https://meu-app.example/health
```

Execute esse plano no alvo autorizado:

```sh
python skills/guard-raillm/scripts/endpoint_audit.py https://meu-app.example/health --authorized
```

O básico envia até três GETs à URL informada: uma resposta de referência e duas com origens sintéticas para avaliar CORS. Não acessa subdomínios, links da página ou destinos de redirecionamentos. As origens sintéticas são apenas valores de cabeçalho; não são acessadas.

## Verificações disponíveis

| Verificação | Resultado possível | O que não permite concluir sozinho |
|---|---|---|
| HTTP/HTTPS | Uso de HTTP ou sucesso/falha na validação do certificado e hostname | Resistência de todos os protocolos/cifras TLS ou de outros hosts |
| Cabeçalhos | Presença de HSTS e, em HTML, CSP, nosniff e referrer policy | Validade e força de toda a política; exploração comprovada |
| Cookies | Ausência de Secure, HttpOnly ou SameSite, sem expor nomes/valores | Que o cookie seja de autenticação ou explorável |
| CORS | Duas origens distintas aceitas com credenciais | Roubo de dados sem comprovar resposta sensível e comportamento do navegador |
| Erros | Assinaturas de stack trace ou erro SQL | Que o texto não seja apenas um exemplo/documentação |
| Arquivos sensíveis | Resposta HEAD em `.env` e `.git/config` | Existência de segredo: login e páginas de fallback também podem retornar 200 |
| Autenticação | Comparação do status anônimo versus identidade de teste | Bypass confirmado, autorização de objetos ou isolamento entre tenants |
| Rate-limit | Ocorrência de 429 na pequena amostra | Ausência de limite, proteção distribuída ou resistência a DDoS |

O agente apresenta **observações confirmadas**, **suspeitas** e **melhorias de configuração** separadamente. Você recebe uma lista do que foi e do que não foi testado.

## Opções de escopo

Acrescente somente rotas e verificações que você está autorizado a testar:

```sh
python skills/guard-raillm/scripts/endpoint_audit.py https://meu-app.example/health --authorized --route /api/status --probe-files --rate-samples 3 --max-requests 12
```

`--probe-files` amplia o escopo para a raiz da origem: `/.env`, `/.git/config` e uma rota aleatória de controle, usando apenas HEAD. Não baixa os arquivos. Uma URL explicitamente reconhecida como arquivo sensível também usa apenas HEAD.

`--rate-samples` faz solicitações adicionais espaçadas à primeira rota; não produz uma carga suficiente para provar resistência a ataques. Evite endpoints que enviam e-mails, disparam cobranças, encerram sessões ou executam operações apenas ao serem acessados.

Para comparar um endpoint protegido, prepare uma variável de ambiente com um **token Bearer de teste** por um mecanismo seguro do seu ambiente. Não cole o token no chat ou no comando. Então use:

```sh
python skills/guard-raillm/scripts/endpoint_audit.py https://meu-app.example/api/test-resource --authorized --protected --auth-env GUARD_AUDIT_TOKEN
```

O token é enviado apenas na comparação autenticada das rotas selecionadas, sempre com HTTPS validado. O executor não faz login automático, não aceita credenciais na URL e não implementa sessões via Cookie. URLs com query string ou fragmento não são aceitas nesta versão; isso evita carregar links assinados ou tokens pela linha de comando.

Para um serviço **local/de rede privada explicitamente autorizado**, adicione `--allow-private`. Destinos de metadados de nuvem e endereços link-local permanecem bloqueados. Variáveis de proxy não são utilizadas.

## Limites e interrupção

O padrão permite até 12 requisições no total, execução sequencial, intervalo mínimo de 0,5 segundo, cinco segundos por requisição e orçamento de rede de 30 segundos. Opções permitem até 40 requisições e 120 segundos; não há paralelismo ou retentativa automática.

O executor interrompe ao receber redirecionamento, 429, erro de servidor, falha TLS/rede ou ao atingir um limite. O relatório preserva resultados anteriores e explicita verificações pendentes. Não segue nem mesmo um redirecionamento para o mesmo host: confirme o destino e faça uma nova avaliação dentro do escopo.

## Relatórios

Por padrão, cada execução cria `.guard-raillm/endpoint-<identificador>/report.json` e `report.md`. Você também pode selecionar uma pasta nova com `--output`. Pastas existentes não são sobrescritas.

O relatório não guarda corpos de resposta, tokens, nomes/valores de cookies ou cabeçalhos brutos. Rotas são identificadas pela ordem dos argumentos, sem registrar caminhos que possam conter identificadores pessoais. Mantenha o mapeamento da URL e das rotas em um plano privado. A origem do alvo permanece no JSON e pode ser sensível.

No POSIX, arquivos são criados com modo 0600 e a pasta com 0700. No Windows, confira as permissões da pasta. Ignorar um relatório no Git não o criptografa.

| Código de saída | Significado |
|---|---|
| 0 | Plano offline, ou execução concluída sem achados confirmados/suspeitos; melhorias ainda podem existir |
| 1 | Execução concluída com observações confirmadas ou suspeitas |
| 2 | Execução incompleta, entrada inválida ou erro operacional |

Nenhum código de saída certifica segurança.

## Testes mais profundos

A URL é o ponto de partida. Testar injeções, uploads, permissões entre usuários ou regras de banco exige rotas/contrato de API, dados descartáveis e verificações específicas. A skill inclui [procedimentos de aprofundamento](../skills/guard-raillm/references/endpoint-follow-up.md), mas o executor básico não realiza exploração, escrita de dados, brute force ou varredura de todo o site.

A implementação foi exercitada com servidores HTTP/HTTPS locais e dados sintéticos. A execução pelo agente nos diferentes modelos continua sem benchmark publicado.
