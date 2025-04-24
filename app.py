from flask import Flask, render_template, request, session
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'secreto'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Dados do chatbot
pilares = {
    "Uso da Plataforma": [
        "Como me cadastro na plataforma?",
        "Esqueci minha senha, o que faço?",
        "Onde acompanho minhas métricas de impacto?"
    ],
    "Conceito ESG": [
        "O que é ESG?",
        "Por que ESG é importante para empresas/organizações e indivíduos?",
        "A plataforma oferece conteúdos educativos?"
    ],
    "Suporte Técnico": [
        "Estou enfrentando erro ao usar uma funcionalidade, e agora?",
        "A plataforma está fora do ar?",
        "Como entro em contato com o suporte humano?"
    ],
    "Ferramentas e Funcionalidades": [
        "Como usar a calculadora de carbono?",
        "O que é o painel de impacto?",
        "Como integro dados da minha empresa à plataforma?"
    ]
}

respostas = {
    pilares["Uso da Plataforma"][0]: "Você pode se cadastrar clicando em 'Criar conta' na página inicial.",
    pilares["Uso da Plataforma"][1]: "Clique em 'Esqueci minha senha' e siga os passos.",
    pilares["Uso da Plataforma"][2]: "As métricas ficam disponíveis no seu painel pessoal.",
    pilares["Conceito ESG"][0]: "ESG é uma sigla para práticas Ambientais, Sociais e de Governança.",
    pilares["Conceito ESG"][1]: "Porque demonstra responsabilidade e sustentabilidade.",
    pilares["Conceito ESG"][2]: "Sim! A plataforma oferece diversos conteúdos educativos.",
    pilares["Suporte Técnico"][0]: "Entre em contato com o suporte ou tente recarregar a página.",
    pilares["Suporte Técnico"][1]: "Verifique sua conexão e tente novamente em instantes.",
    pilares["Suporte Técnico"][2]: "Você pode entrar em contato através do chat ou e-mail de suporte.",
    pilares["Ferramentas e Funcionalidades"][0]: "Você encontra a calculadora no menu principal.",
    pilares["Ferramentas e Funcionalidades"][1]: "O painel de impacto mostra seu desempenho em ESG.",
    pilares["Ferramentas e Funcionalidades"][2]: "A integração pode ser feita via API na aba configurações."
}

@app.route('/')
def index():
    if 'historico' not in session:
        session['historico'] = []
    session['chat_atual'] = []
    return render_template('index.html', pilares=list(pilares.keys()), historico=session['historico'], chat=session['chat_atual'], pilar_selecionado=None)

@app.route('/enviar', methods=['POST'])
def enviar():
    novo_chat = 'novo_chat' in request.form
    pilar = request.form.get('pilar')
    pergunta_idx = request.form.get('pergunta_idx')

    if novo_chat:
        # Salvar o título (última pergunta feita) no histórico
        if session.get('chat_atual'):
            ultima_pergunta = next((m['texto'] for m in reversed(session['chat_atual']) if m['lado'] == 'direito'), None)
            if ultima_pergunta:
                session['historico'].append(ultima_pergunta)
                session.modified = True
        session['chat_atual'] = []
        return render_template('index.html', pilares=list(pilares.keys()), historico=session['historico'], chat=session['chat_atual'], pilar_selecionado=None)

    if pergunta_idx == '-1':
        # Exibe perguntas do pilar
        perguntas = pilares.get(pilar, [])
        chat = [{'texto': f"{pilar} - Escolha um número de 1 a 3:", 'lado': 'esquerdo'}]
        for i, pergunta in enumerate(perguntas):
            chat.append({'texto': f"{i + 1}. {pergunta}", 'lado': 'esquerdo'})
        session['chat_atual'] = chat
        session.modified = True
        return render_template('index.html', pilares=list(pilares.keys()), historico=session['historico'], chat=chat, pilar_selecionado=pilar)

    # Processar pergunta digitada
    try:
        pergunta_idx = int(pergunta_idx) - 1  # Ajusta para 1-3
        perguntas = pilares.get(pilar, [])
        if 0 <= pergunta_idx < len(perguntas):
            pergunta = perguntas[pergunta_idx]
            resposta = respostas.get(pergunta, "Desculpe, não encontrei resposta para isso.")
            chat_atual = session.get('chat_atual', [])
            chat_atual.append({'texto': pergunta, 'lado': 'direito'})
            chat_atual.append({'texto': resposta, 'lado': 'esquerdo'})
            session['chat_atual'] = chat_atual
            session.modified = True
            return render_template('index.html', pilares=list(pilares.keys()), historico=session['historico'], chat=chat_atual, pilar_selecionado=pilar)
        else:
            erro = "Pergunta inválida. Digite 1, 2 ou 3."
            return render_template('index.html', pilares=list(pilares.keys()), historico=session['historico'], chat=session['chat_atual'], pilar_selecionado=pilar, erro=erro)
    except ValueError:
        erro = "Entrada inválida. Digite um número válido."
        return render_template('index.html', pilares=list(pilares.keys()), historico=session['historico'], chat=session['chat_atual'], pilar_selecionado=pilar, erro=erro)

if __name__ == '__main__':
    app.run(debug=True)
