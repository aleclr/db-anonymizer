# 🕵️‍♂️ Pipeline de Anonimização de Dados

Uma ferramenta Python simples para anonimizar dados de bancos relacionais (MySQL ou PostgreSQL).  
A aplicação exporta as tabelas do banco, realiza a anonimização dos dados com dados substitutos (mantendo a sensibilidade e preservando a estrutura) baseado em regras customizáveis, e importa os dados anonimizados de volta ao banco.

---

## 📦 Features

- 🔐 Anonimização de tabelas com regras customizáveis
- 🛠 Suporte para MySQL e PostgreSQL
- 🧾 Configuração simples com arquivos YAML
- 🔄 Pipeline Completa: Exportação → Anonimização → Importação
- :ladder: Suporte para execução de etapas separadamente

---

## ⚙️ Configuração

### 1. `config/db_config.yaml`

Este arquivo contém todas as informações necessárias para a conexão com o banco de dados.

```yaml
db_type: mysql # or postgresql
host: localhost
port: 3306
user: your_db_user
password: your_db_password
database: your_database_name
```

> ⚠️ Não esqueça de garantir que o banco de dados esteja em funcionamento antes de executar a ferramenta.

---

### 2. `config/anonymization_rules.yaml`

Define as regras de anonimização para cada tabela, utilizando as funções de máscara suportadas pela aplicação.

```yaml
clients:
  full_name: mask_name
  email: mask_email
  cpf: mask_cpf
  phone: mask_phone

orders:
  total: mask_float
  created_at: mask_date
  user_id: mask_integer
```

Funções suportadas atualmente:

- `mask_email`
- `mask_name`
- `mask_cpf`
- `mask_phone`
- `mask_string`
- `mask_integer`
- `mask_float`
- `mask_date`
- `mask_boolean`
- `hash_value`
- `nullify`

---

## ▶️ Como utilizar a ferramenta

### 1. Instale as dependências

É recomendado a utilização de ambientes virtuais para a instalação das dependências:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Execute a pipeline

Você tem a opção de executar cada passo individualmente:

```bash
python main.py --step export     # Exporta as tabelas do banco para a pasta /csv_exports
python main.py --step anonymize  # Aplica as regras e anonimiza as tabelas, o resultado fica na pasta /csv_anonymized
python main.py --step import     # Importa os arquivos csv anonimizados da pasta /csv_anonymized para o banco
```

Ou executar a pipeline completa:

```bash
python main.py --step all
```

---

## 📁 Estrutura de arquivos do projeto

```
project-root/
├── config/
│   ├── db_config.yaml
│   └── anonymization_rules.yaml
├── csv_exports/          # Dados originais exportados
├── csv_anonymized/       # CSV's anonimizados
├── src/
│   ├── anonymizer.py
│   ├── db_connector.py
│   ├── exporter.py
│   ├── importer.py
│   └── utils.py
├── main.py
└── requirements.txt
```

## ⚙️ Criação de tabela teste para as funcionalidades de anonimização

Caso queira testar as funções disponíveis na ferramenta, a seguinte tabela pode ser criada, e o seguinte arquivo config de regras pode ser utilizado:

```
CREATE TABLE teste_anonimizacao (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    cpf VARCHAR(11),
    phone VARCHAR(11),
    address VARCHAR(200),
    birth_date DATE,
    salary DECIMAL(10, 2)
);

INSERT INTO teste_anonimizacao (name, email, cpf, phone, address, birth_date, salary) VALUES
('Alice Martins', 'alice@example.com', '12345678901', '11987654321', 'Rua das Flores, 123', '1990-01-15', 5500.75),
('Bruno Lima', 'bruno@example.com', '23456789012', '21999887766', 'Av. Paulista, 456', '1985-03-22', 7000.50),
('Carla Souza', 'carla@example.com', '34567890123', '31988776655', 'Rua A, 789', '1992-06-10', 6400.00),
('Daniel Costa', 'daniel@example.com', '45678901234', '41977665544', 'Av. Central, 1010', '1988-11-05', 8300.25),
('Eduarda Melo', 'eduarda@example.com', '56789012345', '51966554433', 'Rua B, 202', '1995-09-30', 7200.80);
```
<br>

anonymization_rules.yaml

```yaml
teste_anonimizacao:
  name: mask_name
  email: mask_email
  cpf: mask_cpf
  phone: mask_phone
  address: mask_address
  birth_date: mask_date
  salary: mask_number
```

---

### 🕵️‍♂️ Acesse a [wiki](https://github.com/aleclr/db-anonymizer/wiki) para mais informações como pesquisas e plano de updates
