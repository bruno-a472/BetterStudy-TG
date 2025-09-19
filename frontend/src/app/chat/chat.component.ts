import { Component } from '@angular/core';
import { DadosService } from '../dados.service';
import { Mensagem } from '../mensagem';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { EstudanteService } from '../estudante.service';

@Component({
  selector: 'app-chat',
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss'
})
export class ChatComponent {
  mensagens: Mensagem[] = [];
  usuarioInput: string = '';

  constructor(private dadosService: DadosService,
              private estudanteService: EstudanteService
  ) { }

  ngOnInit(): void {
    const mensagensSalvas = localStorage.getItem('chatMensagens');

    const mensagens = mensagensSalvas ? JSON.parse(mensagensSalvas): null;
    if (mensagens && mensagens.length > 0) {
      this.mensagens = mensagens;
    }
  }

  enviarMensagem() {
    if (!this.usuarioInput.trim()) return;

    const userMessage: Mensagem = { 
      chat_id: this.estudanteService.obtemId(), 
      text: this.usuarioInput, 
      remetente: 'usuario', 
      timestamp: new Date() 
    };

    this.mensagens.push(userMessage);
    localStorage.setItem('chatMensagens', JSON.stringify(this.mensagens)); // salva no browser

    this.dadosService.enviarMensagem(userMessage).subscribe(response => {

      const botMessage: Mensagem = { 
        chat_id: this.estudanteService.obtemId(), 
        text: response.text, 
        remetente: 'bot', 
        timestamp: new Date() 
      };

      console.log("Resposta do bot:", response.text);
      this.mensagens.push(botMessage);
      localStorage.setItem('chatMensagens', JSON.stringify(this.mensagens));
      console.log("Mensagens atualizadas:", this.mensagens);
    
    });

    this.usuarioInput = '';
  }

}
