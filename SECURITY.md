# Segurança

Para relatar uma vulnerabilidade no guard-raiLLM, use a opção privada **Report a vulnerability** na aba Security deste repositório. Não publique credenciais, dados de terceiros ou detalhes sensíveis em issues públicas.

Informe versão/revisão, componente afetado, comportamento esperado, impacto e reprodução com dados sintéticos. Relatos sobre aplicações auditadas pertencem aos responsáveis por essas aplicações; não envie seus segredos para este projeto.

A versão mantida é 0.2.x. Correções são distribuídas como novas revisões/releases; revise as mudanças antes de atualizar sua instalação.

O executor de endpoints é uma CLI local para alvos autorizados. Não o exponha como serviço público de varredura: autenticação de usuários, isolamento por execução, quotas globais e controles de saída da rede exigiriam uma arquitetura adicional. Relatórios usam permissões restritivas em sistemas POSIX; no Windows, a proteção também depende das ACLs herdadas da pasta.

O fluxo limita a auditoria ao escopo autorizado e evita exposição de segredos. Essas instruções não substituem as permissões, isolamento ou controles do ambiente que executa o agente. Resultados podem conter falsos positivos e falsos negativos.
