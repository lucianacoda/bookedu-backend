from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. Configuração do Banco de Dados SQLite (Exigência do MVP)
SQLALCHEMY_DATABASE_URL = "sqlite:///./biblioteca.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Como um "Livro" é salvo no Banco de Dados
class LivroDB(Base):
    __tablename__ = "livros"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    autor = Column(String)
    isbn = Column(String)

# Cria o arquivo do banco de dados na sua pasta automaticamente
Base.metadata.create_all(bind=engine)

# 3. Inicializa a nossa API
app = FastAPI(title="BookEdu API", description="API para gerenciamento de biblioteca escolar")

# 4. Formato de dados que a API vai receber da Interface (Frontend)
class Livro(BaseModel):
    titulo: str
    autor: str
    isbn: str

# --- AS 4 ROTAS OBRIGATÓRIAS ---

# ROTA 1: POST (Criar/Cadastrar um livro novo)
@app.post("/livros/")
def criar_livro(livro: Livro):
    db = SessionLocal()
    novo_livro = LivroDB(titulo=livro.titulo, autor=livro.autor, isbn=livro.isbn)
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)
    db.close()
    return novo_livro

# ROTA 2: GET (Ler/Listar todos os livros cadastrados)
@app.get("/livros/")
def listar_livros():
    db = SessionLocal()
    livros = db.query(LivroDB).all()
    db.close()
    return livros

# ROTA 3: PUT (Atualizar os dados de um livro existente)
@app.put("/livros/{livro_id}")
def atualizar_livro(livro_id: int, livro: Livro):
    db = SessionLocal()
    livro_db = db.query(LivroDB).filter(LivroDB.id == livro_id).first()
    if not livro_db:
        db.close()
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    livro_db.titulo = livro.titulo
    livro_db.autor = livro.autor
    livro_db.isbn = livro.isbn
    db.commit()
    db.refresh(livro_db)
    db.close()
    return livro_db

# ROTA 4: DELETE (Deletar um livro do sistema)
@app.delete("/livros/{livro_id}")
def deletar_livro(livro_id: int):
    db = SessionLocal()
    livro_db = db.query(LivroDB).filter(LivroDB.id == livro_id).first()
    if not livro_db:
        db.close()
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    db.delete(livro_db)
    db.commit()
    db.close()
    return {"mensagem": "Livro deletado com sucesso"}