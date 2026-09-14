from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# Configuração do Banco de Dados SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./biblioteca.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo da Tabela no Banco
class LivroModel(Base):
    __tablename__ = "livros"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    autor = Column(String)
    isbn = Column(String, unique=True, index=True)

Base.metadata.create_all(bind=engine)

# Inicialização do FastAPI
app = FastAPI(title="BookEdu API", description="API para gerenciamento de biblioteca escolar", version="0.1.0")

# Configuração do CORS (Resolve o bloqueio do navegador com o frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schema Pydantic para validação de dados
class LivroSchema(BaseModel):
    titulo: str
    autor: str
    isbn: str

    class Config:
        from_attributes = True

# Dependência para pegar a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rota POST: Criar Livro
@app.post("/livros/", response_model=LivroSchema)
def criar_livro(livro: LivroSchema, db: Session = Depends(get_db)):
    db_livro = LivroModel(titulo=livro.titulo, autor=livro.autor, isbn=livro.isbn)
    db.add(db_livro)
    db.commit()
    db.refresh(db_livro)
    return db_livro

# Rota GET: Listar Livros
@app.get("/livros/", response_model=list[LivroSchema])
def listar_livros(db: Session = Depends(get_db)):
    return db.query(LivroModel).all()