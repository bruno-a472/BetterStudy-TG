import { Component, ViewChild } from '@angular/core';
import { EstudanteService } from '../estudante.service';
import { ChatComponent } from "../chat/chat.component";

@Component({
  selector: 'app-test',
  imports: [ChatComponent],
  templateUrl: './test.component.html',
  styleUrl: './test.component.scss'
})
export class TestComponent {
  constructor(private estudanteService: EstudanteService) { }

  @ViewChild(ChatComponent) chatComponent!: ChatComponent;
  visualizacao = false;

  ngOnInit(): void {
    setTimeout(() => {
      this.visualizacao = true;
    }, 100);
      this.estudanteService.defineId(12); 

  } // ngOnInit()

  trocaId() {
    const novoId = (document.getElementsByClassName('login-email')[0] as HTMLInputElement).value;
    const idNumero = parseInt(novoId, 10);
    if (!isNaN(idNumero)) {
      this.estudanteService.defineId(idNumero);
      console.log(`ID do estudante alterado para: ${idNumero}`);
    } else {
      console.error('Por favor, insira um número válido para o ID.');
    }
  } // trocaId()

  checaId() {
    const idAtual = this.estudanteService.obtemId();
    console.log(`ID atual do estudante: ${idAtual}`);
  } // checaId()

  limpaChat() {
    this.chatComponent.limpaChat();
  }

}
