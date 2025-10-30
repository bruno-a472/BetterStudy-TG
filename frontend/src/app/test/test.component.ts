import { Component, ViewChild } from '@angular/core';
import { EstudanteService } from '../estudante.service';
import { ChatComponent } from "../chat/chat.component";
import { EstudantePerfilComponent, PerfilEstudante } from "../estudante-perfil/estudante-perfil.component";

@Component({
  selector: 'app-test',
  imports: [ChatComponent, EstudantePerfilComponent],
  templateUrl: './test.component.html',
  styleUrl: './test.component.scss'
})
export class TestComponent {
  constructor(private estudanteService: EstudanteService) { }

  @ViewChild(ChatComponent) chatComponent!: ChatComponent;
  visualizacao = false;
  perfil: PerfilEstudante = {
    familiaridade_metodos: {
      pomodoro: 1,
      revisao_espacada: 1,
      mapa_mental: 1,
      aprendizado_ativo: 1,
      aprendizado_passivo: 1,
      flashcards: 1
    },
    tipo_aprendiz: 'visual',
    nivel_foco: 'medio',
    horas_estudo_dia: '30min',
    motivacao_estudo: 'Quero me tornar um aprendiz autônomo, capaz de entender como o aprendizado funciona na nossa mente para aumentar ao máximo a eficácia e a eficiência dos meus estudos. Porém, ainda não entendo como nosso cérebro aprende, mesmo que eu estude muito tempo por dia ainda não sinto grandes resultados.',
    atualizadoEm: '"2025-10-30T11:25:15.417Z"'   
  };

  ngOnInit(): void {
    setTimeout(() => {
      this.visualizacao = true;
    }, 100);
      this.estudanteService.defineId(12); 
        const perfilLS = localStorage.getItem('perfil_estudante_v1');
        this.perfil = perfilLS ? JSON.parse(perfilLS) : null;

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
    this.chatComponent.obterRelatorioInicial(this.estudanteService.obtemId(), this.perfil);
  }

}
