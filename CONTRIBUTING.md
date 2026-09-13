# Contribuições

Contribuições devem melhorar decisões verificáveis da auditoria, não apenas aumentar listas de termos. Para uma regra nova, descreva o contexto em que se aplica, evidência necessária, possível falso positivo e teste seguro. Use fontes primárias e confira licenças antes de reutilizar conteúdo.

Mantenha o núcleo em inglês para portabilidade e a documentação principal em português. Respostas da skill seguem o idioma do usuário. Preserve o carregamento seletivo de referências e a separação entre revisão, execução e alteração de ambientes externos.

Execute:

```sh
python scripts/validate.py
python -m unittest discover -s tests -v
```

Não acrescente credenciais reais, dumps, relatórios privados ou testes que contatem produção. Para scripts, prefira biblioteca padrão, caminhos explícitos, ausência de shell e limites de recursos. Não introduza instalação automática de ferramentas ou coleta de telemetria.

Para alterações de comportamento, atualize [os cenários](evals/README.md) e registre resultados reais, incluindo falhas e testes não executados. Testes estruturais não justificam alegações de eficácia contra vulnerabilidades.
