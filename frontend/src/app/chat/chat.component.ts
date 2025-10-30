import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { EstudanteService } from '../estudante.service';
import { Mensagem } from '../mensagem';
import { MarkdownComponent } from 'ngx-markdown';
import { Subscription } from 'rxjs';
import { PerfilEstudante } from '../estudante-perfil/estudante-perfil.component';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule, MarkdownComponent],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss'
})
export class ChatComponent implements OnInit {
  mensagens: Mensagem[] = [];
  usuarioInput: string = '';
  estaCarregando = false;
  
  private sub?: Subscription;

  constructor(private estudanteService: EstudanteService) {}
  ngOnInit() {
    this.sub = this.estudanteService.initRelatorio$.subscribe(({userId, perfil}) => {
      console.log("ChatComponent recebeu solicitação de relatório inicial");
      this.obterRelatorioInicial(userId, perfil);
    });
  }

  obterRelatorioInicial(id: number, perfil: PerfilEstudante) {
  console.log('teste, obterRelatorioInicial');
  // 1. Ative o indicador AQUI, no início de tudo
  this.estaCarregando = true;

    this.estudanteService.iniciarChat(id, perfil).subscribe({
    next: (resposta) => {
      const mensagemInicial: Mensagem = {
        chat_id: this.estudanteService.obtemId(),
        text: resposta.relatorio_inicial,
        remetente: 'bot',
        timestamp: new Date()
      };
      this.mensagens.push(mensagemInicial);
      this.salvarChat();
    },
    error: (err) => {
      console.error("Falha ao iniciar o chat com o backend", err);
    },
    complete: () => {
      // 2. Desative o indicador DEPOIS que a resposta do backend chegar
      this.estaCarregando = false;
    }
  });

  // this.estudanteService.obterNotasLocais().subscribe({
  //   next: (notasDoAluno) => {

  //   },
  //   error: (err) => {
  //     console.error("Falha ao carregar o arquivo JSON local de notas", err);
  //     // 3. Desative também em caso de erro ao carregar o arquivo local
  //     this.estaCarregando = false;
  //   }
  // });
}


  enviarMensagem() {
    if (!this.usuarioInput.trim()) return;

    const perfilLS = localStorage.getItem('perfil_estudante_v1');
    const perfil = perfilLS ? JSON.parse(perfilLS) : null;

    const userMessage: Mensagem = {
      chat_id: this.estudanteService.obtemId(),
      text: this.usuarioInput,
      remetente: 'usuario',
      timestamp: new Date()
    };
    this.mensagens.push(userMessage);
    const textoParaEnviar = this.usuarioInput;
    this.usuarioInput = '';
    this.salvarChat();

    this.estaCarregando = true; // Ativa o indicador

    this.estudanteService.enviarMensagem(textoParaEnviar, perfil).subscribe({
      next: (respostaDoBot) => {
        const botMessage: Mensagem = {
          ...respostaDoBot,
          timestamp: new Date(respostaDoBot.timestamp)
        };
        this.mensagens.push(botMessage);
        this.salvarChat();
      },
      error: (err) => {
        console.error("Falha ao obter resposta do bot", err);
        const erroMsg: Mensagem = {
          chat_id: this.estudanteService.obtemId(),
          text: "Desculpe, estou com dificuldades para responder. Por favor, tente novamente.",
          remetente: 'bot',
          timestamp: new Date()
        };
        this.mensagens.push(erroMsg);
        this.salvarChat();
      },
      complete: () => {
        this.estaCarregando = false; // Desativa o indicador ao completar (sucesso ou erro)
      }
    });
  }

  private salvarChat(): void {
    localStorage.setItem('chatMensagens', JSON.stringify(this.mensagens));
  }

  limpaChat() {
    localStorage.removeItem('chatMensagens');
    this.mensagens = [];
    console.log('🧹 Chat limpo com sucesso');
  }
}