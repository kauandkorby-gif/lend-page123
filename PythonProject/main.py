from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "frota_2026_chave_segura"
ARQUIVO_DADOS = "dados.json"
SAQUE_MINIMO = 20.00

# SENHA DO ADMINISTRADOR (VOCÊ)
SENHA_ADMIN = "123456"

# 10 CAMINHÕES
FROTA = [
    {"id": 1, "nome": "Volvo FH 540", "valor": 50.00, "renda_diaria": 3.00,
     "imagem": "https://image.pollinations.ai/prompt/futuristic%20Volvo%20FH%20540%2C%20neon%20cyan%2C%20dark%20bg?width=600&height=340&nologo=true"},
    {"id": 2, "nome": "Scania R 500", "valor": 100.00, "renda_diaria": 7.00,
     "imagem": "https://image.pollinations.ai/prompt/futuristic%20Scania%20R%20500%2C%20neon%20green%2C%20dark%20truck?width=600&height=340&nologo=true"},
    {"id": 3, "nome": "DAF XF 480", "valor": 200.00, "renda_diaria": 15.00,
     "imagem": "https://image.pollinations.ai/prompt/futuristic%20DAF%20XF%20480%2C%20neon%20blue%2C%20futuristic?width=600&height=340&nologo=true"},
    {"id": 4, "nome": "Iveco S-Way", "valor": 350.00, "renda_diaria": 28.00,
     "imagem": "https://image.pollinations.ai/prompt/futuristic%20Iveco%20S-Way%2C%20orange%20neon%2C%20black?width=600&height=340&nologo=true"},
    {"id": 5, "nome": "MAN TGX 580", "valor": 500.00, "renda_diaria": 45.00,
     "imagem": "https://image.pollinations.ai/prompt/futuristic%20MAN%20TGX%20580%2C%20purple%20neon%2C%20night?width=600&height=340&nologo=true"},
    {"id": 6, "nome": "Mercedes Actros", "valor": 650.00, "renda_diaria": 60.00,
     "imagem": "https://image.pollinations.ai/prompt/futuristic%20Mercedes%20Actros%2C%20silver%20blue%20neon%2C%20dark?width=600&height=340&nologo=true"},
    {"id": 7, "nome": "Renault T High", "valor": 800.00, "renda_diaria": 75.00,
     "imagem": "https://image.pollinations.ai/prompt/futuristic%20Renault%20T%20High%2C%20pink%20neon%2C%20cyberpunk?width=600&height=340&nologo=true"},
    {"id": 8, "nome": "Ford F-Max", "valor": 950.00, "renda_diaria": 90.00,
     "imagem": "https://image.pollinations.ai/prompt/futuristic%20Ford%20F-Max%2C%20red%20neon%2C%20dark%20road?width=600&height=340&nologo=true"},
    {"id": 9, "nome": "Hyundai Xcient", "valor": 1100.00, "renda_diaria": 105.00,
     "imagem": "https://image.pollinations.ai/prompt/futuristic%20Hyundai%20Xcient%2C%20lime%20neon%2C%20eco%20truck?width=600&height=340&nologo=true"},
    {"id": 10, "nome": "Tesla Semi Futuro", "valor": 1500.00, "renda_diaria": 140.00,
     "imagem": "https://image.pollinations.ai/prompt/futuristic%20Tesla%20Semi%2C%20white%20cyan%20led%2C%20ultra%20modern?width=600&height=340&nologo=true"}
]


def carregar():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def salvar(dados):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def add_movimentacao(email, texto, tipo, valor):
    dados = carregar()
    if email not in dados: return
    if "extrato" not in dados[email]:
        dados[email]["extrato"] = []
    dados[email]["extrato"].insert(0, {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "texto": texto,
        "tipo": tipo,
        "valor": round(valor, 2)
    })
    salvar(dados)


def processar_rendas(email):
    dados = carregar()
    if email not in dados: return
    user = dados[email]
    if not user.get("investimentos"): return
    try:
        ultima = datetime.strptime(user.get("ultima_renda", datetime.now().strftime("%d/%m/%Y")), "%d/%m/%Y")
    except:
        ultima = datetime.now() - timedelta(days=1)
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if ultima >= hoje: return
    dias = (hoje - ultima).days
    renda_total = sum(inv["renda_diaria"] * dias for inv in user["investimentos"])
    if renda_total > 0:
        user["saldo"] = round(user["saldo"] + renda_total, 2)
        add_movimentacao(email, f"💰 Renda — {dias} dia(s)", "entrada", renda_total)
    user["ultima_renda"] = hoje.strftime("%d/%m/%Y")
    salvar(dados)


