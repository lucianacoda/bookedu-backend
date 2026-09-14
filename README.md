# BookEdu - API (Backend)

Este é o módulo backend (API REST) do sistema BookEdu, um gerenciador de biblioteca escolar. Ele foi desenvolvido como requisito do MVP da pós-graduação.

## Objetivo
O sistema atua como o cérebro da biblioteca, recebendo requisições da interface, processando regras de negócio e salvando os registros (livros e alunos) no banco de dados SQLite.

## Instruções de Instalação

Para que outros desenvolvedores possam configurar o ambiente local, siga as etapas abaixo:

1. **Clone o repositório:**
   git clone https://github.com/SEU_USUARIO/bookedu-backend.git

2. **Acesse a pasta do projeto:**
   cd bookedu-backend

3. **Inicie o ambiente virtual (Recomendado):**
   python3 -m venv venv
   source venv/bin/activate

4. **Instale as dependências:**
   pip install -r requirements.txt

5. **Execute a aplicação (via Uvicorn):**
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload