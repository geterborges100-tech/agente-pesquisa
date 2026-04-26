# Controle de Sincronização e Infraestrutura

Este documento detalha a arquitetura de sincronização entre o servidor de desenvolvimento (Oracle Cloud) e o repositório remoto (GitHub), garantindo a integridade do código e da documentação do projeto.

---

## 1. Arquitetura de Sincronização
O projeto utiliza um modelo de persistência distribuída:
- **Servidor Oracle:** Ambiente primário de execução, desenvolvimento e manipulação de arquivos.
- **GitHub:** Repositório oficial, backup de segurança e histórico de versões.
- **Fluxo:** O servidor atua como a "fonte da verdade" diária, enviando atualizações para o GitHub via protocolo Git.

## 2. Automação via Crontab
Para evitar perda de dados por falha humana ou técnica, foi implementada uma rotina de backup automático.

- **Frequência:** Diariamente às 23:00.
- **Lógica de Execução:**
    1. O sistema verifica o estado do repositório (`git status -s`).
    2. **Se houver mudanças:** Executa automaticamente o ciclo `add`, `commit` e `push`.
    3. **Se não houver mudanças:** A operação é encerrada sem poluir o histórico de commits.

**Comando configurado:**
\`\`\`bash
0 23 * * * cd ~/agente-pesquisa && git status -s | grep -q . && git add . && git commit -m "Auto-backup: \$(date)" && git push origin main
\`\`\`

## 3. Protocolo de Uso
Para manter a paridade entre os ambientes, deve-se seguir o seguinte protocolo:
1. **Prioridade de Edição:** Sempre realizar alterações diretamente no servidor Oracle.
2. **Edição Web:** Evitar editar arquivos diretamente na interface do GitHub.
3. **Resolução de Conflitos:** Caso existam commits na nuvem que não estejam no servidor, utilizar o comando de integração:
   `git pull origin main --rebase`

## 4. Comandos Úteis
Comandos essenciais para gestão manual do ambiente:
* \`git status\`: Verifica arquivos modificados ou novos.
* \`git log --oneline\`: Visualiza o histórico resumido de versões.
* \`git fetch origin && git diff main origin/main --stat\`: Compara a diferença exata entre o servidor e o GitHub.
* \`git add . && git commit -m "Mensagem" && git push origin main\`: Ciclo de envio manual.

## 5. Riscos e Cuidados
- **Credenciais:** O acesso é feito via *Personal Access Token (PAT)* armazenado com \`credential.helper store\`. Não compartilhar este arquivo.
- **Conflitos:** Pushes rejeitados indicam que o servidor está desatualizado em relação ao GitHub.
- **Crescimento:** Monitorar o tamanho da pasta \`.git\` caso sejam manipulados muitos arquivos binários ou logs grandes.

## 6. Boas Práticas
- Realizar commits pequenos e granulares com mensagens claras.
- Validar se o código está funcional antes do horário da automação (23:00).
- Não depender exclusivamente do backup automático; realizar envios manuais após marcos importantes de desenvolvimento.

## 7. Status Atual do Sistema
- **Status:** Ativo.
- **Paridade:** Confirmada em 26/04/2026. Servidor e GitHub estão 100% sincronizados.

## 7. Status Atual do Sistema
- **Status:** Ativo.
- **Paridade:** Confirmada em 26/04/2026. Servidor e GitHub estão 100% sincronizados.