@app.route("/")
def inicio():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method != "POST":
        return render_template("login.html")
    acao = request.form.get("acao")
    dados = carregar()
    if acao == "criar":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        chave_pix = request.form.get("chave_pix", "").strip()
        senha = request.form.get("senha", "").strip()
        if not nome or not email or not chave_pix or not senha:
            flash("⚠️ Preencha todos os campos!", "erro")
            return render_template("login.html")
        if email in dados:
            flash("⚠️ E-mail já cadastrado!", "erro")
            return render_template("login.html")
        dados[email] = {
            "nome": nome, "chave_pix": chave_pix, "senha": senha,
            "saldo": 0.0, "investimentos": [], "extrato": [],
            "saques_pendentes": [], "ultima_renda": datetime.now().strftime("%d/%m/%Y")
        }
        salvar(dados)
        flash("✅ Conta criada! Faça login.", "sucesso")
        return render_template("login.html")
    elif acao == "entrar":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "").strip()
        if email in dados and dados[email]["senha"] == senha:
            session["usuario"] = email
            session["nome"] = dados[email]["nome"]
            processar_rendas(email)
            return redirect(url_for("painel"))
        flash("⚠️ E-mail ou senha errados!", "erro")
        return render_template("login.html")
    return render_template("login.html")


@app.route("/painel")
def painel():
    if "usuario" not in session:
        return redirect(url_for("login"))
    processar_rendas(session["usuario"])
    dados = carregar()
    user = dados[session["usuario"]]
    total_investido = sum(i["valor"] for i in user.get("investimentos", []))
    renda_diaria = sum(i["renda_diaria"] for i in user.get("investimentos", []))
    return render_template("painel.html",
                           nome=user["nome"], saldo=user["saldo"],
                           total_investido=total_investido, renda_diaria=renda_diaria,
                           renda_mensal=renda_diaria * 30, investimentos=user.get("investimentos", []))


@app.route("/caminhoes")
def caminhoes():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("caminhoes.html", frota=FROTA)


@app.route("/investir/<int:veiculo_id>")
def investir(veiculo_id):
    if "usuario" not in session:
        return redirect(url_for("login"))
    processar_rendas(session["usuario"])
    dados = carregar()
    user = dados[session["usuario"]]
    veiculo = next((v for v in FROTA if v["id"] == veiculo_id), None)
    if not veiculo:
        flash("⚠️ Não encontrado!", "erro")
        return redirect(url_for("caminhoes"))
    if user["saldo"] < veiculo["valor"]:
        flash(f"⚠️ Saldo insuficiente! Tem R$ {user['saldo']:.2f}", "erro")
        return redirect(url_for("caminhoes"))
    user["saldo"] = round(user["saldo"] - veiculo["valor"], 2)
    user["investimentos"].append(
        {"nome": veiculo["nome"], "valor": veiculo["valor"], "renda_diaria": veiculo["renda_diaria"]})
    add_movimentacao(session["usuario"], f"🚛 Compra: {veiculo['nome']}", "saida", veiculo["valor"])
    salvar(dados)
    flash(f"✅ {veiculo['nome']} comprado!", "sucesso")
    return redirect(url_for("painel"))


@app.route("/financeiro", methods=["GET", "POST"])
def financeiro():
    if "usuario" not in session:
        return redirect(url_for("login"))
    processar_rendas(session["usuario"])
    dados = carregar()
    user_email = session["usuario"]
    user = dados[user_email]

    if request.method == "POST":
        if "depositar" in request.form:
            try:
                valor = float(request.form.get("valor", "0").replace(",", "."))
                if valor <= 0: raise ValueError()
            except:
                flash("⚠️ Valor inválido!", "erro")
                return render_template("financeiro.html", saldo=user["saldo"], saque_minimo=SAQUE_MINIMO)
            user["saldo"] = round(user["saldo"] + valor, 2)
            add_movimentacao(user_email, "💰 Depósito", "entrada", valor)
            salvar(dados)
            flash(f"✅ Depósito de R$ {valor:.2f} realizado!", "sucesso")

        elif "sacar" in request.form:
            try:
                valor = float(request.form.get("valor", "0").replace(",", "."))
                if valor <= 0: raise ValueError()
            except:
                flash("⚠️ Valor inválido!", "erro")
                return render_template("financeiro.html", saldo=user["saldo"], saque_minimo=SAQUE_MINIMO)
            if valor < SAQUE_MINIMO:
                flash(f"⚠️ Saque mínimo R$ {SAQUE_MINIMO:.2f}!", "erro")
                return render_template("financeiro.html", saldo=user["saldo"], saque_minimo=SAQUE_MINIMO)
            if valor > user["saldo"]:
                flash("⚠️ Saldo insuficiente!", "erro")
                return render_template("financeiro.html", saldo=user["saldo"], saque_minimo=SAQUE_MINIMO)

            # RESERVA O VALOR E COLOCA EM PENDENTE
            user["saldo"] = round(user["saldo"] - valor, 2)
            if "saques_pendentes" not in user:
                user["saques_pendentes"] = []
            user["saques_pendentes"].append({
                "id_saque": len(user["saques_pendentes"]) + 1,
                "valor": round(valor, 2),
                "data_solicitacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "status": "pendente"
            })
            salvar(dados)
            flash(f"✅ Saque de R$ {valor:.2f} solicitado! Aguardando aprovação.", "sucesso")
        return redirect(url_for("financeiro"))

    # Conta saques pendentes
    qtd_pendentes = len([s for s in user.get("saques_pendentes", []) if s["status"] == "pendente"])
    return render_template("financeiro.html", saldo=user["saldo"], saque_minimo=SAQUE_MINIMO,
                           qtd_pendentes=qtd_pendentes)


@app.route("/extrato")
def extrato():
    if "usuario" not in session:
        return redirect(url_for("login"))
    processar_rendas(session["usuario"])
    dados = carregar()
    user = dados[session["usuario"]]
    return render_template("extrato.html",
                           nome=user["nome"], saldo=user["saldo"],
                           extrato=user.get("extrato", []),
                           saques_pendentes=[s for s in user.get("saques_pendentes", []) if s["status"] == "pendente"],
                           total_entradas=sum(m["valor"] for m in user.get("extrato", []) if m["tipo"] == "entrada"),
                           total_saidas=sum(m["valor"] for m in user.get("extrato", []) if m["tipo"] == "saida"))


# ========== PAINEL ADMINISTRATIVO ==========
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("senha") == SENHA_ADMIN:
            session["admin"] = True
            return redirect(url_for("admin_painel"))
        flash("⚠️ Senha incorreta!", "erro")
    return render_template("admin_login.html")


@app.route("/admin/sair")
def admin_sair():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


@app.route("/admin")
def admin_painel():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    dados = carregar()
    # Coleta todos os saques pendentes de todos os usuários
    todos_pendentes = []
    for email, user in dados.items():
        for saque in user.get("saques_pendentes", []):
            if saque["status"] == "pendente":
                todos_pendentes.append({
                    "email_usuario": email,
                    "nome_usuario": user["nome"],
                    "chave_pix": user["chave_pix"],
                    "id_saque": saque["id_saque"],
                    "valor": saque["valor"],
                    "data_solicitacao": saque["data_solicitacao"]
                })
    return render_template("admin_painel.html", saques=todos_pendentes)


@app.route("/admin/aprovar", methods=["POST"])
def admin_aprovar():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    email_usuario = request.form.get("email_usuario")
    id_saque = int(request.form.get("id_saque"))
    dados = carregar()

    if email_usuario in dados:
        user = dados[email_usuario]
        for saque in user.get("saques_pendentes", []):
            if saque["id_saque"] == id_saque and saque["status"] == "pendente":
                saque["status"] = "aprovado"
                add_movimentacao(email_usuario, f"✅ Saque PIX — APROVADO", "saida", saque["valor"])
                salvar(dados)
                flash(f"✅ Saque de R$ {saque['valor']:.2f} APROVADO!", "sucesso")
                return redirect(url_for("admin_painel"))
    flash("⚠️ Saque não encontrado!", "erro")
    return redirect(url_for("admin_painel"))


@app.route("/admin/negar", methods=["POST"])
def admin_negar():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    email_usuario = request.form.get("email_usuario")
    id_saque = int(request.form.get("id_saque"))
    dados = carregar()

    if email_usuario in dados:
        user = dados[email_usuario]
        for saque in user.get("saques_pendentes", []):
            if saque["id_saque"] == id_saque and saque["status"] == "pendente":
                saque["status"] = "negado"
                # Devolve o valor pro saldo
                user["saldo"] = round(user["saldo"] + saque["valor"], 2)
                add_movimentacao(email_usuario, f"❌ Saque Negado — Valor devolvido", "entrada", saque["valor"])
                salvar(dados)
                flash(f"❌ Saque de R$ {saque['valor']:.2f} NEGADO — valor devolvido!", "erro")
                return redirect(url_for("admin_painel"))
    flash("⚠️ Saque não encontrado!", "erro")
    return redirect(url_for("admin_painel"))


@app.route("/atualizar-dados")
def atualizar_dados():
    if "usuario" not in session:
        return jsonify({"erro": "nao_logado"})
    processar_rendas(session["usuario"])
    dados = carregar()
    user = dados[session["usuario"]]
    renda_diaria = sum(i["renda_diaria"] for i in user.get("investimentos", []))
    return jsonify({"saldo": round(user["saldo"], 2), "renda_diaria": round(renda_diaria, 2)})


@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)